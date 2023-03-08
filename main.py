from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.filemanager import MDFileManager
from kivy.core.window import Window
from kivy.properties import ObjectProperty
from kivy.utils import platform
from plyer import storagepath
from urllib.parse import quote
import json
import os

import comic_sites.apc as apc
import comic_sites.bpc as bpc
import gl as gl
import site_template as st


# permissions (android)

if platform == "android":
    from android.permissions import request_permissions, Permission
    from plyer import orientation
    request_permissions([
        Permission.WRITE_EXTERNAL_STORAGE,
        Permission.READ_EXTERNAL_STORAGE,
        Permission.INTERNET
    ])


#   app

class GroundLayout(MDBoxLayout):
    carousel = ObjectProperty()
    carouselLbl = ObjectProperty()
    cGrid = ObjectProperty()
    chapterBox = ObjectProperty()
    csGrid = ObjectProperty()
    flButton = ObjectProperty()
    hideComicsSection = ObjectProperty()
    hideComicSection = ObjectProperty()
    nav_drawer = ObjectProperty()
    popup = ObjectProperty()
    scrollC = ObjectProperty()
    scrollCs = ObjectProperty()
    sm = ObjectProperty()
    topAppBar = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # make obkects global available
        gl.carousel = self.carousel
        gl.carouselLbl = self.carouselLbl
        gl.cGrid = self.cGrid
        gl.chapterBox = self.chapterBox
        gl.csGrid = self.csGrid
        gl.hideComicsSection = self.hideComicsSection
        gl.hideComicSection = self.hideComicSection
        gl.nav_drawer = self.nav_drawer
        gl.popup = self.popup
        gl.scrollC = self.scrollC
        gl.scrollCs = self.scrollCs
        gl.sm = self.sm
        gl.topAppBar = self.topAppBar

        # hide lock rotation button on windows
        if platform == "win":
            gl.hide_widget(self.flButton)

        # add sites
        apcSite = st.Site("allporncomic", "https://allporncomic.com/home-3/", "https://allporncomic.com/genres/", (1, 0.2, 1, 1))
        bpcSite = st.Site("bestporncomix", "https://bestporncomix.com/multporn-net/", "https://bestporncomix.com/", (1, 0.2, 0.2, 1))
        gl.apcSite = apcSite
        gl.bpcSite = bpcSite
        setattr(apcSite, "findComicBooks", apc.findComicBooks)
        setattr(apcSite, "findComicPages", apc.findComicPages)
        setattr(apcSite, "loadChapter", apc.loadChapter)
        setattr(bpcSite, "findComicBooks", bpc.findComicBooks)
        setattr(bpcSite, "findComicPages", bpc.findComicPages)

        # load favorites from file if it exists
        if os.path.isfile("favs.json") and os.path.getsize("favs.json") != 0:
            with open("favs.json", "r") as f:
                gl.favs = json.load(f)

        # makes the choosable comic site checkboxes scrollable
        self.ids.searchCheckBoxes.bind(minimum_width=self.ids.searchCheckBoxes.setter("width"))

        # file manager for choosing the comic download location
        self.filemanager = MDFileManager(exit_manager=self.fileManagerExit, select_path=self.fileManagerSelectPath)

        # sets the default comic download location to the documents directory
        gl.downloadLocation = storagepath.get_documents_dir()

        # binds a keyboard press to the given function
        Window.bind(on_keyboard=self.androidBackClick)
        
    # goes back if the android back button is pressed
    def androidBackClick(self, window, key, *args):
        if key == 27:
            gl.goBack(gl.gtp)

    # closes the file manager
    def fileManagerExit(self):
        self.filemanager.close()

    # opens the file manager at the documents directory
    def fileManagerOpen(self):
        self.filemanager.show(storagepath.get_documents_dir())

    def fileManagerSelectPath(self, path: str):
        gl.downloadLocation = path
        print(gl.downloadLocation)
        self.fileManagerExit()

    # reroutes the goToScreen function because it can't be accessed from the cg.kv file
    def goToScreen(self, screen: str):
        gl.goToScreen(screen)

    # manual locks the screen rotation on android (because kivy isn't using the auto rotation lock)
    def lockRotation(self):
        if self.flButton.icon == "screen-rotation":
            if Window.width > Window.height:
                orientation.set_landscape()
            else:
                orientation.set_portrait()
            self.flButton.icon = "screen-rotation-lock"
        else:
            orientation.set_sensor()
            self.flButton.icon = "screen-rotation"

    # searches on the selected comic sites for the search term
    def searchComicBooks(self):
        if self.ids.searchInput.text != "":
            gl.searchText = quote(self.ids.searchInput.text)
            if self.ids.apcS.active:
                gl.apcSite.toSiteComicsScreen("search")
            if self.ids.bpcS.active:
                gl.bpcSite.toSiteComicsScreen("search")

    def slideChange(self, *args):
        try:
            self.carouselLbl.text = f" {self.carousel.index + 1}/{len(self.carousel.slides)}"
        except:
            pass

    def slideFirst(self, *args):
        self.carousel.load_slide(self.carousel.slides[0])

    def slideLast(self, *args):
        self.carousel.load_slide(self.carousel.slides[len(self.carousel.slides) - 1])

    # shows all favorited comic books
    def toFavComicBookScreen(self):
        self.topAppBar.title = "Favorite Comic Books"
        gl.goToScreen("comic")
        gl.listComicBooks("", gl.favs)


#   class for running the app

class CG(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"  # Light
        self.theme_cls.primary_palette = "Amber"  #  Red, Pink, Purple, DeepPurple, Indigo, Blue, LightBlue, Cyan, Teal, Green, LightGreen, Lime, Yellow, Amber, Orange, DeepOrange, Brown, Gray, BlueGray
        return GroundLayout()


# only runns the app if executed from this file
if __name__ == "__main__":
    CG().run()