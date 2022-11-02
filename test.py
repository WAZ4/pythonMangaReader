import requests
import json

base_url = "https://api.mangadex.org"


def getMangaFeed(mangaID, offset=0):
    global base_url
    url = base_url + "/manga/" + mangaID + "/feed"
    params = {
        "limit": 500,
        "offset": offset,
        "translatedLanguage[]": ["en"],
        "order[chapter]": "asc"
    }
    r = requests.get(url, params=params)
    if r.status_code != 200:
        print("Request status code: ", r.status_code)
        print(r.url)
        return
    r_json = r.json()["data"]
    if r.json()["limit"] + r.json()["offset"] < r.json()["total"]:
        r_json += getMangaFeed(mangaID, r.json()["limit"]+r.json()["offset"])
    return r_json



mangaFeed = getMangaFeed("746e02b6-c71d-43a4-9783-0143962a9d0c")
# print(mangaFeed)

chapterID = "61ed0f14-f41a-4dbd-b33e-eba36c767d80"
relativeChapter = {
        "previous": None,
        "current": chapterID,
        "next": None
    }

for index, chapter in enumerate(mangaFeed):
    if chapter["id"] == chapterID:
        if index-1 > 0:
            relativeChapter["previous"] = mangaFeed[index-1]["id"]
        if index +1 < len(mangaFeed):
            relativeChapter["next"] = mangaFeed[index+1]["id"]
        break

print(relativeChapter)


