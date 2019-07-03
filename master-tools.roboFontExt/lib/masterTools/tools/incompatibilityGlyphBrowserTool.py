# from masterTools.misc.MasterToolsProcessor import MasterToolsProcessor # for testing
from mojo.roboFont import CurrentFont # for testing
import AppKit
from vanilla.vanillaBase import osVersionCurrent, osVersion10_14
from defconAppKit.windows.baseWindow import BaseWindowController
from masterTools.UI.vanillaSubClasses import MTList,  MTFloatingDialog
from masterTools.UI.settings import Settings
from masterTools.UI.objcBase import MTVerticallyCenteredTextFieldCell
from masterTools.UI.glyphCellFactory import GlyphCellFactory
from vanilla import *
# from mojo.events import addObserver, removeObserver
# from mojo.canvas import CanvasGroup
# from mojo.UI import AllGlyphWindows
# from mojo.roboFont import AllFonts, RGlyph, CurrentGlyph

key = "com.rafalbuchner.MasterTools.IncompatibleGlyphsBrowser"

class IncompatibleGlyphsBrowser(MTFloatingDialog, BaseWindowController):
    id = "com.rafalbuchner.IncompatibleGlyphsBrowser"
    winMinSize = (100,70)
    winMaxSize = (6000,5000)
    txtH = 17
    btnH = 24
    padding = 10

    def __init__(self, designspace):
        self.designspace = designspace
        self.isActive = False





    def start(self):
        self.auditList = {}
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

        self.glyphColor = AppKit.NSColor.secondaryLabelColor()
        if osVersionCurrent >= osVersion10_14 and self.uiSettings["darkMode"]:
            # maybe shitty way, but works…
            self.glyphColor = AppKit.NSColor.whiteColor()

        x, y, p = self.padding, self.padding, self.padding

        self.w = self.window(self.winMinSize,
        "Incompatible Glyphs Browser",
        minSize=self.winMinSize,
        maxSize=self.winMaxSize,
        autosaveName=self.id,
        darkMode=self.uiSettings["darkMode"],
        closable=True,
        noTitleBar=True)

        testAudit = [

            "incompatible number of anchors",
            "bad order of the contours",
            "starting point in bad place",
            "different number of points",
            "different number of contours",
            "different number of components",
        ]
        for name in ["a","b","c","d"]:
            self.createAuditForLetter(testAudit, "a", 0)
        self.refreshAudit()




    def createAuditForLetter(self, auditList, letterName, rowIndex):
        def _btnCallback(sender):
            print(pressedTheButton, sender.glyphName)

        # settubg dimentions
        minSize = 50
        x, y, p = self.padding, self.padding, self.padding
        x += p*2
        auditHeight = len(auditList) * self.txtH
        btnPosSize = (x, y, minSize, -p)

        # creating button
        glyphImage = GlyphCellFactory(CurrentFont()["a"], 100, 100, glyphColor=self.glyphColor, bufferPercent=.01)
        btn = GradientButton(btnPosSize, imageObject=glyphImage, bordered=False, callback=_btnCallback)
        btn.glyphName = letterName

        # creating label
        title = TextBox((x + minSize + p*4, y, -p, self.txtH), "glyph name: " + letterName)
        y += self.txtH + p / 2

        # creating audit
        auditTxt = "\n".join(auditList)
        audit = TextBox((x + minSize + p*5, y, -p, auditHeight), auditTxt, sizeStyle="small")
        y += p + auditHeight
        line = HorizontalLine((p,y-1,-p,1))
        # setting the view and attributes
        height = y
        if height < minSize :
            height = minSize


        view = Group((0, 0, -0, height))
        view.btn = btn
        view.title = title
        view.audit = audit
        view.line = line
        view.rowHeight = height
        view.glyphName = letterName
        view.index = rowIndex

        self.auditList[letterName] = view

    def refreshAudit(self):
        for glyphName in self.auditList:
            view = self.auditList[glyphName]
            setattr(self.w, glyphName+"_obj", view )




    def closeUI(self):
        # binding to window
        self.finish()
    # RF observers

    # code goes here

    # ui callbacks

    # code goes here

    # tool actions

    # code goes here
