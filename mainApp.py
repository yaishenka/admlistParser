import sys  # sys нужен для передачи argv в QApplication
from PyQt5 import QtWidgets
from PyQt5 import QtGui
import design
from parser import Parser

class ExampleApp(QtWidgets.QMainWindow, design.Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.parser = Parser()
        self.lineEdit.setText('WAIT')
        # self.parser.pars(['ВШЭ'])
        self.lineEdit.setText('GO')
        self.okButton.clicked.connect(self.findAbitur)


    def findAbitur(self):
        if self.lineEdit.text() == '':
            pass
        else:
            abits = self.parser.findAbitur(self.lineEdit.text())
            if len(abits) == 0:
                pass
            else:
                for abit in abits:
                    string = abit.name + abit.__str__
                    item = QtGui.QStandardItem (string)
                    print (string)
                    self.listView.model().appendRow(item)


def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = ExampleApp()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение

if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()