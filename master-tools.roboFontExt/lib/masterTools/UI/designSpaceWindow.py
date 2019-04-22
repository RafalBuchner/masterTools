#import importlib
from vanilla import HelpButton, Sheet, Button, Group, Box, SplitView, TextBox, Window, CheckBoxListCell, GradientButton, SquareButton, ImageButton, ImageView, ImageListCell
from vanilla.vanillaBase import osVersionCurrent, osVersion10_14
from masterTools.misc.masterSwitcher import switchMasterTo, resizeOpenedFont
from masterTools.misc import MasterToolsProcessor
from masterTools.UI.objcBase import MTVerticallyCenteredTextFieldCell, setTemplateImages
from masterTools.UI.vanillaSubClasses import MTlist, MTDialog, MTInteractiveSBox, MTGlyphPreview
from masterTools.UI.settings import Settings
from masterTools.UI.glyphCellFactory import GlyphCellFactory
from defconAppKit.windows.baseWindow import BaseWindowController
from masterTools import copy2clip, getDev
from mojo.UI import AccordionView
from mojo.extensions import ExtensionBundle
import os, AppKit,      sys
from mojo.events import addObserver, removeObserver, publishEvent
from mojo.roboFont import AllFonts, CurrentFont, OpenFont, OpenWindow
from mojo.events import addObserver

uiSettingsControler = Settings()
uiSettings = uiSettingsControler.getDict()


if getDev():
    currpath = os.path.join( os.path.dirname( __file__ ), '../..' )
    sys.path.append(currpath)
    sys.path = list(set(sys.path))
    pathForBundle = os.path.abspath(os.path.join(__file__ ,"../../../.."))
    resourcePathForBundle = os.path.join(pathForBundle, "resources")
    bundle = ExtensionBundle(path=pathForBundle, resourcesName=resourcePathForBundle)
else:
    bundle = ExtensionBundle("master-tools")
table_icon = bundle.getResourceImage("table-icon", ext='pdf')
drop_icon = bundle.getResourceImage("drop-icon", ext='pdf')
drop_hover_icon = bundle.getResourceImage("drop-hover-icon", ext='pdf')
kink_icon = bundle.getResourceImage("kink-icon", ext='pdf')
glyphs_icon = bundle.getResourceImage("glyphs-icon", ext='pdf')
problem_icon = bundle.getResourceImage("problem-icon", ext='pdf')
settings_icon = bundle.getResourceImage("settings-icon", ext='pdf')
closeIcon = bundle.getResourceImage("close-icon", ext='pdf')
closed_font_icon = bundle.getResourceImage("closed-font-icon", ext='pdf')
opened_font_icon = bundle.getResourceImage("opened-font-icon", ext='pdf')
setTemplateImages(table_icon, drop_icon, drop_hover_icon, kink_icon, glyphs_icon, problem_icon, settings_icon, closeIcon, closed_font_icon, opened_font_icon)



class DesignSpaceWindow(MTDialog, BaseWindowController):
    rowHeight = MTDialog.txtH + MTDialog.padding[0] * 2
    # winMinSize = (230,519)
    winMinSize = (160,519)
    winMaxSize = (1180,4000)
    glyphExampleName = uiSettings["previewGlyphName"]
    fontListColumnDescriptions = [
        dict(title="openedImage",cell=ImageListCell(), width=50),

        dict(title="include",cell=CheckBoxListCell(),width=30),
        dict(title="fontname", cell=MTVerticallyCenteredTextFieldCell.alloc().init(), editable=False),
        dict(title="glyphExample",cell=ImageListCell(), width=60),
        dict(title="positionString", cell=MTVerticallyCenteredTextFieldCell.alloc().init(), editable=False),

        ]
    designSpaceInfoKeys = [
            "path", "number of masters", "full compatibility", "axes"
        ]
    def __init__(self, designSpacePath=None):

        self.designspace = None
        self.fontNameColumn = None
        self.glyphExampleColumn = None
        self.currentFont = None
        self.fonts = []
        self.w = self.window(self.winMinSize,
        "Master Tools",
        minSize=self.winMinSize,
        maxSize=self.winMaxSize,
        autosaveName="com.rafalbuchner.designspacewindow",
        darkMode=uiSettings["darkMode"])


        self.initObservers()

        # building groups
        self.initFontsGroup()
        self.initInfoGroup()
        self.initToolsGroup()
        self.initGlyphGroup() ###TEST


        # setting the fontNameColumn // needed for resizing main window

        fontPaneNSTable = self.fontPane.list.getNSTableView()
        for column in fontPaneNSTable.tableColumns():
            if column.headerCell().title() == "fontname":
                self.fontNameColumn = column
            if column.headerCell().title() == "positionString":
                self.positionNameColumn = column
            if column.headerCell().title() == "glyphExample":
                self.glyphExampleColumn = column

        # building splitView
        descriptions = [
            dict(label="masters",
                view=self.fontPane,
                identifier="fontPane",
                size=self.fontPaneHeight,
                minSize=self.fontPaneMinHeight,
                canCollapse=False,
                resizeFlexibility=True
                ),
            dict(label="prev",
                view=self.glyphPane,
                identifier="glyphPane",
                minSize=self.glyphPaneMinHeight,
                canCollapse=False,
                resizeFlexibility=False,
                ),
            dict(label="design space info",
                view=self.infoPane,
                identifier="infoPane",
                maxSize=self.infoPaneHeight,
                minSize=self.infoPaneMinHeight,
                canCollapse=False,
                resizeFlexibility=False),
            dict(label="tools",
                view=self.toolsPane,
                identifier="toolsPane",
                size=self.toolsPaneHeight,
                minSize=self.toolsPaneHeight,
                maxSize=self.toolsPaneHeight,
                canCollapse=False,
                resizeFlexibility=False
                ),
        ]
        self.w.SplitView = SplitView((0, 0, -0, -0),
                descriptions,
                isVertical=False,
                dividerStyle="thin")#,autosaveName = "com.rafalbuchner.masterTools.panes")
        #self.w.closeBtn = SquareButton((0,-10-self.btnH,-0,self.btnH), "close",callback=self.closeCB)

        self.w.bind("close", self.closeDesignSpaceMainWindow)
        self.w.bind("resize", self.resizeDesignSpaceMainWindow)

        if designSpacePath is not None:
            self.loadDesignSpaceFile(designSpacePath)

        self.w.open()

        #self.setUpBaseWindowBehavior()
        self.resizeDesignSpaceMainWindow(self.w)
        self.w.getNSWindow().resignFirstResponder()
        self.w.getNSWindow().makeFirstResponder_(self.glyphPane.prev.getNSBox())
        self.w.getNSWindow().firstResponder().acceptsFirstMouse_(True)

    def initObservers(self):
        addObserver(self, "currentFontChangeCB", "fontBecameCurrent")
        addObserver(self, "reloadFontListCB", "fontDidOpen")
        addObserver(self, "reloadFontListCB", "fontDidClose")

    def initGlyphGroup(self):
        x,y,p = self.padding
        self.glyphPane = Group((0, 0, -0, -0))
        self.glyphPane.caption = TextBox((x, y, 150,self.txtH), "preview")
        y = self.txtH + p   +p
        self.glyphPane.prev = MTGlyphPreview((x,y,-p,-p), self.designspace)
        self.glyphHeight = 1200
        self.glyphPaneMinHeight = self.txtH + p*2

    # initilazing groups
    def initFontsGroup(self):
        x,y,p = self.padding
        self.fontPane = Group((0, 0, -0, -0))
        self.fontPane.caption = TextBox((x, y, 150,self.txtH), "masters")
        y = self.txtH + p   +p

        # image for dropping
        self.fontPane.dropIcon = ImageView(
            (0,y,-0,-0))
        self.fontPane.dropIcon.setImage(imageObject=drop_icon)
        self.fontPane.dropIcon.getNSImageView().setToolTip_("drop designspace file here")
        # creating custom list
        dropSettings = dict(type=AppKit.NSFilenamesPboardType, operation=AppKit.NSDragOperationCopy, callback=self.dropFontListCallback)


        self.fontPane.list = MTlist(
                        (0,y,-0,-0),
                        [],# test
                        rowHeight=self.rowHeight,
                        columnDescriptions=self.fontListColumnDescriptions,
                        transparentBackground=True,
                        allowsMultipleSelection=False,
                        showColumnTitles=False,
                        editCallback=self.fontIsIncludedCB,
                        doubleClickCallback=self.doubleClickFontListCB,
                        selectionCallback=self.selectionFontListCB,
                        otherApplicationDropSettings=dropSettings)

        # preparing even cooler look:
        fontPaneNSTable = self.fontPane.list.getNSTableView()


        # setting selection to None for now: (should be set to the Current Font, which should be stored as a separate attr)
        self.fontPane.list.setSelection([])
        #self.w.getNSWindow().makeFirstResponder_(fontPaneNSTable)
        # setting highlighting style (maybe it should be done in MTlist class)
        fontPaneNSTable.setSelectionHighlightStyle_(4)

        self.fontPaneHeight = 200
        self.fontPaneMinHeight = self.txtH + p*2



    def initInfoGroup(self):
        x,y,p = self.padding
        self.infoPane = Group((0, 0, -0, -0))
        self.infoPane.caption = TextBox((x, y, 150,self.txtH), "design space info")
        y = self.txtH + p*2
        self.infoPane.box = Box((x,y,-p,-p))
        columnDescriptions = [{"title": "name","font":AppKit.NSFont.systemFontOfSize_(10),"width":140}, {"title": "value","textColor":((0,1,0,1)),"font":("Monaco",10),"alignment":"right"}]

        initialItems = [dict(name=key)for key in self.designSpaceInfoKeys]
        self.infoPane.box.list = MTlist(
                        (0,0,-0,-0),
                        initialItems,
                        columnDescriptions=columnDescriptions,
                        transparentBackground=True,
                        allowsMultipleSelection=False,
                        showColumnTitles=False,
                        doubleClickCallback=self.doubleClickInfoListCB)

        self.infoPane.box.list.getNSTableView().setSelectionHighlightStyle_(4)
        self.infoPane.box.list.getNSTableView().setToolTip_("double click to copy to clickboard")
        self.infoPane.box.list.setSelection([])

        self.infoPaneHeight = 200
        self.infoPaneMinHeight = self.txtH + p*2



    def initToolsGroup(self):
        x,y,p = self.padding
        self.toolsPane = Group((0, 0, -0, -0))
        self.toolsPane.caption = TextBox((x, y, 150,self.txtH), "tools")
        self.toolsPane.settingsBtn = GradientButton((-self.btnH-8,8,self.btnH,self.btnH),imageObject=settings_icon, bordered=False, callback=self.settingsBtnCB)
        y += self.txtH + p

        toolbarItems = [
                dict(objname="compatibilityTable", imageObject=table_icon, toolTip="comaptibility table", callback=self.compatibilityTableToolitemCB),
                dict(objname="kinkManager", imageObject=kink_icon, toolTip="kink manager", callback=self.compatibilityTableToolitemCB),
                dict(objname="incompatibleGlyphsBrowser", imageObject=glyphs_icon, toolTip="incompatible glyphs browser", callback=self.compatibilityTableToolitemCB),
                dict(objname="problemSolvingTools", imageObject=problem_icon, toolTip="problem solving tools", callback=self.compatibilityTableToolitemCB),
            ]

        self.toolsPane.toolbar = self.toolbar((x,y), items=toolbarItems, itemSize=self.btnH*3, padding=20)
        #self.toolsPane.toolbar = self.toolbar((x,y), items=toolbarItems, itemSize=self.btnH*3, padding=0)


        self.toolsPaneHeight = self.btnH*3 + y+p

    # ---------------------
    # Callbacks
    # ---------------------
    def currentGlyphChangedCB(self, info):
        print(info)

    def doubleClickFontListCB(self, sender):
        item = self.designspace.fontMasters[sender.getSelection()[0]]
        selectedDefconFont = item.get("font")
        selectedRoboFontFont = item.get("robofont.font")

        # don't know why, but sometimes ["robofont.font"] changes into the NSNull
        # here I'm checking if it is NSNull or NoneType or RFont
        if hasattr(selectedRoboFontFont,"isNull"):
            if selectedRoboFontFont.isNull() == 1:
                item["robofont.font"] = None
                selectedRoboFontFont = None

        if selectedRoboFontFont is None:
            if self.currentFont is not None:
                item["robofont.font"] = resizeOpenedFont(self.currentFont, selectedDefconFont.path)
            else:
                item["robofont.font"] = OpenFont(selectedDefconFont.path)
        else:
            selectedRoboFontFont.close()
            item["robofont.font"] = None

    def selectionFontListCB(self, sender):
        if sender.getSelection():
            item = self.designspace.fontMasters[sender.getSelection()[0]]
            selectedRoboFontFont = item.get("robofont.font")

            # don't know why, but sometimes ["robofont.font"] changes into the NSNull
            # here I'm checking if it is NSNull or NoneType or RFont
            if hasattr(selectedRoboFontFont,"isNull"):
                if selectedRoboFontFont.isNull() == 1:
                    item["robofont.font"] = None
                    selectedRoboFontFont = None

            if selectedRoboFontFont is not None: #and not isinstance(selectedRoboFontFont, AppKit.NSNull):
                switchMasterTo(selectedRoboFontFont)

    def currentFontChangeCB(self, sender):
        windowTypes = [w.windowName() for w in AppKit.NSApp().orderedWindows() if w.isVisible() if hasattr(w, "windowName")]
        skip = ["PreferencesWindow", "ScriptingWindow"]
        fontWindowTypes = list(set(windowTypes) - set(skip))
        setSelection = True
        if fontWindowTypes == ["FontWindow"]:
            # if there are only FontWindows opened
            # there is a bug when setting selection
            # - here I'm getting rid of it
            setSelection = False

        for i,item in enumerate(self.designspace.fontMasters):
            robofont = item.get("robofont.font")
            # don't know why, but sometimes ["robofont.font"] changes into the NSNull
            # here I'm checking if it is NSNull or NoneType or RFont
            if hasattr(robofont,"isNull"):
                if robofont.isNull() == 1:
                    item["robofont.font"] = None
                    robofont = None

            if robofont is not None:
                if sender is not None:
                    if robofont == CurrentFont():

                        # if setSelection:
                        self.fontPane.list.setSelection([i])
                        self.currentFont = CurrentFont()

                        break
                else:
                    break


    def doubleClickInfoListCB(self, sender):
        value = sender.get()[sender.getSelection()[0]].get("value")
        if value is not None:
            copy2clip(str(value))
        self.infoPane.box.list.setSelection([])

    def settingsBtnCB(self, sender):
        def _close(sender):
            uiSettingsControler.closeSettingsPanel()
            self.settings.close()
        x,y,p = self.padding
        self.settings = self.settingsSheet((420, 700), self.w)#,title="settings")

        self.settings.closeSettingsBtn = GradientButton((-p-self.btnH, y, self.btnH, self.btnH),imageObject=closeIcon, bordered=False, callback=_close)
        self.settings.helpBtn = HelpButton((x, y, 21, 20))
        uiSettingsControler.settingsPanel(self.settings,40)
        self.settings.open()

    def fontIsIncludedCB(self, sender):
        self.designspace.fontMasters = sender.get()

    def compatibilityTableToolitemCB(self, sender):
        # checkbox functionality of btn in Tools Group
        print("test - compatibilityTableToolitemCB")
        pass

    def reloadFontListCB(self, info):
        self.items = self.prepareFontItems(self.designspace.fontMasters) ###TEST
        self.fontPane.list.set(self.designspace.fontMasters)
        self.currentFontChangeCB(None)

    def closeDesignSpaceMainWindow(self, sender):
        removeObserver(self, "fontDidOpen")
        removeObserver(self, "fontDidClose")
        removeObserver(self, "fontBecameCurrent")
        self.glyphPane.prev.mainWindowClose()

    def resizeDesignSpaceMainWindow(self, sender):
        x,y,p = self.padding
        wx,wy,ww,wh = sender.getPosSize()
        print(ww)
        fontlistBreakingPoint = 260
        fontlistBreakingPoint2 = 440
        fontTable = self.fontNameColumn.tableView()
        infoNameColumn = self.infoPane.box.list.getNSTableView().tableColumns()[0]

        itemSize = self.toolsPane.toolbar.itemSize
        self.toolsPane.toolbar.setPosSize((x,y,ww-2*p,itemSize))
        if self.fontNameColumn is not None:
            self.positionNameColumn.setMaxWidth_(300)
            self.positionNameColumn.setMinWidth_(50)
            # self.fontNameColumn.setMaxWidth_(750)
            # self.fontNameColumn.setMinWidth_(100)
            if ww <= fontlistBreakingPoint2:
                self.positionNameColumn.setHidden_(True)
            else:
                self.positionNameColumn.setHidden_(False)
            if ww <= fontlistBreakingPoint:
                self.glyphExampleColumn.setResizable_(True)
                self.glyphExampleColumn.setMaxWidth_(300)
                self.glyphExampleColumn.setMinWidth_(40)
                self.fontNameColumn.setHidden_(True)
                infoNameColumn.setHidden_(True)
                bigRowHeight = 70
                fontTable.setRowHeight_(bigRowHeight)
                fontTable.sizeToFit()
            else:
                self.glyphExampleColumn.setResizable_(False)
                self.glyphExampleColumn.setMaxWidth_(60)
                self.glyphExampleColumn.setMinWidth_(60)
                self.fontNameColumn.setHidden_(False)
                infoNameColumn.setHidden_(False)
                fontTable.sizeToFit()
                fontTable.setRowHeight_(self.rowHeight)

    # ---------------------
    # Customization of vanilla objects
    # ---------------------

    def dropFontListCallback(self, sender, dropInfo):

        # some cool hovering options ;)
        isProposal = dropInfo["isProposal"]
        paths = dropInfo["data"]
        designSpaceLoaded = False
        foundDesignSpace = None
        if len(paths) == 1:
            path = paths[0]
            if os.path.splitext(path)[-1].lower() == ".designspace":
                foundDesignSpace = True
                self.fontPane.dropIcon.setImage(imageObject=drop_hover_icon)

                if not isProposal:
                    self.loadDesignSpaceFile(path)

        return True



    # ---------------------
    # Actions
    # ---------------------

    def loadDesignSpaceFile(self, path):
        designSpaceLoaded = self.loadDesignSpace(path)
        lineType =AppKit.NSTableViewSolidHorizontalGridLineMask
        self.fontPane.list.getNSTableView().setGridStyleMask_(lineType)
        if designSpaceLoaded:
            self.fontPane.dropIcon.show(False)
            self.items = self.prepareFontItems(self.designspace.fontMasters) ###TEST
            self.fontPane.list.set(self.designspace.fontMasters)
            self.fontPane.list.getNSTableView().tableColumns()[1].sizeToFit()
        else:
            self.fontPane.dropIcon.setImage(imageObject=drop_icon)

    def loadInfo(self):
        path = self.designspace.path
        items = [
            dict(name="path", value=path),
            dict(name="number of masters", value=len(self.designspace.fontMasters)),
            dict(name="full compatibility", value="<not implemented>"),
            dict(name="axes", value=", ".join([axis for axis in self.designspace.getAxisOrder()])),
            ]

        self.infoPane.box.list.set(items)

    def prepareFontItems(self, designSpaceMasters):
        items = []
        for item in designSpaceMasters:
            glyphColor = AppKit.NSColor.secondaryLabelColor()
            if osVersionCurrent >= osVersion10_14 and uiSettings["darkMode"]:
                # maybe shitty way, but works…
                glyphColor = AppKit.NSColor.whiteColor()
            item["glyphExample"] = GlyphCellFactory(item["font"][self.glyphExampleName], 100, 100,glyphColor=glyphColor,bufferPercent=.01)
            # item["glyphExample"] = GlyphCellFactory(item["font"][self.glyphExampleName], 100, 100,.01,AppKit.NSColor.secondaryLabelColor())
            if item["font"].path in [font.path for font in AllFonts()]:
                item["openedImage"] = opened_font_icon
                item["opened"] = True

                # opening robofont object, to be able to show it in the RF intergace
                for font in AllFonts():
                    if font.path == item["font"].path:
                        item["robofont.font"] = font
                        break
            else:
                item["openedImage"] = closed_font_icon
                item["opened"] = False


    def loadDesignSpace(self, path):
        # try:
        self.designspace = MasterToolsProcessor()
        # self.designspace.useVarlib = True
        self.designspace.read(path)
        self.designspace.loadFonts()
        self.loadInfo()

        self.glyphPane.prev.setDesignSpace(self.designspace)
        self.glyphPane.prev.setGlyph("a")
        print("designspace imported")
        return True
        # except:
        #     print("designspace wasn't imported")
        #     return False







def test():
    import os
    #path = '/Users/rafalbuchner/Documents/repos/scripts/RoboFont3.0/+GOOGLE/master-tools/test_designSpace/mutatorSans-master/MutatorSans.designspace'
    o = OpenWindow(DesignSpaceWindow)#, path)

if __name__ == '__main__':
    test()
