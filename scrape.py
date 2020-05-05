from lxml import html
import requests

def searchUrl(url):
    request = requests.get(url)
    targetWords = [["facebook"],["twitter"],["covid", "coronavirus"]]
    ignoreWords = [[], ["/intent/", "/status/"], ["donate","donation","give","join"]]
    #ignoreWords = [[], ["/intent/", "/status/"], []]
    entry = ""
    entry += "{}".format(url)
    for target, ignore in zip(targetWords, ignoreWords):
        entry += ",{}".format(scrape(request, target, ignore))
    print(entry)


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
    ret = "|".join(noDups)
    if not ret:
        ret += "(no {})".format(target[0])
    return ret

def main():
    urlList = ["https://jacksonhealth.org/jackson-memorial/","https://www.mayoclinichealthsystem.org/","https://www.hennepinhealthcare.org/","https://www.mgmc.org/","https://www.nyp.org/"]
    #urlList = ["https://www.mayoclinichealthsystem.org/"]
    for url in urlList:
        searchUrl(url)

if __name__ == "__main__":
    main()