# coding: utf-8
from masterTools.misc.MasterToolsProcessor import MasterToolsProcessor # for testing
from defconAppKit.windows.baseWindow import BaseWindowController
from masterTools.UI.settings import Settings
from masterTools.misc.fontPartsMethods import calculateSelection
from masterTools.UI.vanillaSubClasses import MTList,  MTFloatingDialog
from vanilla import *
from mojo.events import addObserver, removeObserver
from mojo.canvas import CanvasGroup
from mojo.UI import AllGlyphWindows
from mojo.roboFont import AllFonts, RGlyph, CurrentGlyph
# from masterTools.UI.glyphCellFactory import GlyphCellFactory
# glyphcell = GlyphCellFactory(item["font"][self.glyphExampleName], 100, 100,glyphColor=glyphColor,bufferPercent=.01)

key = "com.rafalbuchner.MasterTools.MasterCompatibilityTable"

class CompatibilityTableWindow(MTFloatingDialog, BaseWindowController):
    id = "com.rafalbuchner.masterCompatibilityTableWindow"
    winMinSize = (100,70)
    winMaxSize = (6000,5000)
    txtH = 17
    btnH = 24
    padding = 10

    def __init__(self, designspace, testMode=False):
        if not testMode:
            self.designspace = designspace
        if testMode:
            path = '/Users/rafalbuchner/Dropbox/drawBot/blow/blow-designspace.designspace'
            self.designspace = MasterToolsProcessor()
            self.designspace.read(path)
            self.designspace.loadFonts()

        self.glyph = None
        if CurrentGlyph() != None: self.glyph = CurrentGlyph()
        self.fonts = []


    # UI
    def initUI(self):
        # init settings
        self.uiSettingsControler = Settings()
        self.uiSettings = self.uiSettingsControler.getDict()
        x,y,p = self.padding, self.padding, self.padding
        self.view = Group((10, 0, -10, -0))
        self.infoGroup = Group((0, y, -0, -p))
        self.infoGroup.title = TextBox((5, 0, -0, -p), "info")
        self.infoGroup.box = Box((0, self.btnH, -0, -0))
        infoDescriptions = [
            dict(title="title"),
            dict(title="info", alignment="right", truncateFromStart=True),
        ]
        if self.glyph is not None:
            listItems = [dict(title=title, info=self.info[title]) for title in self.info]
        else:
            listItems = []
        self.infoGroup.box.currentInfo = MTList((0, 0, -0, -0),
                                                listItems,
                                                columnDescriptions=infoDescriptions,
                                                transparentBackground=True,
                                                showColumnTitles=False,
                                                allowSelection=False
                                                )

        self.tableContainer = Box((0, y, -0, -p))

        self.tableContainer.list = MTList((0, 0, -0, -0),
                                          self.items,
                                          columnDescriptions=self.fontsDescriptor,
                                          transparentBackground=True,
                                          allowSelection=False
                                          )
        # this splitView will help user to control width of the table
        self.makeSplitView()

        self.w = self.window(self.winMinSize,
        "Master Compatibility Table",
        minSize=self.winMinSize,
        maxSize=self.winMaxSize,
        autosaveName=self.id,
        darkMode=self.uiSettings["darkMode"],
        closable=False,
        noTitleBar=True)
        self.w.view = self.view


    def makeSplitView(self):
        paneDescriptors = [
            dict(view=self.infoGroup, identifier="infoPane", size=210, canCollapse=False),
            dict(view=self.tableContainer, identifier="table", canCollapse=False),
        ]
        self.view.splitView = SplitView((0, 0, -0, -0), paneDescriptors, dividerStyle="splitter",
                                        autosaveName=key + ".view.SplitView")
        self.view.splitView.getNSSplitView().setDividerStyle_(1)

    ### mastertools template actions:
    def start(self):
        if CurrentGlyph() != None: self.glyph = CurrentGlyph()
        self.updateFonts(None)
        self.updateItems()
        self.initUI()
        self.w.open()
        self.addObservers()

    def finish(self):
        self.w.close()
        self.removeObservers()

    ### adding/removing observers
    def addObservers(self):
        addObserver(self, "glyphWindowWillOpenObserver",  "glyphWindowWillOpen")
        addObserver(self, "glyphWindowWillCloseObserver", "glyphWindowWillClose")
        addObserver(self, "currentGlyphChangedObserver",  "currentGlyphChanged")
        addObserver(self, "updateFonts",                  "MT.designspace.fontMastersChanged")

    def removeObservers(self):
        removeObserver(self, "glyphWindowWillOpen")
        removeObserver(self, "glyphWindowWillClose")
        removeObserver(self, "currentGlyphChanged")
        removeObserver(self, "MT.designspace.fontMastersChanged")

    ### Observers

    def glyphWindowWillOpenObserver(self, info):
        currGlyph = info.get("glyph")
        if currGlyph is not None:
            self.glyph = currGlyph

        try:
            self.glyph.addObserver(self, "glyphChangedObserver", "Glyph.Changed")
            self.updateFonts(None)
            self.updateItems()
        except:
            self.updateFonts(None)
            self.updateItems()

        self.infoGroup.box.currentInfo.set(
                                  [dict(title=title,info=self.info[title]) for title in self.info]
                               )

        self.tableContainer.list = MTList((0, 0, -0, -0),
                              self.items,
                              columnDescriptions=self.fontsDescriptor,
                              mainWindow=window,
                              transparentBackground=True,
                              allowSelection=False
                               )
        # this splitView will help user to control width of the table
        self.makeSplitView()

    def glyphWindowWillCloseObserver(self, sender):
        if self.glyph != None:
            self.glyph.removeObserver(self, "Glyph.Changed")

    def currentGlyphChangedObserver(self, info):
        if self.glyph != None:
            self.glyph.removeObserver(self, "Glyph.Changed")
        self.glyph = info["glyph"]
        if self.glyph != None:
            self.glyph.addObserver(self, "glyphChangedObserver", "Glyph.Changed")

        self.updateItems()

        self.tableContainer.list.set(self.items)
        self.infoGroup.box.currentInfo.set([dict(title=title,info=self.info[title]) for title in self.info])

    def glyphChangedObserver(self, sender):
        self.updateItems()
        if hasattr(self.tableContainer, "list"):
            self.tableContainer.list.set(self.items)
        self.infoGroup.box.currentInfo.set([dict(title=title,info=self.info[title]) for title in self.info])

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
            self.fontsDescriptor += [{"title": fontName,"alignment":"right","truncateFromStart":True}]

        if sender != None:
            del self.tableContainer
            del self.view.splitView
            self.tableContainer = Box((0, y, -0, -p))
            self.tableContainer.list = MTList((0, 0, -0, -0),
                              self.items,
                              columnDescriptions=self.fontsDescriptor,
                              transparentBackground=True,
                              allowSelection=False
                                   )
            self.makeSplitView()

    # table actions
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
                if gName in font.keys():
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
                else:
                    columns[masterName] = ["!NO GLYPH!"]*17
                    pass


            for i in range(maxNumOfContours-1,-1,-1):
                row = {}
                row["contours"] = "C%s" % (i)

                compatible = True
                if not fontName:
                    print("Master-Tools-issue!!!")
                    continue
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
        if hasattr(self, "tableContainer"):
            table = self.tableContainer.list.getNSTableView()
            highlightRowIds = []
            highlightColumnIds = []

            for rowId, row in enumerate(self.items):
                if " ERR" in row["contours"]:
                    highlightRowIds += [rowId]
                if rowId == 0:
                    # it is enough to iterate only once: every other row
                    # of column with '!NO GLYPH!' will have the same value
                    for columnId, cellText in enumerate( row.values() ):
                        if '!NO GLYPH!' == cellText:
                            highlightColumnIds += [columnId]

            cellDescription = {}
            for rowId in range(len(self.items)):
                for columnId in range(len(table.tableColumns())):
                    if rowId in highlightRowIds:
                        cellDescription[(columnId,rowId)] = (1,0,0,.3)
                    if columnId in highlightColumnIds:
                        cellDescription[(columnId,rowId)] = (1,0,0.7,.3)


            self.tableContainer.list.setCellHighlighting(cellDescription)




key = "com.rafalbuchner.MasterTools.MasterCompatibilityTable"

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
            self.glyph.addObserver(self, "glyphChangedObserver", "Glyph.Changed")
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
        self.infoGroup = Group((0,y,-0,-p))
        self.infoGroup.title = TextBox((5,0,-0,-p),"info")
        self.infoGroup.box = Box((0, self.btnH, -0, -0))
        infoDescriptions = [
            dict(title="title"),
            dict(title="info", alignment="right",truncateFromStart=True),
        ]
        self.infoGroup.box.currentInfo = MTList((0, 0, -0, -0),
                              [dict(title=title,info=self.info[title]) for title in self.info],
                              columnDescriptions=infoDescriptions,
                              transparentBackground=True,
                              showColumnTitles=False,
                              allowSelection=False
                               )

        self.tableContainer = Box((0, y, -0, -p))
        self.tableContainer.list = MTList((0, 0, -0, -0),
                              self.items,
                              columnDescriptions=self.fontsDescriptor,
                              mainWindow=window,
                              transparentBackground=True,
                              allowSelection=False
                               )
        # this splitView will help user to control width of the table
        self.makeSplitView(view)
        window.addGlyphEditorSubview(view)
        self.windows[window] = view # I think overlapping is going on here

    def makeSplitView(self, view):
        __emptyGroup = Group((0,0,0,-0))
        paneDescriptors = [
            dict(view=__emptyGroup, identifier="emptyGroupLeft", canCollapse=False, size=1, minSize=0, resizeFlexibility=False),
            dict(view=self.infoGroup, identifier="infoPane",size=210,minSize=50,canCollapse=False),
            dict(view=self.tableContainer, identifier="table", canCollapse=False),
            dict(view=__emptyGroup, identifier="emptyGroupRight", canCollapse=False, size=1, minSize=0, resizeFlexibility=False),
        ]
        view.splitView = SplitView((0, 0, -0, -0), paneDescriptors,dividerStyle="splitter",autosaveName=key+".view.SplitView")
        view.splitView.getNSSplitView().setDividerStyle_(1)


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
            self.fontsDescriptor += [{"title": fontName,"alignment":"right","truncateFromStart":True}]

        if sender != None:
            for window in self.windows:
                view = self.windows[window]
                del self.tableContainer
                del view.splitView
                self.tableContainer = Box((0, y, -0, -p))
                self.tableContainer.list = MTList((0, 0, -0, -0),
                                  self.items,
                                  columnDescriptions=self.fontsDescriptor,
                                  mainWindow=window,
                                  transparentBackground=True,
                                  allowSelection=False
                                       )
                self.makeSplitView(view)
                #self.infoGroup.box.info = TextBox((x,y,120-p,-p),"".join([f"{self.info[info]}\n"for info in self.info]))

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
                if gName in font.keys():
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
                else:
                    columns[masterName] = ["!NO GLYPH!"]*17
                    pass


            for i in range(maxNumOfContours-1,-1,-1):
                row = {}
                row["contours"] = "C%s" % (i)

                compatible = True
                if not fontName:
                    print("Master-Tools-issue!!!")
                    continue
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
            if hasattr(self.tableContainer, "list"):
                table = self.tableContainer.list.getNSTableView()
                highlightRowIds = []
                highlightColumnIds = []

                for rowId, row in enumerate(self.items):
                    if " ERR" in row["contours"]:
                        highlightRowIds += [rowId]
                    if rowId == 0:
                        # it is enough to iterate only once: every other row
                        # of column with '!NO GLYPH!' will have the same value
                        for columnId, cellText in enumerate( row.values() ):
                            if '!NO GLYPH!' == cellText:
                                highlightColumnIds += [columnId]

                cellDescription = {}
                for rowId in range(len(self.items)):
                    for columnId in range(len(table.tableColumns())):
                        if rowId in highlightRowIds:
                            cellDescription[(columnId,rowId)] = (1,0,0,.3)
                        if columnId in highlightColumnIds:
                            cellDescription[(columnId,rowId)] = (1,0,0.7,.3)


                self.tableContainer.list.setCellHighlighting(cellDescription)

    def observerGlyphWindowWillClose(self, sender):
        if self.glyph != None:
            self.glyph.removeObserver(self, "Glyph.Changed")

    def currentGlyphChangedObserver(self, info):
        if self.glyph != None:
            self.glyph.removeObserver(self, "Glyph.Changed")
        self.glyph = info["glyph"]
        if self.glyph != None:
            self.glyph.addObserver(self, "glyphChangedObserver", "Glyph.Changed")

        self.updateItems()

        for window in self.windows:
            view = self.windows[window]
            self.tableContainer.list.set(self.items)
            self.infoGroup.box.currentInfo.set([dict(title=title,info=self.info[title]) for title in self.info])

    def glyphChangedObserver(self, sender):
        self.updateItems()
        for window in self.windows:
            if hasattr(self.tableContainer, "list"):
                self.tableContainer.list.set(self.items)
            self.infoGroup.box.currentInfo.set([dict(title=title,info=self.info[title]) for title in self.info])

    def observerDraw(self, notification):
        for window in self.windows:
            view = self.windows[window]
            if hasattr(self.tableContainer, "list"):
                self.tableContainer.list.show(True)
            self.infoGroup.show(True)

    def observerDrawPreview(self, notification):
        # hide the view in Preview mode
        for window in self.windows:
            view = self.windows[window]
            if hasattr(self.tableContainer, "list"):
                self.tableContainer.list.show(True)
            self.infoGroup.show(True)

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
    CompatibilityTableWindow(None, testMode=True)
