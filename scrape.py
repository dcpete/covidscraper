from lxml import html
from pymongo import MongoClient
import requests
import settings

urlList = [
    "https://jacksonhealth.org/jackson-memorial/",
    "https://www.mayoclinichealthsystem.org/",
    "https://www.hennepinhealthcare.org/",
    "https://www.mgmc.org/",
    "https://www.nyp.org/"
]
# targetWords is a list of lists, each sublist containing words to scrape
# lists containing more than one word are searches using OR
targetWords = [["facebook"],["twitter"],["covid", "coronavirus"]]
# ignoreWords is a list of lists, one for each list of lists in targetWords
# urls matched by targetWords are ignored if they contain any in ignoreWords
ignoreWords = [[], ["/intent/", "/status/"], ["donate","donation","give","join"]]


def initDatabase():
    # initialize or establish connection to database
    mongo_uri = 'mongodb://{}:{}'.format(settings.MONGO_HOST, settings.MONGO_PORT)
    client = MongoClient(mongo_uri)
    return client[settings.MONGO_DB]


def searchUrl(url):
    # do a search on one url
    request = requests.get(url)
    # entry is a dict for this url that will eventually be added to mongodb
    # start by adding the search url
    entry = { 'url': url }
    # for each pair of targetWords/ignoreWords
    for target, ignore in zip(targetWords, ignoreWords):
        # add all matching links to entry using the first targetWord as a key 
        entry[target[0]] = scrape(request, target, ignore)
    return entry


def scrape(request, target, ignore):
    # get the document from the url and parse it
    root = html.fromstring(request.content)
    # we will loop the search over each targetWord because I couldn't find how
    # to do an OR search with lxml.html.xpath
    # links is the list that will contain the links for all searches
    links = []
    for targetWord in target:
        # add this to xpath search for targetWord
        targetString = "[contains(@href, '{}')]".format(targetWord)
        ignoreString = ""
        # add a not(contains()) clause for each word in the ignore list
        for ignoreText in ignore:
            ignoreString += "[not(contains(@href, '{}'))]".format(ignoreText)
        matches = root.xpath("//a{}{}/@href".format(targetString, ignoreString))
        # make all urls lowercase
        lower = [link.lower() for link in matches]
        # some links are relative, so prepend the base url if it is
        noRelative = []
        for link in lower:
            linkText = link
            if linkText.startswith("/"):
                if request.url.endswith("/"):
                    linkText = request.url + linkText[1:]
                else:
                    linkText = request.url + linkText
            noRelative.append(linkText.strip())
        # add the list for this targetWord to the links list
        links.extend(noRelative)
    # make sure there are no duplicate links in the list
    noDups = list(set(links))
    return noDups


def writeToConsole(entry):
    print(entry)


def writeToMongo(db, entry):
    db.hospitals.insert_one(entry)


def writeToFile(entries):
    with open("output.csv", "w") as f:
        targetHeaders = []
        for wordList in targetWords:
            targetHeaders.append(wordList[0])
        headers = ",".join(targetHeaders) + "\n"
        f.write('url,')
        f.write(headers)
        for entry in entries:
            f.write(entry.get('url') + ",")
            rowList = []
            for header in targetHeaders:
                urlList = entry.get(header).copy()
                joinedList = "|".join(urlList)
                rowList.append(joinedList)
            row = ",".join(rowList) + "\n"
            f.write(row)


def main():
    # program starts here
    db = initDatabase()
    entries = []
    for url in urlList:
        entry = searchUrl(url)
        #writeToConsole(entry)
        entries.append(entry)
        writeToMongo(db, entry)
    writeToFile(entries)

        

if __name__ == "__main__":
    main()