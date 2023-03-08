from bs4 import BeautifulSoup
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.fitimage import FitImage
from kivymd.uix.imagelist.imagelist import MDSmartTile
from kivymd.uix.label import MDLabel
from kivymd.uix.navigationdrawer import MDNavigationDrawerItem
from kivymd.toast import toast
from kivy.properties import ObjectProperty
from kivy.uix.behaviors import ButtonBehavior
from urllib.parse import quote
from urllib.request import Request, urlopen
import os
import pathlib
import requests
import shutil
import threading

import gl as gl


# variables

colors = {}
gtp = True
comics = {}
currentComicSite = ""
currentPage = 0
downloaded = False
downloadImages = []
downloadLocation = ""
downloadPath = ""
favs = {}
prevScreens = []
searchText = ""
tag = ""

apcSite = None
bpcSite = None

carousel = ObjectProperty()
carouselLbl = ObjectProperty()
cGrid = ObjectProperty()
chapterBox = ObjectProperty()
csGrid = ObjectProperty()
hideComicsSection = ObjectProperty()
hideComicSection = ObjectProperty()
nav_drawer = ObjectProperty()
popup = ObjectProperty()
scrollC = ObjectProperty()
scrollCs = ObjectProperty()
sm = ObjectProperty()
topAppBar = ObjectProperty()


# functions

def bs4(url: str):
    headers = {'User-Agent': 'Mozilla/5.0'}
    r = Request(url, headers=headers)
    try:
        conn = urlopen(r)
        data = conn.read()
        conn.close()
        soup = BeautifulSoup(data, "html.parser")
        return soup
    except:
        return None

def download(chapter = 0):
    def download_thread(chapter):
        headers = {'User-Agent': 'Mozilla/5.0'}
        cookies = requests.session().get(gl.currentComicSite).cookies
        if(len(gl.downloadImages) > 0):
            if gl.downloadLocation == "":
                path = gl.downloadPath
            else:
                path = os.path.normpath(gl.downloadLocation + "/" + gl.downloadPath)
            p = pathlib.Path(path)
            p.mkdir(parents=True, exist_ok=True)
            num = 0
            for img in gl.downloadImages:
                num = num + 1
                res = requests.get(img, stream=True, headers=headers, cookies=cookies)
                print(res.status_code)
                if res.status_code == 200:
                    print(os.path.normpath(path + "/" + str(num) + ".jpg"))
                    with open(os.path.normpath(path + "/" + str(num) + ".jpg"), "wb") as f:
                        shutil.copyfileobj(res.raw, f)
                    gl.downloaded = True
                else:
                    print(path)
                    path = os.path.normpath(path)
                    print(path)
                    os.system(f"wget {img} -O '{path}/{num}.jpg'")
                    gl.downloaded = True
                    #print("There was one or more errors while downloading")
                    #toast("There was one or more errors while downloading")
    thread = threading.Thread(target=download_thread(chapter))
    gl.downloaded = False
    thread.start()
    if gl.downloaded:
        print("Downloaded images")
        toast("Downloaded images")

def goBack(toScreen = True):
    if toScreen:
        gl.nav_drawer.active = False
        if len(gl.prevScreens) != 0:
            gl.goToScreen(gl.prevScreens.pop(), gl.sm.current == "")
            gl.prevScreens.pop()
            if len(gl.prevScreens) == 0:
                gl.topAppBar.left_action_items = [["menu", lambda x: gl.nav_drawer.set_state("open")]]
    else:    # comic pages -> comic books
        gl.topAppBar.left_action_items = [["menu", lambda x: gl.nav_drawer.set_state("open")], ["arrow-left-circle", lambda x: gl.goBack()]]
        gl.hide_widget(gl.hideComicsSection, False)
        gl.hide_widget(gl.hideComicSection)

def goToScreen(screen: str, comic = False):
    gl.nav_drawer.set_state("close")
    if gl.prevScreens == [] or screen != gl.sm.current:
        gl.prevScreens.append(gl.sm.current)
    print(gl.prevScreens)
    gl.sm.current = screen
    match screen:
        case "home":
            gl.topAppBar.title = "Home"
            gl.topAppBar.left_action_items = [["menu", lambda x: gl.nav_drawer.set_state("open")], ["arrow-left-circle", lambda x: gl.goBack()]]
            gl.topAppBar.right_action_items = [["cog-outline", lambda x: gl.goToScreen("settings")]]
            gl.comics = {}
            gl.gtp = True
        case ("settings" | "tags") as scr:
            gl.topAppBar.title = scr.capitalize()
            gl.topAppBar.left_action_items = [["menu", lambda x: gl.nav_drawer.set_state("open")], ["arrow-left-circle", lambda x: gl.goBack()]]
            gl.topAppBar.right_action_items = [["home-outline", lambda x: gl.goToScreen("home")]]
            gl.comics = {}
            gl.gtp = True
        case "comic":
            if comic:    # comic pages
                gl.topAppBar.left_action_items = [["menu", lambda x: gl.nav_drawer.set_state("open")], ["arrow-left-circle", lambda x: gl.goBack(False)]]
                gl.topAppBar.right_action_items = [["arrow-down-circle", lambda x: gl.download()]]
                gl.hide_widget(gl.hideComicsSection)
                gl.hide_widget(gl.hideComicSection, False)
                gl.scrollC.scroll_y = 1
                gl.cGrid.clear_widgets()
                gl.chapterBox.clear_widgets()
                gl.carousel.clear_widgets()
                gl.gtp = False
            else:        # comic books
                gl.topAppBar.left_action_items = [["menu", lambda x: gl.nav_drawer.set_state("open")], ["arrow-left-circle", lambda x: gl.goBack()]]
                gl.topAppBar.right_action_items = []
                gl.hide_widget(gl.hideComicsSection, False)
                gl.hide_widget(gl.hideComicSection)
                gl.scrollCs.scroll_y = 1
                gl.csGrid.clear_widgets()
                gl.gtp = True
    if screen != "comic":
        for i in range(len(gl.colors)):
            siteChild = gl.nav_drawer.children[0].children[0].children[i]
            siteChild.selected = False
            siteChild.text_color = gl.colors[siteChild.text]
    
def hide_widget(wid, dohide = True):
    if hasattr(wid, 'saved_attrs'):
        if not dohide:
            wid.height, wid.size_hint_y, wid.opacity, wid.disabled = wid.saved_attrs
            del wid.saved_attrs
    elif dohide:
        wid.saved_attrs = wid.height, wid.size_hint_y, wid.opacity, wid.disabled
        wid.height, wid.size_hint_y, wid.opacity, wid.disabled = 0, None, 0, True
    

#   custom objects
        

class BaseNavigationDrawerItem(MDNavigationDrawerItem):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.radius = 24
        #self.text_color = "#4a4939"
        self.icon_color = "#4a4939"
        #self.focus_color = "#e7e4c0"
        
class DrawerClickableItem(BaseNavigationDrawerItem):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        #self.ripple_color = "#c5bdd2"
        #self.text_color = "white"
        self.selected_color = "white"

class MDClickableLabel(ButtonBehavior, MDLabel):
    pass

class ImageButton(ButtonBehavior, FitImage):
    pass

class MDSmartTileButton(ButtonBehavior, MDSmartTile):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        r = 10
        self.radius = r
        self.box_radius = [0, 0, r, r]

class TopAppBarPlaceholder(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint = (1, None)
        self.size = (0, "70dp")
