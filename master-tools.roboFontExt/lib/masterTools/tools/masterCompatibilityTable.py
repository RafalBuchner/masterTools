# coding: utf-8
from pprint import pprint
from masterTools.misc.MasterToolsProcessor import MasterToolsProcessor # for testing
from defconAppKit.windows.baseWindow import BaseWindowController
from masterTools.UI.settings import Settings
from masterTools.misc.fontPartsMethods import calculateSelection
from masterTools.UI.vanillaSubClasses import MTList,  MTFloatingDialog
from vanilla import *
from mojo.events import addObserver, removeObserver
from mojo.canvas import CanvasGroup
from mojo.UI import AllGlyphWindows
from mojo.roboFont import AllFonts, RGlyph, CurrentGlyph, RContour
from masterTools.UI.glyphCellFactory import GlyphCellFactory
from masterTools.misc import getDev
from mojo.extensions import ExtensionBundle

if getDev():
    import sys, os
    currpath = os.path.join( os.path.dirname( __file__ ), '../..' )
    sys.path.append(currpath)
    sys.path = list(set(sys.path))
    pathForBundle = os.path.abspath(os.path.join(__file__ ,"../../../.."))
    resourcePathForBundle = os.path.join(pathForBundle, "resources")
    bundle = ExtensionBundle(path=pathForBundle, resourcesName=resourcePathForBundle)
else:
    bundle = ExtensionBundle("master-tools")
table_icon_30x30 = bundle.getResourceImage("table-icon-30x30", ext='pdf')

key = "com.rafalbuchner.MasterTools.MasterCompatibilityTable"

class CompatibilityTableWindow(MTFloatingDialog, BaseWindowController):
    id = "com.rafalbuchner.masterCompatibilityTableWindow"
    winMinSize = (100,70)
    winMaxSize = (6000,5000)
    txtH = 17
    btnH = 24
    padding = 10
    headerHeight = 40

    def __init__(self, designspace, toolBtn):
        self.designspace = designspace
        self.isActive = False
        self.glyph = None
        if CurrentGlyph() != None: self.glyph = CurrentGlyph()
        self.fonts = []
        self.toolBtn = toolBtn


    # UI
    def initUI(self):
        # init settings
        

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
                                          headerHeight=self.headerHeight,
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
            closable=True,
            noTitleBar=True)
        self.w.view = self.view
        self.w.bind('close', self.closeWindow)




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
        self.uiSettingsControler = Settings()
        self.uiSettings = self.uiSettingsControler.getDict()
        self.updateFonts(None)
        self.updateItems()
        self.initUI()
        self.w.open()
        self.addObservers()
        self.isActive = True

    def finish(self):
        if hasattr(self, "w"):
            if self.w._window is not None:
                self.w.close()
        self.removeObservers()
        self.isActive = False

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
                              transparentBackground=True,
                              headerHeight=self.headerHeight,
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
        size = self.headerHeight
        maxsize = size * 50
        width = round(int(size*1.5))
        contourWidth = size*4
        if sender is not None:
            self.designspace = sender['designspace']
        x,y,p=(self.padding for i in range(3))
        self.fonts = []
        self.fontsDescriptor = [{'title': 'contours',"alignment":"center",'image':table_icon_30x30}]

        for item in self.designspace.includedFonts:
            opened = item.get("openedFont")
            fontName = item["fontname"]
            if opened is None:
                self.fonts += [(fontName, item["font"])] # (fontname, font)
            else:
                self.fonts += [(fontName, opened)] # (fontname, font)
            # size of the cell will be determined by font's unitsPerEm
            bufferPercent = (item['font'].info.unitsPerEm / 1000) *.001
            bufferPercent = .1
            glyphcell = self.uiSettingsControler.getGlyphCellPreview_inFont(item['font'], size=(width, size*.75))
            if glyphcell is None:
                size = None
                maxsize = None

            self.fontsDescriptor += [{"title": fontName,"alignment":"center","truncateFromStart":True, 'image':glyphcell,'minWidth':width,'width':width}]

        if sender != None:
            del self.tableContainer
            del self.view.splitView
            self.tableContainer = Box((0, y, -0, -p))
            self.tableContainer.list = MTList((0, 0, -0, -0),
                              self.items,
                              columnDescriptions=self.fontsDescriptor,
                              transparentBackground=True,
                              allowSelection=False,
                              headerHeight=self.headerHeight,
                                   )
            self.makeSplitView()

    # table actions
    def updateItems(self):
        self.items = []
        if self.glyph != None:
            gName = self.glyph.name
            fontName = ""
            for masterName,font in self.fonts:
                if font == self.glyph.font:
                    fontName = masterName
            numberOfPoints = sum([len(c.points) for c in self.glyph])
            numberSelectedOfPoints = calculateSelection(self.glyph)
            self.info = {"master": fontName,"name": gName,"contours": len(self.glyph),"points":numberOfPoints, "selected":numberSelectedOfPoints}

            contours = []
            components = []
            table = []
            columns = {}
            maxNumOfContours = 0
            maxNumOfComponents = 0
            for masterName, font in self.fonts:
                print(font.__class__.__name__)
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

        pprint(self.items)
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

    def closeWindow(self, info):
        # binding to window
        self.removeObservers()
        self.isActive = False
        # resetting toolbar button status, when window is closed
        buttonObject = self.toolBtn.getNSButton()
        self.toolBtn.status = False
        buttonObject.setBordered_(False)



if __name__=="__main__":
    CompatibilityTableWindow(None, testMode=True)
