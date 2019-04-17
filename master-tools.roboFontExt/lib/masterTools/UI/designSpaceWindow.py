#import importlib
from vanilla import HelpButton, Sheet, Button, Group, Box, SplitView, TextBox, Window, CheckBoxListCell, GradientButton, SquareButton, ImageButton, ImageView, ImageListCell
from masterTools.misc.masterSwitcher import switchMasterTo, resizeOpenedFont
from masterTools.misc import MasterToolsProcessor
from masterTools.UI.objcBase import VerticallyCenteredTextFieldCell
from masterTools.UI.vanillaSubClasses import MTlist, MTDialog, MTInteractiveSBox

from masterTools.UI.glyphCellFactory import *
from defconAppKit.windows.baseWindow import BaseWindowController
from masterTools import copy2clip
from mojo.UI import AccordionView
from mojo.extensions import ExtensionBundle
import os, AppKit,      sys
from mojo.events import addObserver, removeObserver, publishEvent
from mojo.roboFont import AllFonts, CurrentFont, OpenFont, OpenWindow
from mojo.events import addObserver


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




class DesignSpaceWindow(MTDialog, BaseWindowController):
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
        "path","number of masters","full compatibility","axes"
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
        autosaveName = "com.rafalbuchner.designspacewindow")#, autosaveName = "com.rafalbuchner.masterTools.panes"




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
            dict(label="prev",
                view=self.glyphPane,
                identifier="glyphPane",
                size=self.glyphHeight,
                minSize=self.glyphHeight,
                #maxSize=self.glyphHeight,
                canCollapse=False,
                resizeFlexibility=False),
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
        self.glyphHeight = 200


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
            self.settings.close()
        x,y,p = self.padding
        self.settings = self.settingsSheet((600, 700), self.w,title="settings")
        y += 20
        self.settings.closeSettingsBtn = GradientButton((-p-self.btnH, y, self.btnH, self.btnH),imageObject=closeIcon, bordered=False, callback=_close)
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
        self.glyphPane.prev.mainWindowClose()

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

from mojo.glyphPreview import GlyphPreview
from mojo.roboFont import OpenWindow, RGlyph, CurrentGlyph
from fontTools.designspaceLib import InstanceDescriptor
from mojo.UI import MenuBuilder
from vanilla import Slider
from vanilla.vanillaBase import VanillaCallbackWrapper
from copy import deepcopy

class MTGlyphPreview(Box):
    """
        NSView that shows the preview of the glyph in the given designspace
        
        !!! It doesn't know what to do if there is incompatibility !
    """
    nsBoxClass = MTInteractiveSBox
    check = "•"
    roundLocations = True
    def __init__(self, posSize, title=None):
        super(MTGlyphPreview, self).__init__(posSize, title=title)
        self.glyphName = None
        self.rightClickGroup = []
        self.windowAxes = {"horizontal axis":None, "vertical axis":None,}
        self.currentLoc = {}
        
        self.glyphView = GlyphPreview((0,0,-0,-0))
        self.horAxisInfo = self.textBox((8,-20,0,12),f'horizontal axis',alignment="left",textColor=(0,1,0,1),fontSize=("Monaco",10))
        rotate = self.horAxisInfo.getNSTextField().setFrameRotation_(90)

        self.verAxisInfo = self.textBox((10,-12,0,12),f'vertical axis',alignment="left",textColor=(0,1,0,1),fontSize=("Monaco",10))
        self.interpolationProblemMessage = self.textBox((0,0,0,0),f'<Possible Interpolation Error>',alignment="center",textColor=(1,0,0,1),fontSize=("Monaco",10))
        self.interpolationProblemMessage.show(False)
        addObserver(self, "locChangedCallback","MT.prevMouseDragged")
        addObserver(self, "rightMouseDownCallback","MT.prevRightMouseDown")
        addObserver(self, "currentGlyphChangedCallback", "currentGlyphChanged")
        
    def updateInfo(self):
        
        horValue = self.currentLoc.get(self.windowAxes["horizontal axis"])
        self.horAxisInfo.set(f'{self.windowAxes["horizontal axis"]} - {horValue}')
        verValue = self.currentLoc.get(self.windowAxes["vertical axis"])
        self.verAxisInfo.set(f'{self.windowAxes["vertical axis"]} - {verValue}')
        
    def textBox(self,posSize,title,textColor,fontSize,alignment="left"):
        color =AppKit.NSColor.colorWithCalibratedRed_green_blue_alpha_(*textColor)
        font = AppKit.NSFont.fontWithName_size_(*fontSize)
        #cell.setTextColor_(color)
        txtBox = TextBox(posSize,title,alignment=alignment)
        nsTextFiled = txtBox.getNSTextField()
        nsTextFiled.setTextColor_(color)
        nsTextFiled.setFont_(font)
        return txtBox
        
    def currentGlyphChangedCallback(self,sender):
        self.glyphName = CurrentGlyph().name
        self.interpolationProblemMessage.setTitle(f'glyph "{self.glyphName}" <Possible Interpolation Error>')
        
        self.setGlyph(self.glyphName, self.currentLoc)
        
    def rightMouseDownCallback(self,sender):
        for l in self.rightClickGroup:
            l.setSelection([])

    def menuItemCallback(self,sender):
        if sender.getSelection():
            curr_axisList = sender
            if curr_axisList.axis == "vertical axis":
                second_axisList = self.rightClickGroup[0]
            elif curr_axisList.axis == "horizontal axis":
                second_axisList = self.rightClickGroup[1]
            rowIndex = curr_axisList.getSelection()[0]
            allitems = curr_axisList.get()
            item = allitems[rowIndex]
            # popupbutton imitation:
            itemChoosenAxisName = item[curr_axisList.axis]
            if item["set"] != self.check:                
                item["set"] = self.check
                self.windowAxes[curr_axisList.axis] = itemChoosenAxisName
            else:
                item["set"] = ""
                self.windowAxes[curr_axisList.axis] = None
            for other_index,other_item in enumerate(allitems):
                if other_index == rowIndex:
                    continue
                other_item["set"] = ""
            
            
            secondAllItems = second_axisList.get()

            # if the same axis tag is choosen in the second list
            # deselect it from the second list
            for item in secondAllItems:
                if item['set'] == self.check:
                    self.windowAxes[second_axisList.axis] = item[second_axisList.axis]
                if item[second_axisList.axis] == itemChoosenAxisName:
                    item['set'] = ""
                    self.windowAxes[second_axisList.axis]=None
            curr_axisList.set(allitems)
            second_axisList.setSelection([])
            curr_axisList.setSelection([])
            self.updateInfo()

    
    def sCB(self, sender):
        print(">HURRA<")
        
    def _setContextualMenu(self):
        y,x,p = (10,10,10)
        axisPopUpMenuItem = AppKit.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("axisPopUp", '', '')
        columnDescriptions_hor = [{"title": "set","width":8},{"title": "horizontal axis"}]
        columnDescriptions_ver = [{"title": "set","width":8},{"title": "vertical axis"}]
        # group is going to be a container for
        # two lists, that will behave 
        # like a popup buttons
        group = Group((0,0,220+3*p,100)) 
        group._list_hor = MTlist((x, y, 110, -p), self.axesList_hor, columnDescriptions=columnDescriptions_hor,doubleClickCallback=self.menuItemCallback,transparentBackground=True,)
        group._list_hor.axis = "horizontal axis"
        group._list_ver = MTlist((x+110+p, y, 110, -p), self.axesList_ver, columnDescriptions=columnDescriptions_ver,doubleClickCallback=self.menuItemCallback,transparentBackground=True,)
        group._list_ver.axis = "vertical axis"
        self.rightClickGroup = [group._list_hor,group._list_ver]
        # setting the appearance of the lists
        for l in self.rightClickGroup:
            l.setSelection([])
            NSTable = l.getNSTableView()
            NSTable.setSelectionHighlightStyle_(1)
            NSTable.tableColumns()[0].headerCell().setTitle_("")
        sliderItems = []
                
        items =  []
        for i,item in enumerate(self.axesList_ver):
            axis_name = item["vertical axis"]
            sliderMenuItem = AppKit.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(axis_name, '', '')
            
            minValue = self.axesInfo[axis_name]["minimum"]
            maxValue = self.axesInfo[axis_name]["maximum"]
            value = self.currentLoc[axis_name]
            group2 = Group((0,0,220+3*p,50))
            group2.title = TextBox((10,0,-0,20),axis_name)
            group2.slider = Slider((10, 20, 220+p, 30), callback=self.sCB,minValue=minValue,maxValue=maxValue,value=value) 
            group2.slider.axis = axis_name
            view = group2.getNSView()
            view.setFrame_(((0, 100), (220+3*p, 50)))
            sliderMenuItem.setView_(view)
            items.append(sliderMenuItem)
                            
        # Building NSMenu
        view = group.getNSView()
        axisPopUpMenuItem.setView_(view)
        
        builder = MenuBuilder([
             axisPopUpMenuItem,
         ]+[item for item in items])
        
        self.menu = builder.getMenu()
        self.menu.setMinimumWidth_(120)
        self.menu.setAutoenablesItems_(False)
        view.setFrame_(((0, 0), (220+3*p, 2*p+23+23*len(self.axesList_hor))))
        # # viewsliders.setFrame_(((0, 0), (220+3*p, sliderGroupHeight)))
        sliderMenuItem.setTarget_(self.getNSBox())
        self.getNSBox().rightMenu = self.menu


    def setDesignSpace(self, designspace):
        
        self.designspace = designspace
        self.glyphName = "a"
        self.axesInfo = {}
        for axisInfo in self.designspace.getSerializedAxes():
            info = {}
            info["minimum"] = axisInfo["minimum"]
            info["maximum"] = axisInfo["maximum"]
            info["range"] = axisInfo["maximum"]-axisInfo["minimum"]
            
            self.axesInfo[axisInfo['name']] = info
        if designspace.findDefault() is not None:
            self.currentLoc = designspace.findDefault().location
            self.lastAllLocations = deepcopy(designspace.findDefault().location)
        else:
            self.currentLoc = {}
            self.lastAllLocations = {name:0 for name in self.axesInfo.keys()}
        self.axesList_hor = []
        self.axesList_ver = []
        for axis in designspace.getSerializedAxes():
            self.axesList_hor += [{"set":"","horizontal axis":axis['name']}]
            self.axesList_ver += [{"set":"","vertical axis":axis['name']}]
        self.getDefaultLoc = 0 # later replace it with special finding default loc
        self._setContextualMenu()
        self.setGlyph(self.glyphName,self.currentLoc)

    def setGlyph(self,name, loc=None):
        if loc is None or loc == {}:
            return
        if  name is None:
            return
        for axisname in loc:
            self.lastAllLocations[axisname] = loc[axisname]

        self.updateInfo()
        self.glyphView.setGlyph(self._getInterpolation(name,self.lastAllLocations))
                
    def locChangedCallback(self, data):
        x,y = data["cursorpos"]
        w,h = (self.getNSBox().frameSize().width,self.getNSBox().frameSize().height)
        horizontalAxisName = self.windowAxes["horizontal axis"]
        verticalAxisName   = self.windowAxes["vertical axis"]
        horizontalAxisValue = None
        verticalAxisValue = None
        currentLoc = {}
        
        if horizontalAxisName is not None:
            axis_info = self.axesInfo[horizontalAxisName]
            horizontalAxisValue = axis_info["minimum"] + x/w * axis_info["range"]
            if self.roundLocations: horizontalAxisValue = round(horizontalAxisValue)
            
            
        if verticalAxisName is not None:
            axis_info = self.axesInfo[verticalAxisName]
            verticalAxisValue = axis_info["minimum"] + y/h * axis_info["range"]
            if self.roundLocations: verticalAxisValue = round(verticalAxisValue)
        if horizontalAxisValue is not None:
            currentLoc[horizontalAxisName] = horizontalAxisValue
        if verticalAxisValue is not None:
            currentLoc[verticalAxisName] = verticalAxisValue

        self.currentLoc = currentLoc
        self.setGlyph(self.glyphName, self.currentLoc)

    def _getInterpolation(self,name,loc):
        instance = None
        for master in self.designspace.fontMasters:
            if loc == master['designSpacePosition']:
                instance = master['font']
                break

        if instance is None:            
            instanceDescriptor = InstanceDescriptor()
            instanceDescriptor.location = loc

            instance = self.designspace.makeInstance(instanceDescriptor, glyphNames=[name],pairs=[], bend=True)
        if name in instance.keys():
            self.interpolationProblemMessage.show(False)
            self.glyphView.show(True)
            return instance[name]
        else:
            self.interpolationProblemMessage.show(True)
            self.glyphView.show(False)
            return instance[name]

    def mainWindowClose(self):
        removeObserver(self, "MT.prevMouseDragged")
        removeObserver(self, "MT.prevRightMouseDown")
        removeObserver(self, "currentGlyphChanged")



def test():
    import os
    path = "path/to/some/design/space"
    o = OpenWindow(DesignSpaceWindow)#, path)

if __name__ == '__main__':
    test()
