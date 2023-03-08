from kivy.clock import Clock
from urllib.parse import quote

import gl as gl

def findComicBooks(self, option: str):
    siteObj = gl.apcSite
    mainURL = f"{siteObj.mainSite}/page/{gl.currentPage}"
    searchURL = f"https://{siteObj.mainSite.split('/')[2]}/page/{gl.currentPage}/?s={gl.searchText}&post_type=wp-manga"
    tagURL = f"https://{siteObj.name}.com/porncomic-genre/{gl.tag.replace(' ', '-')}/page/{gl.currentPage}"

    match option:
        case "main":
            soup = gl.bs4(mainURL)
            main = soup.findAll("div", {"class": "manga"})
        case "search":
            soup = gl.bs4(searchURL)
            main = soup.findAll("div", {"class": "tab-thumb"})
        case "tags":
            soup = gl.bs4(tagURL)
            main = soup.findAll("div", {"class": "manga"})
    if soup == None:
        siteObj.morePages = False
        gl.csGrid.add_widget(gl.MDLabel(text=f"No more comics on {siteObj.name} found", halign="center"))
        return
    comics = {}
    for div in main:
        link = div.findAll("a")[0]
        txt = link["title"]
        comics.setdefault(txt, [])
        comics[txt].append(link["href"])
        try:
            comics[txt].append(quote(link.find("img")["data-srcset"].split(" ")[0], safe=":/"))
        except:
            comics[txt].append("")
    match option:
        case "main":
            gl.comics = comics
        case "search" | "tags":
            gl.comics.update(comics)
    siteObj.listComicBooks(gl.comics)

def findComicPages(self, link: str, name: str):
    links = {}
    firstLink = ""

    soup = gl.bs4(link)
    for ul in soup.find_all("ul", {"class": "main"}):
        for li in ul.find_all("li"):
            links.setdefault(li.find_all("a")[0]["href"], "")
            firstLink = li.find_all("a")[0]["href"]

    countCh = 1
    for link in links:
        text = link.split("/")[5].replace("-", " ").split()
        output_string = ""
        for word in text:
            if word.isdigit():
                output_string += word + " "
            if word.isalpha():
                break
        if output_string == "":
            links[link] = str(countCh)
        else:
            links[link] = output_string.strip().replace(" ", ".")
        countCh += 1
    try:
        links = sorted(links.items(), key=lambda x: float(x[1]))
    except:
        links = sorted(links.items(), key=lambda x: x[1])
    self.addChapters(links)

    link = firstLink

    images = []
    soup = gl.bs4(link)
    for div in soup.find_all("div", {"class": "reading-content"}):
        for img in div.find_all("img"):
            if img.has_attr("data-src"):
                images.append(quote(img["data-src"].strip(), safe=":/"))
    gl.downloadImages = images
    gl.downloadPath = f"comics/{name}/{link.split('/')[4].replace('-', ' ')}/1/"
    self.listComicPages(images)

def loadChapter(self, chapterLink: str, *args):
    gl.cGrid.clear_widgets()
    gl.carousel.clear_widgets()
    gl.scrollC.scroll_y = 1
    images = []
    soup = gl.bs4(chapterLink)
    for div in soup.find_all("div", {"class": "reading-content"}):
        for img in div.find_all("img"):
            if img.has_attr("data-src"):
                images.append(gl.quote(img["data-src"].strip(), safe=":/"))
    gl.downloadImages = images
    gl.downloadPath = f"comics/{self.name}/{chapterLink.split('/')[4].replace('-', ' ')}/{args[0].text}/"
    self.listComicPages(images)