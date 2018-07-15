#pip install bs4
#pip install lxml
#pip install html5lib

from bs4 import BeautifulSoup
from urllib.request import urlopen
import csv
from PyQt5.QtCore import *

class Abitur ():
    def __init__(self, name):
        self.high_schools = {}
        self.name = name

    def addSchool(self, schoolName, directName, konkurs):
        tmp = (directName, str(konkurs))
        if self.high_schools.get(schoolName) == None:
            self.high_schools[schoolName] = []
        self.high_schools[schoolName].append(tmp)

    def checkBVI(self):
        for sch in self.high_schools:
            for dir in self.high_schools[sch]:
                if 'БВИ' in dir:
                    return True
        return False

    # def __str__(self):
    #     return self.name + ' ' + self.high_schools.__str__()
    def __str__(self):
        return self.high_schools.__str__()


class Parser (QObject):
    mySign = pyqtSignal(int)
    def __init__(self):
        super(Parser, self).__init__()
        self.main_url = 'http://admlist.ru/'
        self.high_schools_urls = []  # ссылки на вузы
        self.high_schools_directions = {}  # словарь название вуза : ссылки на направления
        # self.abitur_high_school = {}  # словарь абитур : вузы
        self.name_abitur = {}  # словарь имя: абитур (внутри вуз: все направления)
        self.directCount = 0
        self.updatedCount = 0

    def clear(self):
        self.high_schools_urls = []
        self.high_schools_directions = {}
        self.name_abitur = {}
        self.directCount = 0
        self.updatedCount = 0

    def fetch_hight_schools_urls(self): #берет все ссылки на вузы
        html_doc = urlopen(self.main_url).read()
        soup = BeautifulSoup(html_doc, "lxml")
        for link in soup.find_all('a'):
            high_school = link.get('href')
            if 'vk' in high_school:
                pass
            else:
                high_school_url = self.main_url + high_school
                self.high_schools_urls.append(high_school_url)


    def fetch_directions_urls(self): #берет все ссылки на направления для каждого вуза
        for high_school_url in self.high_schools_urls:
            directions = []
            html_doc = urlopen(high_school_url).read()
            soup = BeautifulSoup(html_doc, "lxml")
            name = soup.h1.string  # название вуза
            for link in soup.find_all('a'):
                direction = link.get('href')
                if 'index' in direction:
                    pass
                else:
                    self.directCount += 1
                    direction_url = high_school_url[0:high_school_url.find('index')] + direction  # ссылка на направление
                    directions.append(direction_url)
            self.high_schools_directions[name] = directions


    #для всех вузов из списка names извлекает список абитуров и пишет их в словарь
    #по дефолту берет все вузы
    def fetchAbitsToHighSchools (self, names = []):
        if len(names) == 0:
            names = self.high_schools_directions
        self.directCount = 0
        for high_school_name in names:
            directions = self.high_schools_directions[high_school_name]
            self.directCount += len(directions)
        for high_school_name in names:
            directions = self.high_schools_directions[high_school_name]
            for direct_url in directions:
                html_doc = urlopen(direct_url).read()
                soup = BeautifulSoup(html_doc, "lxml")
                directName = soup.h2.contents[1].split(',')
                directName = directName[len(directName)-1] #название направления
                for tr in soup.find_all('tr'):
                    test = tr.find_all('td')
                    if len(test) > 5:
                        konkurs = test[5].contents[0] #ОК БВИ
                        if len(test[3].contents) == 0:
                            continue
                        abitur = test[3].contents[0]
                        try:
                            abitur = int(abitur)
                        except:
                            if self.name_abitur.get(abitur) == None:
                                tmpAbitur = Abitur(abitur)
                                self.name_abitur[abitur] = tmpAbitur
                            self.name_abitur[abitur].addSchool(high_school_name, directName, konkurs)
                            # if self.abitur_high_school.get(abitur) == None:
                            #     self.abitur_high_school[abitur] = []
                            # if high_school_name in self.abitur_high_school[abitur]:
                            #     pass
                            # else:
                            #     self.abitur_high_school[abitur].append(high_school_name)
                self.updatedCount += 1
                self.mySign.emit((float(self.updatedCount)/float(self.directCount))*100)



    #записывает словарь с абитурами в файл CSV
    def save(self, path):
        data = self.name_abitur
        with open(path, 'w', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(('Абитур', 'Вузы'))
            for abit in data:
                writer.writerow((abit, data[abit]))


    # собирает все функции вместе
    def pars(self, names = []):
        self.clear()
        self.fetch_hight_schools_urls()
        self.fetch_directions_urls()
        self.fetchAbitsToHighSchools(names)


    def parsAndSave(self, path, names = []):
        self.pars(names)
        self.save(path)


    def findAbitur(self, name):
        querset = []
        if self.name_abitur.get(name) != None:
            querset.append(self.name_abitur[name])
        else:
            name = name.lower()
            for abitName in self.name_abitur:
                if name in abitName.lower():
                    querset.append(self.name_abitur[abitName])
        return querset


