# from masterTools.misc.MasterToolsProcessor import MasterToolsProcessor # for testing
from defconAppKit.windows.baseWindow import BaseWindowController
from masterTools.UI.vanillaSubClasses import MTList,  MTFloatingDialog
from masterTools.UI.settings import Settings

# from masterTools.misc.fontPartsMethods import calculateSelection
from vanilla import *
# from mojo.events import addObserver, removeObserver
# from mojo.canvas import CanvasGroup
# from mojo.UI import AllGlyphWindows
# from mojo.roboFont import AllFonts, RGlyph, CurrentGlyph

key = "com.rafalbuchner.MasterTools.ProblemSolvingTools"

class ProblemSolvingTools(MTFloatingDialog, BaseWindowController):
    id = "com.rafalbuchner.ProblemSolvingTools"
    winMinSize = (100,70)
    winMaxSize = (6000,5000)
    txtH = 17
    btnH = 24
    padding = 10
    def __init__(self, designspace):
        self.designspace = designspace
        self.isActive = False

    def start(self):
        self.initUI()
        self.w.open()
        self.addObeservers()
        self.isActive = True

    def finish(self):
        if hasattr(self, "w"):
            self.w.close()
        self.removeObservers()
        self.isActive = False

    def addObeservers(self):
        pass

    def removeObservers(self):
        pass

    def initUI(self):
        self.uiSettingsControler = Settings()
        self.uiSettings = self.uiSettingsControler.getDict()

        x, y, p = self.padding, self.padding, self.padding

        self.w = self.window(self.winMinSize,
        "Problem Solving Tools       ",
        minSize=self.winMinSize,
        maxSize=self.winMaxSize,
        autosaveName=self.id,
        darkMode=self.uiSettings["darkMode"],
        closable=True,
        noTitleBar=True)


    def closeUI(self):
        # binding to window
        self.finish()
    # RF observers

    # code goes here

    # ui callbacks

    # code goes here

    # tool actions

    # code goes here
