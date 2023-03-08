from urllib.parse import quote

import gl as gl

def findComicBooks(self, option: str):
    siteObj = gl.bpcSite
    mainURL = f"{siteObj.mainSite}/page/{gl.currentPage}"
    searchURL = f"https://{siteObj.mainSite.split('/')[2]}/page/{gl.currentPage}/?s={gl.searchText}"
    tagURL = f"{siteObj.tagSite}/gallery/tag/{gl.tag.replace(' ', '-')}/page/{gl.currentPage}"

    match option:
        case "main":
            soup = gl.bs4(mainURL)
        case "search":
            soup = gl.bs4(searchURL)
        case "tags":
            soup = gl.bs4(tagURL)
    if soup == None:
        siteObj.morePages = False
        gl.csGrid.add_widget(gl.MDLabel(text=f"No more comics on {siteObj.name} found", halign="center"))
        return
    comics = {}
    for link in soup.find_all("a"):
        if link.has_attr("title") and link.has_attr("class"):
            for img in link.find_all("img", {"class": "size-bimber-grid-standard"}):
                txt = link["title"]
                comics.setdefault(txt, [])
                comics[txt].append(link["href"])
                comics[txt].append(quote(img["src"], safe=":/"))
            for img in link.find_all("img", {"class": "size-bimber-list-standard"}):
                txt = link["title"]
                comics.setdefault(txt, [])
                comics[txt].append(link["href"])
                comics[txt].append(quote(img["src"], safe=":/"))
    match option:
        case "main":
            gl.comics = comics
        case "search" | "tags":
            gl.comics.update(comics)
    siteObj.listComicBooks(gl.comics)

def findComicPages(self, link: str, name: str):
    images = []
    soup = gl.bs4(link)
    for linkImg in soup.find_all("a"):
        if linkImg.has_attr("class") or linkImg.has_attr("title"):
            pass
        else:
            for img in linkImg.find_all("img"):
                images.append(linkImg["href"])
    gl.downloadImages = images
    gl.downloadPath = f"comics/{name}/{link.split('/')[4].replace('-', ' ')}/"
    self.listComicPages(images)