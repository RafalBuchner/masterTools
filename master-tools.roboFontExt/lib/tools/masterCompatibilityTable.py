# coding: utf-8

from tools.vanillaSubClasses import CompatibilityList
from vanilla import *
import mojo.drawingTools as ctx
from mojo.events import addObserver, removeObserver
from mojo.canvas import CanvasGroup
from mojo.UI import AllGlyphWindows




class CompatibilityTable(object):
    txtH = 17
    btnH = 24
    def __init__(self, testMode=False):
        # for debugging only
        self.padding = 10
        p = self.padding
        if testMode:
            self.w = HUDFloatingWindow((250, 110), "debug only")
            self.w.text = TextBox((p,p,-p,-p), "Master Compatibility is on, \nwhile this window is opened.\n\nIf you don't see the table, reopen the Glyph Edit Window")
            self.w.bind("close", self.windowClose)
            self.w.open()
        # end debugging

        self.glyph = None
        self.fonts = []
        addObserver(self, "observerGlyphWindowWillOpen", "glyphWindowWillOpen")
        addObserver(self, "observerGlyphWindowWillClose",
                    "glyphWindowWillClose")
        addObserver(self, "observerDraw", "draw")
        addObserver(self, "observerDrawPreview", "drawPreview")
        addObserver(self, "currentGlyphChangedObserver", "currentGlyphChanged")
        addObserver(self, "updateFonts", "fontDidOpen")
        addObserver(self, "updateFonts", "fontDidClose")

    def windowClose(self, sender):
        # if hasattr(self.view,"list"):
        #     del self.view.list
        # for i in self.windows:
        #     self.windows[i][1].window().unbind("resize", self.glyphWindowResizedCallback)
        removeObserver(self, "glyphWindowWillOpen")
        removeObserver(self, "draw")
        removeObserver(self, "drawPreview")
        removeObserver(self, "currentGlyphChanged")
        removeObserver(self, "fontWillClose")
        removeObserver(self, "fontDidOpen")

    def glyphWindowWillClose(self, sender):
        #sender.window().unbind("resize", self.glyphWindowResizedCallback)
        self.glyph.removeObserver(self, "Glyph.Changed")

    def glyphWindowResizedCallback(self, sender):
        print(sender.getPosSize())
        x,y,w,h = sender.getPosSize()
        if sender.view.list.tableWidth+210+18 < w-25:
            x,y,w,h =  sender.view.list.getPosSize()
            sender.view.list.setPosSize((x,y,tableWidth,h))
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
        #self.window = info["window"]
        self.glyph = info["glyph"]

        self.windows = {}

        x,y,p=(self.padding for i in range(3))
        for win_id, window in enumerate(AllGlyphWindows()):

            # create a view with some controls
            view = CanvasGroup((18, -200, -15, -19-15), delegate=self)

            view.list = CompatibilityList((x+210, y, -p, -p),
                                  self.items,
                                  columnDescriptions=self.fontsDescriptor,
                                  mainWindow=window,
                                  transparentBackground=True,)
            view.infoGroup = Group((x,y,210-p,-p))
            view.infoGroup.title = TextBox((5,0,-0,-p),"info")
            view.infoGroup.box = Box((0, self.btnH, -0, -0))
            view.infoGroup.box.info = TextBox((0,0,-0,-p), "".join([f"{self.info[info]}\n"for info in self.info]), alignment="right")
            view.infoGroup.box.infoTitles = TextBox((0,0,-0,-p), "".join([title+"\n" for title in self.info]))
            # add the view to the GlyphEditor

            window.addGlyphEditorSubview(view)
            window.window().bind("resize", self.glyphWindowResizedCallback)
            self.windows[win_id] = (view, window)

    def updateFonts(self, sender):
        x,y,p=(self.padding for i in range(3))
        self.fonts = []
        self.fontsDescriptor = [{"title": "contours"}]
        for font in AllFonts():
            self.fonts += [font]
            self.fontsDescriptor += [{"title": font.info.styleName}]
        if sender != None:
            for i in self.windows:
                view = self.windows[i][0]
                view.list.show(True)
                view.infoGroup.show(True)

                del view.list
                #del view.box

                view.list = CompatibilityList((x+210, y, -p, -p),
                                  self.items,
                                  columnDescriptions=self.fontsDescriptor,
                                  mainWindow=self.windows[i],
                                  transparentBackground=True,)

                #view.infoGroup.box.info = TextBox((x,y,120-p,-p),"".join([f"{self.info[info]}\n"for info in self.info]))

    def updateItems(self):
        if self.glyph != None:
            gName = self.glyph.name
            fontName = self.glyph.font.info.styleName
            numberOfPoints = sum([len(c.points) for c in self.glyph])
            numberSelectedOfPoints = len([p for c in self.glyph for s in c for p in s.points if p.selected])
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
        print(self.items)

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
            view.list.set(self.items)
            view.infoGroup.box.info.set("".join([f"{self.info[info]}\n"for info in self.info]))

    def glyphChanged(self, sender):
        self.updateItems()
        for i in self.windows:
            view = self.windows[i][0]
            view.list.set(self.items)
            view.infoGroup.box.info.set("".join([f"{self.info[info]}\n"for info in self.info]))

    def observerDraw(self, notification):
        for i in self.windows:
            view = self.windows[i][0]
            view.list.show(True)
            view.infoGroup.show(True)


    def observerDrawPreview(self, notification):
        # hide the view in Preview mode
        for i in self.windows:
            view = self.windows[i][0]
            view.list.show(True)
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
