from lxml import html
from pymongo import MongoClient
import requests
import settings

def initDatabase():
    mongo_uri = 'mongodb://{}:{}'.format(settings.MONGO_HOST, settings.MONGO_PORT)
    client = MongoClient(mongo_uri)
    return client[settings.MONGO_DB]


def searchUrl(url):
    request = requests.get(url)
    targetWords = [["facebook"],["twitter"],["covid", "coronavirus"]]
    ignoreWords = [[], ["/intent/", "/status/"], ["donate","donation","give","join"]]
    entry = { 'url': url }
    for target, ignore in zip(targetWords, ignoreWords):
        entry[target[0]] = scrape(request, target, ignore)
    return entry


def scrape(request, target, ignore):
    root = html.fromstring(request.content)
    entries = []
    for targetWord in target:
        targetString = "[contains(@href, '{}')]".format(targetWord)
        ignoreString = ""
        for ignoreText in ignore:
            ignoreString += "[not(contains(@href, '{}'))]".format(ignoreText)
        matches = root.xpath("//a{}{}/@href".format(targetString, ignoreString))
        lower = [link.lower() for link in matches]
        noRelative = []
        for link in lower:
            linkText = link
            if linkText.startswith("/"):
                if request.url.endswith("/"):
                    linkText = request.url + linkText[1:]
                else:
                    linkText = request.url + linkText
            noRelative.append(linkText.strip())
        entries.extend(noRelative)
    noDups = list(set(entries))
    return noDups

def writeToConsole(entry):
    print(entry)

def writeToMongo(db, entry):
    db.hospitals.insert_one(entry)

def main():
    db = initDatabase()
    urlList = ["https://jacksonhealth.org/jackson-memorial/","https://www.mayoclinichealthsystem.org/","https://www.hennepinhealthcare.org/","https://www.mgmc.org/","https://www.nyp.org/"]
    for url in urlList:
        entry = searchUrl(url)
        #writeToConsole(entry)
        writeToMongo(db, entry)
        

if __name__ == "__main__":
    main()