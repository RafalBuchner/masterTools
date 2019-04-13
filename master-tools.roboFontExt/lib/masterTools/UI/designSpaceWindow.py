from vanilla import HelpButton, Sheet, Button, Group, Box, SplitView, TextBox, Window, CheckBoxListCell, GradientButton, SquareButton, ImageButton, ImageView, ImageListCell
from masterTools.misc.masterSwitcher import switchMasterTo, resizeOpenedFont
from masterTools.misc import MasterToolsProcessor
from masterTools.UI.objcBase import VerticallyCenteredTextFieldCell
from masterTools.UI.vanillaSubClasses import MTDialog, MTlist, TMTextBox
from masterTools.UI.glyphCellFactory import *

from masterTools import copy2clip
from mojo.UI import AccordionView
from mojo.extensions import ExtensionBundle
import os, AppKit,      sys
from mojo.events import addObserver, removeObserver
from mojo.roboFont import AllFonts, CurrentFont, OpenFont



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




class DesignSpaceWindow(MTDialog):
    rowHeight = MTDialog.txtH + MTDialog.padding[0] * 2
    # winMinSize = (230,519)
    winMinSize = (160,519)
    winMaxSize = (1180,4000)
    glyphExampleName = "a"
    fontListColumnDescriptions = [
        dict(title="openedImage",cell=ImageListCell(), width=50),

        dict(title="include",cell=CheckBoxListCell(),width=30),
        dict(title="fontname", cell=VerticallyCenteredTextFieldCell.alloc().init(), editable=False),
        dict(title="glyphExample",cell=ImageListCell(), width=70),

        ]
    designSpaceInfoKeys = [
        "path","number of masters","full compatibility"
        ]
    def __init__(self):
        self.fontNameColumn = None
        self.glyphExampleColumn = None
        self.currentFont = None
        self.fonts = []
        self.w = self.window(self.winMinSize,"Master Tools",minSize=self.winMinSize,maxSize=self.winMaxSize)#, autosaveName = "com.rafalbuchner.masterTools.panes"

        self.initObservers()

        # building groups
        self.initFontsGroup()
        self.initInfoGroup()
        self.initToolsGroup()

        # setting the fontNameColumn // needed for resizing main window

        fontPaneNSTable = self.fontPane.list.getNSTableView()
        for column in fontPaneNSTable.tableColumns():
            if column.headerCell().title() == "fontname":
                self.fontNameColumn = column
            if column.headerCell().title() == "glyphExample":
                self.glyphExampleColumn = column

        # building splitView
        descriptions = [
            dict(label="fonts",
                view=self.fontPane,
                identifier="fontPane",
                size=self.fontPaneHeight,
                minSize=self.fontPaneMinHeight,
                canCollapse=False,
                resizeFlexibility=True),
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
                resizeFlexibility=False),
        ]
        self.w.SplitView = SplitView((0, 0, -0, -0),
                descriptions,
                isVertical=False,
                dividerStyle="thin")#,autosaveName = "com.rafalbuchner.masterTools.panes")
        #self.w.closeBtn = SquareButton((0,-10-self.btnH,-0,self.btnH), "close",callback=self.closeCB)
        self.setUpBaseWindowBehavior()
        self.w.bind("close", self.closeDesignSpaceMainWindow)
        self.w.bind("resize", self.resizeDesignSpaceMainWindow)
        self.w.open()
        self.resizeDesignSpaceMainWindow(self.w)

    def initObservers(self):
        addObserver(self, "currentFontChangeCB", "fontBecameCurrent")
        addObserver(self, "reloadFontListCB", "fontDidOpen")
        addObserver(self, "reloadFontListCB", "fontDidClose")



    # initilazing groups
    def initFontsGroup(self):
        x,y,p = self.padding
        self.fontPane = Group((0, 0, -0, -0))
        self.fontPane.caption = TextBox((x, y, 150,self.txtH), "fonts")
        y = self.txtH + p   +p
        ### this is test: very dict should contain info for the list + fontobject
        self.fonts = [{"fontname":"gamer-medium-slant.ufo","included":True},{"fontname":"gamer-medium-slant.ufo","included":True},{"fontname":"gamer-medium-slant.ufo","included":True},{"fontname":"gamer-medium-slant.ufo","included":True},{"fontname":"gamer-medium-slant.ufo","included":True},{"fontname":"gamer-medium-slant.ufo","included":True}]

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
        item = sender.get()[sender.getSelection()[0]]
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
                OpenFont(selectedDefconFont.path)
        else:
            selectedRoboFontFont.close()
            item["robofont.font"] = None

    def selectionFontListCB(self, sender):
        if sender.getSelection():
            item = sender.get()[sender.getSelection()[0]]
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
        ########################################################
        #TEST: hard test, checking when the font becames NSNull
        ########################################################
        # # # for item in self.designspace.fontMasters:
        # # #     for key in item:
        # # #         print(">>",key,">: ",item[key])
        
        ########################################################
        for i,item in enumerate(self.designspace.fontMasters):
            robofont = item.get("robofont.font")
            print(robofont) ## TEST
            if robofont is not None:
                if sender is not None:
                    if robofont == sender["font"]:
                        
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
            self.settings.close()
        x,y,p = self.padding
        self.settings = self.settingsSheet((600, 700), self.w)
        self.settings.closeSettingsBtn = GradientButton((-p-self.btnH, -p+self.btnH, self.btnH, self.btnH),imageObject=closeIcon, bordered=False, callback=_close)
        self.settings.helpBtn = HelpButton((x, y, 21, 20))
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

    def resizeDesignSpaceMainWindow(self, sender):
        x,y,p = self.padding
        wx,wy,ww,wh = sender.getPosSize()
        fontlistBreakingPoint = 260
        fontTable = self.fontNameColumn.tableView()
        infoNameColumn = self.infoPane.box.list.getNSTableView().tableColumns()[0]

        itemSize = self.toolsPane.toolbar.itemSize
        self.toolsPane.toolbar.setPosSize((x,y,ww-2*p,itemSize))
        if self.fontNameColumn is not None:
            if ww <= fontlistBreakingPoint:
                self.glyphExampleColumn.setResizable_(True)
                self.glyphExampleColumn.setMaxWidth_(200)
                self.glyphExampleColumn.setMinWidth_(40)

                self.fontNameColumn.setHidden_(True)
                infoNameColumn.setHidden_(True)
                bigRowHeight = 70
                fontTable.setRowHeight_(bigRowHeight)
                fontTable.sizeToFit()
            else:
                self.glyphExampleColumn.setResizable_(False)
                self.glyphExampleColumn.setMaxWidth_(70)
                self.glyphExampleColumn.setMinWidth_(70)
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

        return True



    # ---------------------
    # Actions
    # ---------------------
    def loadInfo(self):
        path = self.designspace.path
        items = [
            dict(name="path", value=path),
            dict(name="number of masters", value=len(self.designspace.fontMasters)),
            dict(name="full compatibility", value="<not implemented>"),
            ]

        self.infoPane.box.list.set(items)

    def prepareFontItems(self, designSpaceMasters):
        items = []
        for item in designSpaceMasters:

            item["glyphExample"] = GlyphCellFactory(item["font"][self.glyphExampleName], 100, 100,bufferPercent=.01)
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
        try:
            self.designspace = MasterToolsProcessor()
            # self.designspace.useVarlib = True
            self.designspace.read(path)
            self.designspace.loadFonts()
            self.loadInfo()
            print("designspace imported")
            return True
        except:
            print("designspace wasn't imported")
            return False



def test():
    DesignSpaceWindow()

if __name__ == '__main__':
    test()
