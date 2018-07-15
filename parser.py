#pip install bs4
#pip install lxml
#pip install html5lib

from bs4 import BeautifulSoup
from urllib.request import urlopen
import csv
import sys

class Parser ():
    main_url = 'http://admlist.ru/'
    high_schools_urls = []  # ссылки на вузы
    high_schools_directions = {}  # словарь название вуза : ссылки на направления
    abitur_high_school = {}  # словарь абитур : вузы


    def fetch_hight_schools_urls(self): #берет все ссылки на вузы
        html_doc = urlopen(self.main_url).read()
        soup = BeautifulSoup(html_doc)
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
            soup = BeautifulSoup(html_doc)
            name = soup.h1.string  # название вуза
            for link in soup.find_all('a'):
                direction = link.get('href')
                if 'index' in direction:
                    pass
                else:
                    direction_url = high_school_url[0:high_school_url.find('index')] + direction  # ссылка на направление
                    directions.append(direction_url)
            self.high_schools_directions[name] = directions


    #для всех вузов из списка names извлекает список абитуров и пишет их в словарь
    #по дефолту берет все вузы
    def fetchAbitsToHighSchools (self, names = []):
        if len(names) == 0:
            names = self.high_schools_directions
        for high_school_name in names:
            directions = self.high_schools_directions[high_school_name]
            print(high_school_name)
            for direct_url in directions:
                html_doc = urlopen(direct_url).read()
                soup = BeautifulSoup(html_doc, "lxml")
                print(soup.h2.contents[1])
                for tr in soup.find_all('tr'):
                    test = tr.find_all('td')
                    if len(test) > 3:
                        abitur = test[3].contents[0]
                        try:
                            abitur = int(abitur)
                        except:
                            if self.abitur_high_school.get(abitur) == None:
                                self.abitur_high_school[abitur] = []
                            if high_school_name in self.abitur_high_school[abitur]:
                                pass
                            else:
                                self.abitur_high_school[abitur].append(high_school_name)


    #записывает словарь с абитурами в файл CSV
    def save(self, path):
        data = self.abitur_high_school
        with open(path, 'w', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(('Абитур', 'Вузы'))
            for abit in data:
                writer.writerow((abit, data[abit]))


    # собирает все функции вместе
    def pars(self, names = []):
        self.fetch_hight_schools_urls()
        self.fetch_directions_urls()
        self.fetchAbitsToHighSchools(names)


    def parsAndSave(self, path, names = []):
        self.pars(names)
        self.save(path)


    def findAbitur(self, name):
        if self.abitur_high_school.get(name) != None:
            return self.abitur_high_school[name]
        else:
            for abitName in self.abitur_high_school:
                if name in abitName:
                    return self.abitur_high_school[abitName]
        return "Абитур не найден"


parser = Parser()
# parser.parsAndSave('abiturs.csv', ['ВШЭ'])
# parser.pars(['ВШЭ'])
parser.pars()
print (parser.findAbitur('Галынская Арина Михайловна'))
print (parser.findAbitur('Галынская'))