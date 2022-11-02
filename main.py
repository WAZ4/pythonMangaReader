from flask import Flask, render_template, request
import requests
import json

# MangaDexAPI verion 5.7.5

base_url = "https://api.mangadex.org"
app = Flask(__name__)

def getMangaList(parameters={}):
    global base_url
    url = base_url + "/manga"
    r = requests.get(url, params=parameters)
    if r.status_code == 200:
        r = r.json()
        res = []
        for data in r["data"]:
            mangaInfo = {
                "id": data["id"],
                "title": data["attributes"]["title"]["en"], #potential breaking point assuming that the language will en will always be available
                "coverUrl": "../temp/thumbnail512.jpg",
            }
            for relationship in data["relationships"]:
                if relationship["type"] == "cover_art":
                    mangaInfo["coverUrl"] = getMangaCover(data["id"], relationship["id"])
                    break
            res.append(mangaInfo)
        return res
    else: #extremely redundat else but I think its more readable for someone who dosent know whats going ons
        return False


def getMangaCover(mangaID, coverID):
    global base_url
    url = base_url + "/cover"
    r = requests.get(url, params={"ids[]": [coverID]})

    if r.status_code == 200:
        filename = r.json()["data"][0]["attributes"]["fileName"]
        return f"https://uploads.mangadex.org/covers/{mangaID}/{filename}.512.jpg"
    return False

@app.route("/", methods=["GET"])
def mainPage():
    mangaQueryParams = {
        "availableTranslatedLanguage[]": ["en"],
    }
    paramList = request.args.to_dict(flat=True)
    if "searchText" in paramList and paramList["searchText"].strip() != "":
        mangaQueryParams["title"] = paramList["searchText"]
    return render_template("index.html", mangaList = getMangaList(mangaQueryParams))

def getAuthor(authorID):
    global base_url
    url = base_url + "/author"
    r = requests.get(url, params={"ids[]": [authorID]})
    if r.status_code != 200:
        return

    r = r.json()["data"]
    return r

def getManga(mangaID):
    global base_url
    url = base_url + "/manga/" + mangaID
    r = requests.get(url)
    if r.status_code != 200:
        return

    r = r.json()["data"]
    mangaInfo = {
        "id": r["id"],
        "titleEn": r["attributes"]["title"]["en"],
        "authorMame": "",
        "authorID": "",
        "coverUrl": "",
        "lastChapter": r["attributes"]["lastChapter"],
        "status": r["attributes"]["status"].title(),
        "description": r["attributes"]["description"]["en"],
        "malID": False,
        "genres": [],
        "themes": []
    }
    for relationship in r["relationships"]:
        if relationship["type"] == "author":
            mangaInfo["authorID"] = relationship["id"]
            mangaInfo["authorName"] = getAuthor(relationship["id"])[0]["attributes"]["name"]
            break

    if "mal" in r["attributes"]["links"]:
        mangaInfo["malID"] = r["attributes"]["links"]["mal"]

    for tag in r["attributes"]["tags"]:
        if tag["attributes"]["group"] == "genre":
            mangaInfo["genres"].append(tag)
        elif tag["attributes"]["group"] == "theme":
            mangaInfo["themes"].append(tag)

    for relationship in r["relationships"]:
        if relationship["type"] == "cover_art":
            mangaInfo["coverUrl"] = getMangaCover(mangaID, relationship["id"])
            break

    return mangaInfo

@app.route("/manga/<mangaID>")
def manga(mangaID):
    mangaInfo = getManga(mangaID)
    return render_template("manga.html", mangaInfo = mangaInfo)

if __name__ == '__main__':
    app.run()


#TODO: -get chapter list on manga.html
#      -actually be able to read manga
