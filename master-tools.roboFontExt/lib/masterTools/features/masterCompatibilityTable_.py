# coding: utf-8
from masterTools.misc.fontPartsMethods import calculateSelection
from masterTools.UI.vanillaSubClasses import MTlist
from vanilla import *
import mojo.drawingTools as ctx
from mojo.events import addObserver, removeObserver
from mojo.canvas import CanvasGroup
from mojo.UI import AllGlyphWindows
from mojo.roboFont import AllFonts
"""
# TODO:
    # numberSelectedOfPoints = calculateSelection(self.glyph) should be changed only when the selection changes. It cost too much memmory. (do it on mouseUp)
    # provide better comments
    def updateFonts(self):
    !!! # change naming from font.info.styleName to designspace.fontMasters["fontname"]
    !!! # use only includedFonts
"""




class CompatibilityTable(object):
    id = "com.rafalbuchner.masterCompatibilityTable"
    txtH = 17
    btnH = 24
    padding = 10
    def __init__(self, designspace):
        self.designspace = designspace
        self.glyph = None
        self.fonts = []
        self.windows = {}
        addObserver(self, "observerGlyphWindowWillOpen", "glyphWindowWillOpen")
        addObserver(self, "observerGlyphWindowWillClose", "glyphWindowWillClose")
        addObserver(self, "observerDraw", "draw")
        addObserver(self, "observerDrawPreview", "drawPreview")
        addObserver(self, "currentGlyphChangedObserver", "currentGlyphChanged")
        addObserver(self, "updateFonts", "MT.designspace.fontMastersChanged")

    def deleteThePanel(self):
        for window in AllGlyphWindows():
            for subview in window.getGlyphView().subviews():
                if hasattr(subview, "id"):
                    if subview.id == self.id:
                        window.removeGlyphEditorSubview(subview)
                        print("deleted subview")

    def __del__(self):
        self.deleteThePanel()
        removeObserver(self, "glyphWindowWillOpen")
        removeObserver(self, "glyphWindowWillClose")
        removeObserver(self, "draw")
        removeObserver(self, "drawPreview")
        removeObserver(self, "currentGlyphChanged")
        removeObserver(self, "MT.designspace.fontMastersChanged")

    def glyphWindowWillClose(self, sender):
        self.glyph.removeObserver(self, "Glyph.Changed")

    def glyphWindowResizedCallback(self, sender):
        x,y,w,h = sender.getPosSize()
        if sender.view.box.list.tableWidth+210+18 < w-25:
            tableWidth = sender.view.box.list.tableWidth
            x,y,w,h =  sender.view.box.list.getPosSize()
            sender.view.box.list.setPosSize((x,y,tableWidth,h))
            x,y,w,h =  sender.view.box.getPosSize()
            sender.view.box.setPosSize((x,y,tableWidth+10,h))

    def observerGlyphWindowWillOpen(self, info):

        self.glyph = info["glyph"]
        try:
            print("added glyph.change obesrver")
            self.glyph.addObserver(self, "glyphChanged", "Glyph.Changed")
            self.updateFonts(None)
            self.updateItems()
        except:
            self.updateFonts(None)
            pass
        self.glyph = info["glyph"]

        self.windows = {}

        x,y,p=(self.padding for i in range(3))
        for win_id, window in enumerate(AllGlyphWindows()):

            view = CanvasGroup((18, -200, -15, -19-15), delegate=self)
            view.id = self.id
            view.infoGroup = Group((x,y,210-p,-p))
            view.infoGroup.title = TextBox((5,0,-0,-p),"info")
            view.infoGroup.box = Box((0, self.btnH, -0, -0))
            view.infoGroup.box.infoTitles = TextBox((0,0,-0,-p), "".join([title+"\n" for title in self.info]))
            view.infoGroup.box.info = TextBox((0,0,-0,-p), "".join([f"{self.info[info]}\n" for info in self.info]), alignment="right")

            view.box = Box((x+210, y, -p, -p))
            view.box.list = MTlist((0, 0, -0, -0),
                                  self.items,
                                  columnDescriptions=self.fontsDescriptor,
                                  mainWindow=window,
                                  transparentBackground=True,
                                  widthIsHeader=True)
            tableWidth = view.box.list.tableWidth
            x,y,w,h =  view.box.getPosSize()
            view.box.setPosSize((x,y,tableWidth+10,h))

            window.addGlyphEditorSubview(view)
            window.window().bind("resize", self.glyphWindowResizedCallback)
            self.windows[win_id] = (view, window)

    def updateFonts(self, sender):
        if sender is not None:
            self.designspace = sender['designspace']
        x,y,p=(self.padding for i in range(3))
        self.fonts = []
        self.fontsDescriptor = [{"title": "contours"}]
        print(self.designspace)
        for item in self.designspace.fontMasters:
            opened = item.get("openedFont")
            if opened is None:
                self.fonts += [item["font"]] # (fontname, font)
            else:
                self.fonts += [opened] # (fontname, font)
            self.fontsDescriptor += [{"title": item["fontname"]}]


        if sender != None:
            for i in self.windows:
                view = self.windows[i][0]

                del view.box
                del view.box
                #del view.box
                print("!!!!!!!! add list > updateFonts")
                view.box = Box((x+210, y, -p, -p))
                view.box.list = MTlist((0, 0, -0, -0),
                                  self.items,
                                  columnDescriptions=self.fontsDescriptor,
                                  mainWindow=self.windows[i][1],
                                  transparentBackground=True,
                                  widthIsHeader=True)

                #view.infoGroup.box.info = TextBox((x,y,120-p,-p),"".join([f"{self.info[info]}\n"for info in self.info]))

    def updateItems(self):
        if self.glyph != None:
            gName = self.glyph.name
            fontName = self.glyph.font.info.styleName
            numberOfPoints = sum([len(c.points) for c in self.glyph])
            numberSelectedOfPoints = calculateSelection(self.glyph)
            self.info = {"master": fontName,"name": gName,"contours": len(self.glyph),"points":numberOfPoints, "selected":numberSelectedOfPoints}
            #self.items = [{font.info.styleName:"TEST"} for font in self.fonts for c in font[gName]]

            self.items = []
            contours = []
            components = []
            table = []
            columns = {}
            maxNumOfContours = 0
            maxNumOfComponents = 0
            for font in self.fonts:
                glyph = font[gName]
                columns[font.info.styleName] = []
                countCountour = 0
                countComponent = 0
                for c in glyph:
                    columns[font.info.styleName] += [len(c.points)]
                    countCountour += 1
                for comp in glyph.components:
                    columns[font.info.styleName] += [comp.baseGlyph]
                    countComponent += 1
                if countCountour > maxNumOfContours:
                    maxNumOfContours = countCountour
                if countComponent > maxNumOfComponents:
                    maxNumOfComponents = countComponent

            for i in range(maxNumOfContours-1,-1,-1):
                row = {}
                row["contours"] = "C%s" % (i)

                compatible = True
                if i < len(columns[self.fonts[0].info.styleName]):
                    model = columns[self.fonts[0].info.styleName][i]
                else:
                    compatible = False
                    continue
                for font in self.fonts:
                    if i < len(columns[font.info.styleName]):
                        row[font.info.styleName] = columns[font.info.styleName][i]
                        if row[font.info.styleName] != model:
                            compatible = False
                    else:
                        row[font.info.styleName] = ""
                        compatible = False
                if not compatible:
                    row["contours"] += " ERROR!!!"
                contours += [row]

            for i in range(maxNumOfComponents-1,-1,-1):
                row = {}
                row["contours"] = "(%s) Component%s" % (gName, i)
                print(type(i),i)
                print(type(maxNumOfContours),maxNumOfContours)
                for font in self.fonts:
                    if maxNumOfContours+i < len(columns[font.info.styleName]):
                        row[font.info.styleName] = columns[font.info.styleName][maxNumOfContours+i]
                components += [row]

            self.items = list(reversed(contours)) + list(reversed(components))
        else:
            self.items = []

    def observerGlyphWindowWillClose(self, sender):
        if self.glyph != None:
            self.glyph.removeObserver(self, "Glyph.Changed")

    def currentGlyphChangedObserver(self, info):
        # if hasattr(self,"glyph"):
        if self.glyph != None:
            self.glyph.removeObserver(self, "Glyph.Changed")
        self.glyph = info["glyph"]
        # self.view = info["view"]
        if self.glyph != None:
            self.glyph.addObserver(self, "glyphChanged", "Glyph.Changed")

        self.updateItems()

        for i in self.windows:
            view = self.windows[i][0]
            view.box.list.set(self.items)
            view.infoGroup.box.info.set("".join([f"{self.info[info]}\n"for info in self.info]))

    def glyphChanged(self, sender):
        self.updateItems()
        for i in self.windows:
            view = self.windows[i][0]
            view.box.list.set(self.items)
            view.infoGroup.box.info.set("".join([f"{self.info[info]}\n"for info in self.info]))

    def observerDraw(self, notification):
        for i in self.windows:
            view = self.windows[i][0]
            view.box.list.show(True)
            view.infoGroup.show(True)


    def observerDrawPreview(self, notification):
        # hide the view in Preview mode
        for i in self.windows:
            view = self.windows[i][0]
            view.box.list.show(True)
            view.infoGroup.show(True)

    # canvas delegate callbacks
    def opaque(self):
        return True

    def acceptsFirstResponder(self):
        return False

    def acceptsMouseMoved(self):
        return True

    def becomeFirstResponder(self):
        return False

    def resignFirstResponder(self):
        return False

    def shouldDrawBackground(self):
        return False


if __name__=="__main__":
    CompatibilityTable(testMode=True)
