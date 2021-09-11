import requests
import json
import random
import time
import os
import re
from bs4 import BeautifulSoup


headers = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36 OPR/78.0.4093.184"
}


def get_author_id(author, headers):
    """Find 'top result' author id in Genius search"""

    url = f"https://genius.com/api/search/multi?per_page=5&q={author.replace(' ', '%20')}"
    response = requests.get(url, headers)
    data = response.json()
    
    if data["response"]["sections"][3]["type"] != "artist":
        raise ValueError("Can`t find an artist")    

    return data["response"]["sections"][3]["hits"][0]["result"]["id"]


def get_data_file(author_id, headers):
    """Collect data and return JSON"""
    
    all_songs = {}
    page = 1
    print("[INFO] Start collecting pages of songs")
    while True:
        url = f"https://genius.com/api/artists/{author_id}/songs?page={page}&sort=popularity"

        response = requests.get(url, headers)
        data = response.json()

        for song in data["response"]["songs"]:
            all_songs[song["title"]] = song["url"]

        print(f"[+] Page {page} collected")
        if data["response"]["next_page"] is None:
            break
        else:
            page += 1
    
    print("[INFO] Songs collected")
    with open(f"songs.json", "w", encoding="utf-8") as file:
        json.dump(all_songs, file, indent=4, ensure_ascii=False)


def get_song_text(headers):
    """Iterate trough songs and collect text"""
    
    with open("songs.json", encoding="utf-8") as file:
        all_songs = json.load(file)
    
    count = 1
    print("[INFO] Start collecting lyrics")
    for title, url in all_songs.items():
        rep = [" ", ".", ",", "<", ">", ":", "\"", "\'", "\\", "/", "|", "?", "*", "+", "%", "!", "@"]
        for symbol in rep:
            if symbol in title:
                title = title.replace(symbol, "_")
        
        response = requests.get(url)
        src = response.text.replace("<br/>", "\n")

        soup = BeautifulSoup(src, "lxml")
        div = soup.find(class_=re.compile("^lyrics$|Lyrics__Root"))
        if div is None:
            print("[INFO] 1 song with no lyrics skipped")
            continue
        text = div.text.strip().replace("EmbedShare URLCopyEmbedCopy", "")

        with open(f"{count}_{title}.txt", "w", encoding="utf-8") as file:
            file.write(text)
        
        print(f"[+] Lyrics of song {count} collected")
        count += 1
    print("[INFO] Lyrics collected")


def main():
    author = input().strip().lower()
    author_dir = author.replace(" ", "_")

    if "data" not in os.listdir():
        os.mkdir("data")
    if author_dir not in os.listdir("data/"):
        os.mkdir(f"data/{author_dir}")
    os.chdir(f"data/{author_dir}")

    author_id = get_author_id(author, headers)
    get_data_file(author_id, headers)
    get_song_text(headers) 


if __name__ == "__main__":
    main()