# coding: utf-8

from masterTools.UI.vanillaSubClasses import MTList
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
"""
def calculateSelection(g):
    """calculate the real number of highlighted points"""
    # moveTo special misc
    # apply for qcurves!!!
    selectedPoints = 0
    #totalNumber = 0
    for c in g:
        lastSelected = None
        if c.points[-3].selected and c.points[0].selected and c.points[0].type == "curve":

            selectedPoints += 2
            lastSelected=c.points[-3]

        iterC = iter(list(c.points))
        next(iterC,None)
        for i,p in enumerate(c.points):
            #totalNumber += 1
            prevP = c.points[i-1]
            if i > len(c.points)-1:
                nextP = next(iterC)
            else:
                nextP=c.points[0]
            if p.selected:
                if lastSelected is not None:
                    if lastSelected == c.points[i-3] and p.type == "curve" and i != 0:
                        # add selected handle points

                        selectedPoints += 2

                else:
                    # if the first selected point has outer handle, add 1
                    if c.points[i-1].type == "offcurve" and p.type != "offcurve":

                        selectedPoints += 1

                # if the last selected point has outer handle, add 1
                if i+3 < len(c.points):
                    if not c.points[i+3].selected and c.points[i+3].type == "curve":

                        selectedPoints += 1
                if i+3 == len(c.points):
                    if not c.points[0].selected and c.points[0].type == "curve":

                        selectedPoints += 1
                if i+2 == len(c.points):
                    if not c.points[1].selected and c.points[1].type == "curve":

                        selectedPoints += 1
                if i+1 == len(c.points):
                    if not c.points[2].selected and c.points[2].type == "curve":

                        selectedPoints += 1


                selectedPoints += 1
                lastSelected = p

    return selectedPoints



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
        self.windows = {}
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
        x,y,w,h = sender.getPosSize()
        if sender.view.list.tableWidth+210+18 < w-25:
            x,y,w,h =  sender.view.list.getPosSize()
            sender.view.list.setPosSize((x,y,tableWidth,h))

    def observerGlyphWindowWillOpen(self, info):
        self.glyph = info["glyph"]
        try:
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

            view.list = MTList((x+210, y, -p, -p),
                                  self.items,
                                  columnDescriptions=self.fontsDescriptor,
                                  mainWindow=window,
                                  transparentBackground=True,)
            view.infoGroup = Group((x,y,210-p,-p))
            view.infoGroup.title = TextBox((5,0,-0,-p),"info")
            view.infoGroup.box = Box((0, self.btnH, -0, -0))
            view.infoGroup.box.infoTitles = TextBox((0,0,-0,-p), "".join([title+"\n" for title in self.info]))
            view.infoGroup.box.info = TextBox((0,0,-0,-p), "".join([f"{self.info[info]}\n" for info in self.info]), alignment="right")

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

                view.list = MTlist((x+210, y, -p, -p),
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
