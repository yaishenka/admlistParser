import sys  # sys нужен для передачи argv в QApplication
from PyQt5  import QtWidgets
from PyQt5.QtCore import *
from PyQt5  import QtGui

import design
from MyParser import Abitur
from MyParser import Parser
import webbrowser
from subprocess import call


class Thread(QThread):
    mySignal = pyqtSignal()

    def __init__(self, parser):
        QThread.__init__(self)
        self.parser = parser
        self.names =[]

    def __del__(self):
        self.wait()

    def run(self):
        self.parser.pars(self.names)
        self.mySignal.emit()


class ExampleApp(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.label.setText('made by yaishenka <a href="http://github.com/yaishenka">github.com/yaishenka</a>')
        self.label.linkActivated.connect(self.link)
        p = QtGui.QPalette()
        self.mainColor = QtGui.QColor(255, 102, 0)
        p.setBrush(QtGui.QPalette.Window, QtGui.QBrush(self.mainColor))
        self.setPalette(p)
        self.setIconSize(QSize(24,24))
        self.setWindowIcon(QtGui.QIcon('icon.ico'))
        self.parser = Parser()
        self.okButton.clicked.connect(self.findAbitur)
        self.myReloadButton.clicked.connect(self.pars)
        self.allChecked.clicked.connect(self.setAllChecked)
        self.allUnchecked.clicked.connect(self.setAllUnchecked)
        self.saveButton.clicked.connect(self.save)
        self.thread = Thread(self.parser)
        self.thread.mySignal.connect(self.activeMode)
        self.parser.mySign.connect(self.updateProgressBar)
        self.progressBar.setVisible(False)
        self.updListSchools()

    def pars(self):
        self.waitMode()
        names = []
        model = self.listView.model()
        for index in range(model.rowCount()):
            item = model.item(index)
            if item.checkState() == Qt.Checked:
                names.append(item.text())
        self.thread.names = names
        self.thread.start()

    def save(self):
        if len(self.parser.name_abitur) == 0:
            self.listWidget.addItem('Обновите базу!')
            return
        self.parser.save('base.csv')

    def updListSchools(self):
        model = QtGui.QStandardItemModel()
        self.parser.fetch_hight_schools_urls()
        self.parser.fetch_directions_urls()
        self.checkboxes = []
        names = self.parser.high_schools_directions
        for i,name in enumerate(names):
            item = QtGui.QStandardItem(name)
            check = Qt.Checked
            item.setCheckState(check)
            item.setCheckable(True)
            item.setBackground(self.mainColor)
            model.appendRow(item)
        self.listView.setModel(model)
        self.listView.show()

    def setAllChecked(self):
        model = self.listView.model()
        for index in range(model.rowCount()):
            item = model.item(index)
            if item.isCheckable() and item.checkState() == Qt.Unchecked:
                item.setCheckState(Qt.Checked)

    def setAllUnchecked(self):
        model = self.listView.model()
        for index in range(model.rowCount()):
            item = model.item(index)
            if item.isCheckable() and item.checkState() == Qt.Checked:
                item.setCheckState(Qt.Unchecked)


    def updateProgressBar(self, val):
        self.progressBar.setValue(val)

    def waitMode(self):
        self.listWidget.clear()
        self.lineEdit.setText('WAIT')
        self.okButton.setEnabled(False)
        self.lineEdit.setEnabled(False)
        self.myReloadButton.setEnabled(False)
        self.checkBox.setEnabled(False)
        self.saveButton.setEnabled(False)
        self.progressBar.setValue(0)
        self.progressBar.setVisible(True)

    def activeMode(self):
        self.listWidget.clear()
        self.lineEdit.setText('')
        self.okButton.setEnabled(True)
        self.lineEdit.setEnabled(True)
        self.checkBox.setEnabled(True)
        self.saveButton.setEnabled(True)
        self.myReloadButton.setEnabled(True)
        self.progressBar.setVisible(False)

    def findAbitur(self):
        if len(self.parser.name_abitur) == 0:
            self.listWidget.addItem('Обновите базу!')
            return
        if self.lineEdit.text() == '':
            return
        else:
            self.listWidget.clear()
            abits = self.parser.findAbitur(self.lineEdit.text())
            if len(abits) == 0:
                self.listWidget.addItem('Абитур не найден :(')
                return
            else:
                for abit in abits:
                    if self.checkBox.isChecked() and not abit.checkBVI():
                        continue
                    self.listWidget.addItem(abit.name)
                    for school in abit.high_schools:
                        directList = abit.high_schools[school]
                        for direct in directList:
                            string = school + ' '
                            if direct[1] != 'БВИ':
                                if not self.checkBox.isChecked():
                                    string += direct[0] + ' ' + direct[1] + ' '
                            else:
                                string += direct[0] + ' ' + direct[1] + ' '
                            if string != school + ' ':
                                self.listWidget.addItem(string)

    def link(self, linkStr):
        QtGui.QDesktopServices.openUrl(QUrl(linkStr))


def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = ExampleApp()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение


if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()
