from kivy.uix.image import AsyncImage
from kivymd.uix.button import MDRectangleFlatButton, MDIconButton
from functools import partial
import json

import gl as gl

class Site():
    def __init__(self, name, mainSite, tagSite, color):
        self.name = name
        self.mainSite = mainSite
        self.tagSite = tagSite
        self.color = color
        self.morePages = True

        gl.colors.setdefault(name, color)

        gl.nav_drawer.children[0].add_widget(gl.DrawerClickableItem(text=name, text_color=color, on_release=partial(self.toSiteComicsScreen, "main")))

    def addChapters(self, links, *args):
        for link in links:
            gl.chapterBox.add_widget(MDRectangleFlatButton(text=link[1], on_release=partial(self.loadChapter, self, link[0])))
        gl.chapterBox.bind(minimum_width=gl.chapterBox.setter("width"))

    def addFav(star, title: str, link: str, img: str, *args):
        if star.icon == "star-outline":
            gl.favs.setdefault(title, [])
            gl.favs[title].append(link)
            gl.favs[title].append(img)
            gl.favs[title].append("apc")
        else:
            gl.favs.pop(title)
        gl.favs = dict(sorted(gl.favs.items()))
        with open("favs.json", "w") as f:
            gl.json.dump(gl.favs, f)
        setattr(star, "icon", "star" if star.icon == "star-outline" else "star-outline")

    def listComicBooks(self, comicBooks: dict):
        if self.name == "":
            color = (0, 0, 0, 0)
        else:
            color = gl.colors[self.name]
        if comicBooks == {}:
            gl.csGrid.add_widget(gl.MDLabel(text=f"Nothing to show", halign="center"))
        for title in comicBooks:
            smartTile = gl.MDSmartTileButton(source=comicBooks[title][1], on_release=partial(self.toSiteComicScreen, title)) # 

            star = MDIconButton(icon="star-outline", theme_icon_color="Custom", icon_color=(1, 1, 0, 1), pos_hint={"center_y": .5})
            star.bind(on_release=partial(self.addFav, star, title, comicBooks[title][0], comicBooks[title][1]))
            setattr(star, "icon", "star" if title in gl.favs else "star-outline")
            smartTile.add_widget(star)

            smartTile.add_widget(gl.MDLabel(text=title))

            outline = gl.MDBoxLayout(padding="2dp", md_bg_color=color, radius=10)
            outline.add_widget(smartTile)
            gl.csGrid.add_widget(outline)
        gl.csGrid.bind(minimum_height=gl.csGrid.setter("height"))

    def listComicPages(self, pages: list):
        for i, page in enumerate(pages):
            gl.cGrid.add_widget(gl.ImageButton(source=page, on_release=partial(self.openPopup, i))) # 
            gl.carousel.add_widget(AsyncImage(source=page, allow_stretch=True)) # 
        gl.cGrid.bind(minimum_height=gl.cGrid.setter("height"))
    
    def openPopup(self, slide: int, *args):
        gl.carousel.load_slide(gl.carousel.slides[slide])
        gl.carouselLbl.text = f" {gl.carousel.index + 1}/{len(gl.carousel.slides)}"
        gl.popup.open()

    def toSiteComicsScreen(self, option: str, *args):
        gl.goToScreen("comic")
        self.findComicBooks(self, option)
        match option:
            case "main":
                gl.topAppBar.title = self.name
            case "search":
                gl.topAppBar.title = f"{gl.searchText} - Page {gl.currentPage}"
            case "tags":
                pass

    def toSiteComicScreen(self, title: str, *args):
        gl.currentComicSite = self.mainSite
        gl.goToScreen("comic", True)
        self.findComicPages(self, gl.comics[title][0], self.name)
        gl.topAppBar.title = title