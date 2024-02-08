import requests
from bs4 import BeautifulSoup
import urllib.parse
from pathlib import Path
import os 
dir_path = os.path.dirname(os.path.realpath(__file__))

    
def get_last_url_part(url: str):
    url_path = Path(urllib.parse.urlparse(url).path)
    return url_path.name


def wiki_to_txt(_infile) -> None:
    with open("wikipedialist.csv") as infile:
        wikiurls = infile.read().split("\n")

    for url in wikiurls:
        if len(url) > 0:
            response = requests.get(url=url)
            soup = BeautifulSoup(response.content, 'html.parser')
            outfile = get_last_url_part(url) + ".txt"
            with open(os.path.join(dir_path, "textfiles", outfile), "w") as of:
                of.write(soup.get_text())


if __name__ == "__main__":
    print(get_last_url_part("https://thewalrus.ca/the-ethnic-vote-is-a-myth"))
    wiki_to_txt(os.path.join(dir_path, "wikipedialist.csv"))
