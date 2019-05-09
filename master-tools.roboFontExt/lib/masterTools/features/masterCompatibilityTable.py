# coding: utf-8
from masterTools.misc.fontPartsMethods import calculateSelection
from masterTools.UI.vanillaSubClasses import MTlist
from vanilla import *
import mojo.drawingTools as ctx
from mojo.events import addObserver, removeObserver
from mojo.canvas import CanvasGroup
from mojo.UI import AllGlyphWindows
from mojo.roboFont import AllFonts, RGlyph

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

    def start(self):
        addObserver(self, "observerGlyphWindowWillOpen",  "glyphWindowWillOpen")
        addObserver(self, "observerGlyphWindowWillClose", "glyphWindowWillClose")
        addObserver(self, "observerDraw",                 "draw")
        addObserver(self, "observerDrawPreview",          "drawPreview")
        addObserver(self, "currentGlyphChangedObserver",  "currentGlyphChanged")
        addObserver(self, "updateFonts",                  "MT.designspace.fontMastersChanged")

        # initilazing panel for the first time:
        for window in AllGlyphWindows():
            self.glyph = RGlyph(window.getGlyph())
            info = {
                "window": window,
                "glyph" : self.glyph
            }
            self.observerGlyphWindowWillOpen(info)

    def finish(self):
        self.deleteThePanel()
        removeObserver(self, "glyphWindowWillOpen")
        removeObserver(self, "glyphWindowWillClose")
        removeObserver(self, "draw")
        removeObserver(self, "drawPreview")
        removeObserver(self, "currentGlyphChanged")
        removeObserver(self, "MT.designspace.fontMastersChanged")

    def deleteThePanel(self):
        for window in AllGlyphWindows():
            if window in self.windows.keys():
                view = self.windows[window]
                window.removeGlyphEditorSubview(view)

    def glyphWindowWillClose(self, sender):
        self.glyph.removeObserver(self, "Glyph.Changed")

    def observerGlyphWindowWillOpen(self, info):
        currGlyph = info.get("glyph")
        if currGlyph is not None:
            self.glyph = currGlyph

        try:
            self.glyph.addObserver(self, "glyphChanged", "Glyph.Changed")
            self.updateFonts(None)
            self.updateItems()
        except:
            self.updateFonts(None)
            self.updateItems()

        x,y,p=(self.padding for i in range(3))
        # for win_id, window in enumerate(AllGlyphWindows()):
        window = info["window"]
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

        window.addGlyphEditorSubview(view)
        self.windows[window] = view # I think overlapping is going on here

    def updateFonts(self, sender):
        if sender is not None:
            self.designspace = sender['designspace']
        x,y,p=(self.padding for i in range(3))
        self.fonts = []
        self.fontsDescriptor = [{"title": "contours"}]

        for item in self.designspace.includedFonts:
            opened = item.get("openedFont")
            fontName = item["fontname"]
            if opened is None:
                self.fonts += [(fontName, item["font"])] # (fontname, font)
            else:
                self.fonts += [(fontName, opened)] # (fontname, font)
            self.fontsDescriptor += [{"title": fontName}]

        if sender != None:
            for window in self.windows:
                view = self.windows[window]
                del view.box
                view.box = Box((x+210, y, -p, -p))
                view.box.list = MTlist((0, 0, -0, -0),
                                  self.items,
                                  columnDescriptions=self.fontsDescriptor,
                                  mainWindow=window,
                                  transparentBackground=True,
                                  widthIsHeader=True)

                #view.infoGroup.box.info = TextBox((x,y,120-p,-p),"".join([f"{self.info[info]}\n"for info in self.info]))

    def updateItems(self):
        if self.glyph != None:
            gName = self.glyph.name
            fontName = ""
            for masterName,font in self.fonts:
                if font == self.glyph.font:
                    fontName = masterName
            numberOfPoints = sum([len(c.points) for c in self.glyph])
            numberSelectedOfPoints = calculateSelection(self.glyph)
            self.info = {"master": fontName,"name": gName,"contours": len(self.glyph),"points":numberOfPoints, "selected":numberSelectedOfPoints}

            self.items = []
            contours = []
            components = []
            table = []
            columns = {}
            maxNumOfContours = 0
            maxNumOfComponents = 0
            for masterName, font in self.fonts:
                glyph = font[gName]
                columns[masterName] = []
                countCountour = 0
                countComponent = 0
                for c in glyph:
                    columns[masterName] += [len(c.points)]
                    countCountour += 1
                for comp in glyph.components:
                    columns[masterName] += [comp.baseGlyph]
                    countComponent += 1
                if countCountour > maxNumOfContours:
                    maxNumOfContours = countCountour
                if countComponent > maxNumOfComponents:
                    maxNumOfComponents = countComponent

            for i in range(maxNumOfContours-1,-1,-1):
                row = {}
                row["contours"] = "C%s" % (i)

                compatible = True
                if i < len(columns[fontName]):
                    model = columns[fontName][i]
                else:
                    compatible = False
                    continue
                for masterName, font in self.fonts:
                    if i < len(columns[masterName]):
                        row[masterName] = columns[masterName][i]
                        if row[masterName] != model:
                            compatible = False
                    else:
                        row[masterName] = ""
                        compatible = False
                if not compatible:
                    row["contours"] += " ERROR!!!"

                contours += [row]

            for i in range(maxNumOfComponents-1,-1,-1):
                row = {}
                row["contours"] = "(%s) Component%s" % (gName, i)

                for masterName, font in self.fonts:
                    if maxNumOfContours+i < len(columns[masterName]):
                        row[masterName] = columns[masterName][maxNumOfContours+i]
                components += [row]

            self.items = list(reversed(contours)) + list(reversed(components))

        else:
            self.items = []

        self.updateErrorHighlighting()

    def updateErrorHighlighting(self):
        for window in self.windows:
            view = self.windows[window]
            if hasattr(view.box, "list"):
                table = view.box.list.getNSTableView()
                highlightRowIds = []
                for i, row in enumerate(self.items):
                    if " ERR" in row["contours"]:
                        highlightRowIds += [i]
                cellDescription = {}
                for rowId in highlightRowIds:
                    for columnId in range(len(table.tableColumns())):
                        cellDescription[(columnId,rowId)] = (1,0,0,.3)

                view.box.list.setCellHighlighting(cellDescription)

    def observerGlyphWindowWillClose(self, sender):
        if self.glyph != None:
            self.glyph.removeObserver(self, "Glyph.Changed")

    def currentGlyphChangedObserver(self, info):
        if self.glyph != None:
            self.glyph.removeObserver(self, "Glyph.Changed")
        self.glyph = info["glyph"]
        if self.glyph != None:
            self.glyph.addObserver(self, "glyphChanged", "Glyph.Changed")

        self.updateItems()

        for window in self.windows:
            view = self.windows[window]
            view.box.list.set(self.items)
            view.infoGroup.box.info.set("".join([f"{self.info[info]}\n"for info in self.info]))

    def glyphChanged(self, sender):
        self.updateItems()
        for window in self.windows:
            view = self.windows[window]
            if hasattr(view.box, "list"):
                view.box.list.set(self.items)
            view.infoGroup.box.info.set("".join([f"{self.info[info]}\n"for info in self.info]))

    def observerDraw(self, notification):
        for window in self.windows:
            view = self.windows[window]
            if hasattr(view.box, "list"):
                view.box.list.show(True)
            view.infoGroup.show(True)

    def observerDrawPreview(self, notification):
        # hide the view in Preview mode
        for window in self.windows:
            view = self.windows[window]
            if hasattr(view.box, "list"):
                view.box.list.show(True)
            view.infoGroup.show(True)

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
