# coding: utf-8
from vanilla import HUDFloatingWindow, FloatingWindow, TextBox, Sheet, Window, Group, GradientButton

import AppKit
from masterTools.UI.objcBase import *
from mojo.events import addObserver, removeObserver, publishEvent
from vanilla.vanillaList import *
from vanilla.vanillaBase import  VanillaCallbackWrapper, VanillaError, osVersionCurrent, osVersion10_14
from mojo.glyphPreview import GlyphPreview
from mojo.roboFont import OpenWindow, RGlyph, CurrentGlyph
from fontTools.designspaceLib import InstanceDescriptor
from mojo.UI import MenuBuilder
from vanilla import Box, HUDFloatingWindow
from copy import deepcopy
_textAlignmentMap = {
    "left":AppKit.NSLeftTextAlignment,
    "right":AppKit.NSRightTextAlignment,
    "center":AppKit.NSCenterTextAlignment,
    "justified":AppKit.NSJustifiedTextAlignment,
    "natural":AppKit.NSNaturalTextAlignment,
}

class MTGlyphPreview(Box):
    """
        NSView that shows the preview of the glyph in the given designspace

        !!! It doesn't know what to do if there is incompatibility !
    """
    nsBoxClass = MTInteractiveSBox
    check = "•"
    roundLocations = True
    def __init__(self, posSize, title=None):
        # print("MTGlyphPreview-22.04.19 A")
        super(MTGlyphPreview, self).__init__(posSize, title=title)
        self.glyphName = None
        self.rightClickGroup = []
        self.windowAxes = {"horizontal axis":None, "vertical axis":None,}
        self.currentLoc = {}

        self.glyphView = GlyphPreview((0,0,-0,-0))
        self.horAxisInfo = self.textBox((8,-20,0,12),f'horizontal axis',alignment="left",textColor=AppKit.NSColor.systemGreenColor(),fontSize=("Monaco",10))
        rotate = self.horAxisInfo.getNSTextField().setFrameRotation_(90)

        self.verAxisInfo = self.textBox((10,-12,0,12),f'vertical axis',alignment="left",textColor=AppKit.NSColor.systemGreenColor(),fontSize=("Monaco",10))
        self.interpolationProblemMessageTxt = f'<Possible Interpolation Error>'
        self.interpolationProblemMessage = self.textBox((0,0,0,0),self.interpolationProblemMessageTxt,alignment="center",textColor=(1,0,0,1),fontSize=("Monaco",10))
        self.interpolationProblemMessage.show(False)

        addObserver(self, "mouseDragged","MT.prevMouseDragged")
        addObserver(self, "rightMouseDownCallback","MT.prevRightMouseDown")
        addObserver(self, "currentGlyphChangedCallback", "currentGlyphChanged")

    def updateInfo(self):

        horValue = self.currentLoc.get(self.windowAxes["horizontal axis"])
        self.horAxisInfo.set(f'{self.windowAxes["horizontal axis"]} - {horValue}')
        verValue = self.currentLoc.get(self.windowAxes["vertical axis"])
        self.verAxisInfo.set(f'{self.windowAxes["vertical axis"]} - {verValue}')

    def textBox(self,posSize,title,textColor,fontSize,alignment="left"):
        if isinstance(textColor,tuple):
            color =AppKit.NSColor.colorWithCalibratedRed_green_blue_alpha_(*textColor)
        else:
            color = textColor
        font = AppKit.NSFont.fontWithName_size_(*fontSize)
        #cell.setTextColor_(color)
        txtBox = TextBox(posSize,title,alignment=alignment)
        nsTextFiled = txtBox.getNSTextField()
        nsTextFiled.setTextColor_(color)
        nsTextFiled.setFont_(font)
        return txtBox

    def currentGlyphChangedCallback(self,sender):
        if CurrentGlyph() is not None:
            self.glyphName = CurrentGlyph().name
            self.interpolationProblemMessageTxt = f'glyph "{self.glyphName}" <Possible Interpolation Error>'

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
            secondAllItems = second_axisList.get()
            secondItem = secondAllItems[rowIndex]
            item = allitems[rowIndex]

            if secondItem[second_axisList.axis] == item[curr_axisList.axis] and secondItem["set"] == self.check:
                secondItem["set"] = ""
                self.windowAxes[second_axisList.axis] = None
                curr_axisList.set(secondAllItems)

            # popupbutton imitation:
            itemChoosenAxisName = item[curr_axisList.axis]
            if item["set"] != self.check:
                item["set"] = self.check
                self.windowAxes[curr_axisList.axis] = itemChoosenAxisName
            else:
                item["set"] = ""
                self.windowAxes[curr_axisList.axis] = None

            for other_item in allitems:
                if item != other_item:
                    other_item["set"] = ""
            curr_axisList.set(allitems)
            second_axisList.setSelection([])
            curr_axisList.setSelection([])
            self.updateInfo()

    def sliderCallback(self, sender):
        self.currentLoc[sender.axisName] = round(sender.get())

        self.setGlyph(self.glyphName,self.currentLoc)
        self.updateInfo()

    def _setContextualMenu(self):
        y,x,p = (10,10,10)
        axisPopUpMenuItem = AppKit.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("axisPopUp", '', '')
        columnDescriptions_hor = [{"title": "set","width":8},{"title": "horizontal axis"}]
        columnDescriptions_ver = [{"title": "set","width":8},{"title": "vertical axis"}]
        # group is going to be a container for
        # two lists, that will behave
        # like a popup buttons
        group = Group((0,0,220+3*p,100))
        group._list_hor = MTList((x, y, 110, -p), self.axesList_hor, columnDescriptions=columnDescriptions_hor,doubleClickCallback=self.menuItemCallback,transparentBackground=True,)
        group._list_hor.axis = "horizontal axis"
        group._list_ver = MTList((x+110+p, y, 110, -p), self.axesList_ver, columnDescriptions=columnDescriptions_ver,doubleClickCallback=self.menuItemCallback,transparentBackground=True,)
        group._list_ver.axis = "vertical axis"
        self.rightClickGroup = [group._list_hor,group._list_ver]
        # setting the appearance of the lists
        for l in self.rightClickGroup:
            l.setSelection([])
            NSTable = l.getNSTableView()
            NSTable.setSelectionHighlightStyle_(1)
            NSTable.tableColumns()[0].headerCell().setTitle_("")
        sliderItems = []

        self.sliderItems =  []
        for i,item in enumerate(self.axesList_ver):
            axis_name = item["vertical axis"]
            minValue = self.axesInfo[axis_name]["minimum"]
            maxValue = self.axesInfo[axis_name]["maximum"]
            value = self.currentLoc[axis_name]
            sliderItem = MTSliderAxisMenuItem(axis_name, value, minValue, maxValue, self.sliderCallback)
            self.sliderItems.append(sliderItem)

        # Building NSMenu
        view = group.getNSView()
        axisPopUpMenuItem.setView_(view)

        builder = MenuBuilder([
             axisPopUpMenuItem,
         ]+[item for item in self.sliderItems])

        self.menu = builder.getMenu()
        self.menu.setMinimumWidth_(120)
        self.menu.setAutoenablesItems_(False)
        view.setFrame_(((0, 0), (220+3*p, 2*p+23+23*len(self.axesList_hor))))
        self.getNSBox().rightMenu = self.menu


    def setDesignSpace(self, designspace):

        self.designspace = designspace
        self.glyphName = "A"
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

    def _updateSliders(self):
        if hasattr(self, "sliderItems"):
            for item in self.sliderItems:
                slider = item.getSlider()
                value = self.lastAllLocations[slider.axisName]
                slider.set(value)

    def mouseDragged(self, data):
        _x,_y,_w,_h = self.getPosSize()
        x,y = data["cursorpos"]
        w,h = data["framesize"]
        w,h = (w+_w, h+_h) ## hardcoded, still didn't figured out
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
        self._updateSliders()


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
            self.interpolationProblemMessage.set(self.interpolationProblemMessageTxt)
            self.glyphView.show(False)
            return instance[name]

    def mainWindowClose(self):
        removeObserver(self, "MT.prevMouseDragged")
        removeObserver(self, "MT.prevRightMouseDown")
        removeObserver(self, "currentGlyphChanged")

class MTToolbar(Group):
    """
        items = [{
            dict(objname="objname",
            imageObject=imageObject,
            toolTip="toolTip",
            callback=callback)
            }]
    """
    def __init__(self, pos, items, itemSize, padding=0):


        x,y=pos
        w = len(items)*itemSize+(len(items)-1)*padding
        posSize = (x,y,w,itemSize)
        super().__init__(posSize)

        self.toolNames = []
        self.itemSize = itemSize
        self.padding = padding
        x = 0
        for item in items:
            posSize = (x,0,itemSize,itemSize)
            self.toolNames += [item["objname"]]

            toolbarItemObj = self.ToolbarItem(
                posSize,
                imageObject=item["imageObject"],
                toolTip=item["toolTip"],
                callback=item["callback"])
            setattr(self,item["objname"],toolbarItemObj)
            x += itemSize + padding
        self.len = len(items)

    def setPosSize(self, posSize):
        x,y,w,h = posSize
        oldx,oldy,oldw,oldh = self.getPosSize()
        standardWidth = self.len * self.itemSize + self.padding * self.len-1

        super().setPosSize((oldx,oldy,w,h))
        if w > standardWidth:
            for i, objName in enumerate(self.toolNames):
                toolbarItem = getattr(self, objName)
                item_x,item_y,item_w,item_h = toolbarItem.getPosSize()
                factor = w/standardWidth
                item_x = (w-standardWidth)/2+ i*item_w
                toolbarItem.setPosSize((item_x,item_y,item_w,item_h))
        elif w < standardWidth:
            for i, objName in enumerate(self.toolNames):
                toolbarItem = getattr(self, objName)
                item_x,item_y,item_w,item_h = toolbarItem.getPosSize()
                factor = w/standardWidth
                item_h = factor*self.itemSize
                item_w = w/self.len
                item_y = self.itemSize/2-item_h/2
                item_x = i*item_w

                toolbarItem.setPosSize((item_x,item_y,item_w,item_h))
                toolbarItem.getNSButton().setImageScaling_(factor)



    def ToolbarItem(self, posSize, imageObject=None, toolTip=None, callback=None):
        toolbaritem = GradientButton(posSize,imageObject=imageObject, bordered=False, callback=self.toolbarItemStatusUpdateCB)
        if toolTip is not None:
            toolbaritem.getNSButton().setToolTip_(toolTip)
        toolbaritem.status = False
        if callback is not None:
            toolbaritem.callback = callback
        return toolbaritem

    def toolbarItemStatusUpdateCB(self, sender):
        # creating checkbox functionality of btns in Tools Group
        buttonObject = sender.getNSButton()
        if sender.status:
            sender.status = False
            buttonObject.setBordered_(False)
        else:
            sender.status = True
            buttonObject.setBordered_(True)

        sender.callback(sender) # calling custom toggle callback

class MTSheet(Sheet):
    pass
    # def __init__(self, posSize, parentWindow, title="", minSize=None, maxSize=None, textured=False,
    #             autosaveName=None, closable=True, miniaturizable=True, initiallyVisible=True,
    #             fullScreenMode=None, titleVisible=True, fullSizeContentView=False, screen=None):
    #     if isinstance(parentWindow, Window):
    #         parentWindow = parentWindow._window
    #     self.parentWindow = parentWindow
    #     textured = bool(parentWindow.styleMask() & AppKit.NSTexturedBackgroundWindowMask)
    #
    #     mask = AppKit.NSHUDWindowMask | AppKit.NSUtilityWindowMask | AppKit.NSBorderlessWindowMask
    #     if closable:
    #         mask = mask | AppKit.NSClosableWindowMask
    #     if miniaturizable:
    #         mask = mask | AppKit.NSMiniaturizableWindowMask
    #     if minSize or maxSize:
    #         mask = mask | AppKit.NSResizableWindowMask
    #     if textured:
    #         mask = mask | AppKit.NSTexturedBackgroundWindowMask
    #     if fullSizeContentView and osVersionCurrent >= osVersion10_10:
    #         mask = mask | AppKit.NSFullSizeContentViewWindowMask
    #     # start the window
    #     ## too magical?
    #     if len(posSize) == 2:
    #         l = t = 100
    #         w, h = posSize
    #         cascade = True
    #     else:
    #         l, t, w, h = posSize
    #         cascade = False
    #     if screen is None:
    #         screen = AppKit.NSScreen.mainScreen()
    #     frame = _calcFrame(screen.visibleFrame(), ((l, t), (w, h)))
    #     self._window = self.nsWindowClass.alloc().initWithContentRect_styleMask_backing_defer_screen_(
    #         frame, mask, AppKit.NSBackingStoreBuffered, False, screen)
    #     if autosaveName is not None:
    #         # This also sets the window frame if it was previously stored.
    #         # Make sure we do this before cascading.
    #         self._window.setFrameAutosaveName_(autosaveName)
    #     if cascade:
    #         self._cascade()
    #     if minSize is not None:
    #         self._window.setMinSize_(minSize)
    #     if maxSize is not None:
    #         self._window.setMaxSize_(maxSize)
    #     self._window.setTitle_(title)
    #     self._window.setLevel_(self.nsWindowLevel)
    #     self._window.setReleasedWhenClosed_(False)
    #     self._window.setDelegate_(self)
    #     self._bindings = {}
    #     self._initiallyVisible = initiallyVisible
    #     # full screen mode
    #     if osVersionCurrent >= osVersion10_7:
    #         if fullScreenMode is None:
    #             pass
    #         elif fullScreenMode == "primary":
    #             self._window.setCollectionBehavior_(AppKit.NSWindowCollectionBehaviorFullScreenPrimary)
    #         elif fullScreenMode == "auxiliary":
    #             self._window.setCollectionBehavior_(AppKit.NSWindowCollectionBehaviorFullScreenAuxiliary)
    #     # titlebar visibility
    #     if osVersionCurrent >= osVersion10_10:
    #         if not titleVisible:
    #             self._window.setTitleVisibility_(AppKit.NSWindowTitleHidden)
    #         else:
    #             self._window.setTitleVisibility_(AppKit.NSWindowTitleVisible)
    #     # full size content view
    #     self._window.setTitleVisibility_(False)
    #     self._window.setTitlebarAppearsTransparent_(True)
    #
    #     self.title = TextBox((0,2,-0,17),title,alignment="center",sizeStyle="small")



class MTWindowWrapper(Window):
    #appearance = AppKit.NSAppearance.appearanceNamed_(AppKit.NSAppearanceNameAqua)
    nsWindowClass = MTWindow

    nsWindowStyleMask = AppKit.NSHUDWindowMask | AppKit.NSUtilityWindowMask | AppKit.NSTitledWindowMask | AppKit.NSBorderlessWindowMask
    if osVersionCurrent >= osVersion10_14:
        appearanceDark = AppKit.NSAppearance.appearanceNamed_(AppKit.NSAppearanceNameDarkAqua)
        appearanceLight = AppKit.NSAppearance.appearanceNamed_(AppKit.NSAppearanceNameAqua)


    def __init__(self, posSize, title="", minSize=None, maxSize=None, textured=False,
                autosaveName=None, closable=True, miniaturizable=True, initiallyVisible=True,
                fullScreenMode=None, titleVisible=True, fullSizeContentView=False, screen=None, darkMode=False):
        super().__init__(posSize, title=title, minSize=minSize, maxSize=maxSize, textured=textured,
                    autosaveName=autosaveName, closable=closable, miniaturizable=miniaturizable, initiallyVisible=initiallyVisible,
                    fullScreenMode=fullScreenMode, titleVisible=titleVisible, fullSizeContentView=fullSizeContentView, screen=screen)
        if osVersionCurrent >= osVersion10_14:
            if darkMode:
                self._window.setAppearance_(self.appearanceDark)
            else:
                self._window.setAppearance_(self.appearanceLight)

class MTFloatingWindowWrapper(Window):
    #appearance = AppKit.NSAppearance.appearanceNamed_(AppKit.NSAppearanceNameAqua)
    # nsWindowClass = MTWindowWrapper
    nsWindowClass = AppKit.NSPanel
    nsWindowLevel = AppKit.NSFloatingWindowLevel

    nsWindowStyleMask = AppKit.NSHUDWindowMask | AppKit.NSUtilityWindowMask | AppKit.NSTitledWindowMask | AppKit.NSBorderlessWindowMask
    if osVersionCurrent >= osVersion10_14:
        appearanceDark = AppKit.NSAppearance.appearanceNamed_(AppKit.NSAppearanceNameDarkAqua)
        appearanceLight = AppKit.NSAppearance.appearanceNamed_(AppKit.NSAppearanceNameAqua)


    def __init__(self, posSize, title="", minSize=None, maxSize=None, textured=False,
                autosaveName=None, closable=True, miniaturizable=True, initiallyVisible=True,
                fullScreenMode=None, titleVisible=True, fullSizeContentView=False, screen=None, darkMode=False, noTitleBar=False):
        super().__init__(posSize, title=title, minSize=minSize, maxSize=maxSize, textured=textured,
                    autosaveName=autosaveName, closable=closable, miniaturizable=miniaturizable, initiallyVisible=initiallyVisible,
                    fullScreenMode=fullScreenMode, titleVisible=titleVisible, fullSizeContentView=fullSizeContentView, screen=screen)
        self._window.setBecomesKeyOnlyIfNeeded_(True)
        if noTitleBar:
            self._window.setTitlebarAppearsTransparent_(True)
            self._window.setTitleVisibility_(0)
        if osVersionCurrent >= osVersion10_14:
            if darkMode:
                self._window.setAppearance_(self.appearanceDark)
            else:
                self._window.setAppearance_(self.appearanceLight)
    def show(self):
        """
        Show the window if it is hidden.
        """
        # don't make key!
        self._window.orderFront_(None)


class MTDialog(object):
    """
    in subclass you have to describe self.w as instance of MTWindowWrapper (you can use class attr window for it)
    """
    txtH = 17
    btnH = 24
    padding = (10,10,10)
    window = MTWindowWrapper
    settingsSheet = MTSheet
    toolbar = MTToolbar
class MTFloatingDialog(object):
    """
    in subclass you have to describe self.w as instance of MTWindowWrapper (you can use class attr window for it)
    """
    txtH = 17
    btnH = 24
    padding = (10,10,10)
    window = MTFloatingWindowWrapper
    settingsSheet = MTSheet
    toolbar = MTToolbar


class MTList(List):
    """
    sepcialCellDescription = {column index:AppKit.NSTableCell subclass}
    """
    nsTableViewClass = MTTableViewSubclass
    delegateClass = MTTableDelegate

    def __init__(self, posSize, items, dataSource=None, columnDescriptions=None, showColumnTitles=True,
                selectionCallback=None, doubleClickCallback=None, editCallback=None, menuCallback=None,
                enableDelete=False, enableTypingSensitivity=False,
                allowsMultipleSelection=True, allowsEmptySelection=True,
                allowsSorting=True,
                drawVerticalLines=False, drawHorizontalLines=False,
                autohidesScrollers=True, drawFocusRing=False, rowHeight=17.0,
                drawBorders=False,
                allowSelection=True,
                transparentBackground=False,
                selfDropSettings=None,
                selfWindowDropSettings=None,
                selfDocumentDropSettings=None,
                selfApplicationDropSettings=None,
                otherApplicationDropSettings=None,
                widthIsHeader=False,
                dragSettings=None,
                mainWindow=None,
                font=None,
                ):
        if items is not None and dataSource is not None:
            raise VanillaError("can't pass both items and dataSource arguments")
        self._rowNum = len(items)
        self._posSize = posSize
        self._enableDelete = enableDelete
        self._nsObject = getNSSubclass(self.nsScrollViewClass)(self)
        self._nsObject.setAutohidesScrollers_(autohidesScrollers)
        self._nsObject.setHasHorizontalScroller_(True)
        self._nsObject.setHasVerticalScroller_(True)
        self._nsObject.setBorderType_(NSBezelBorder)
        self._nsObject.setDrawsBackground_(False)

        self._setAutosizingFromPosSize(posSize)
        self._allowsSorting = allowsSorting
        # add a table view to the scroll view
        self._tableView = getNSSubclass(self.nsTableViewClass)(self)
        self._nsObject.setDocumentView_(self._tableView)
        # set up an observer that will be called by the bindings when a cell is edited
        self._editCallback = editCallback
        self._editObserver = self.nsArrayControllerObserverClass.alloc().init()

        if editCallback is not None:
            self._editObserver._targetMethod = self._edit # circular reference to be killed in _breakCycles
        if items is not None:
            # wrap all the items
            items = [self._wrapItem(item) for item in items]
            items =AppKit.NSMutableArray.arrayWithArray_(items)
            # set up an array controller
            self._arrayController = self.nsArrayControllerClass.alloc().initWithContent_(items)
            self._arrayController.setSelectsInsertedObjects_(False)
            self._arrayController.setAvoidsEmptySelection_(not allowsEmptySelection)
        else:
            self._arrayController = dataSource
        self._tableView.setDataSource_(self._arrayController)
        # hide the header
        if not showColumnTitles or not columnDescriptions:
            self._tableView.setHeaderView_(None)
            self._tableView.setCornerView_(None)
        # set the table attributes
        self._tableView.setUsesAlternatingRowBackgroundColors_(False)
        #if not drawFocusRing:
        self._tableView.setFocusRingType_(NSFocusRingTypeNone)
        self._tableView.setRowHeight_(rowHeight)
        self._tableView.setAllowsEmptySelection_(allowsEmptySelection)
        self._tableView.setAllowsMultipleSelection_(allowsMultipleSelection)
        if drawVerticalLines or drawHorizontalLines:
            if drawVerticalLines and drawHorizontalLines:
                lineType =AppKit.NSTableViewSolidVerticalGridLineMask |AppKit.NSTableViewSolidHorizontalGridLineMask
            elif drawVerticalLines:
                lineType =AppKit.NSTableViewSolidVerticalGridLineMask
            else:
                lineType =AppKit.NSTableViewSolidHorizontalGridLineMask
            self._tableView.setGridStyleMask_(lineType)
        # set up the columns. also make a flag that will be used
        # when unwrapping items.
        self._orderedColumnIdentifiers = []
        self._typingSensitiveColumn = 0
        if not columnDescriptions:
            self._makeColumnWithoutColumnDescriptions()
            self._itemsWereDict = False
        else:
            self._makeColumnsWithColumnDescriptions(columnDescriptions, mainWindow, drawBorders, transparentBackground, font, widthIsHeader)
            self._itemsWereDict = True
        # set some typing sensitivity data
        self._typingSensitive = enableTypingSensitivity
        if enableTypingSensitivity:
            self._lastInputTime = None
            self._typingInput = []
        # set up an observer that will be called by the bindings when the selection changes.
        # this needs to be done ater the items have been added to the table. otherwise,
        # the selection method will be called when the items are added to the table view.
        if selectionCallback is not None:
            self._selectionCallback = selectionCallback
            self._selectionObserver = self.nsArrayControllerObserverClass.alloc().init()
            self._arrayController.addObserver_forKeyPath_options_context_(self._selectionObserver, "selectionIndexes",AppKit.NSKeyValueObservingOptionNew, 0)
            self._selectionObserver._targetMethod = self._selection # circular reference to be killed in _breakCycles
        # set the double click callback the standard way
        if doubleClickCallback is not None:
            self._doubleClickTarget = VanillaCallbackWrapper(doubleClickCallback)
            self._tableView.setTarget_(self._doubleClickTarget)
            self._tableView.setDoubleAction_("action:")
        # store the contextual menu callback
        self._menuCallback = menuCallback
        # set the drop data
        self._selfDropSettings = selfDropSettings
        self._selfWindowDropSettings = selfWindowDropSettings
        self._selfDocumentDropSettings = selfDocumentDropSettings
        self._selfApplicationDropSettings = selfApplicationDropSettings
        self._otherApplicationDropSettings = otherApplicationDropSettings
        allDropTypes = []
        for settings in (selfDropSettings, selfWindowDropSettings, selfDocumentDropSettings, selfApplicationDropSettings, otherApplicationDropSettings):
            if settings is None:
                continue
            dropType = settings["type"]
            allDropTypes.append(dropType)
        self._tableView.registerForDraggedTypes_(allDropTypes)
        # set the default drop operation masks
        notLocal =AppKit.NSDragOperationNone
        if otherApplicationDropSettings is not None:
            notLocal = otherApplicationDropSettings.get("operation",AppKit.NSDragOperationCopy)
        self._tableView.setDraggingSourceOperationMask_forLocal_(notLocal, False)
        local =AppKit.NSDragOperationNone
        for settings in (selfDropSettings, selfDocumentDropSettings, selfApplicationDropSettings):
            if settings is None:
                continue
            local = settings.get("operation",AppKit.NSDragOperationCopy)
        self._tableView.setDraggingSourceOperationMask_forLocal_(local, True)

        if transparentBackground:
            self._tableView.setBackgroundColor_(NSColor.clearColor())
            #self._tableView.headerView().setBackgroundColor_(NSColor.clearColor())
        # deletingBorders
        if drawBorders is False:
            self._tableView.enclosingScrollView().setBorderType_(0)
        # set the drag data
        self._dragSettings = dragSettings

        # set up a delegate class

        self._delegate = self.delegateClass.alloc().initWithSelectionPremission_(allowSelection)
        self._tableView.setDelegate_(self._delegate)
        if not allowSelection:
            self.setSelection([])

    def setCellHighlighting(self, cellDescriptions):
        """
        :param info: {(rowId,columnId)=(rgb||rgba)}
        :return: None
        """

        self._tableView.setTableCellHighlight_(cellDescriptions)

    def _handleColumnWidths(self, columnDescriptions):
        # we also use this opportunity to determine if
        # autoresizing should be set for the table.
        autoResize = True
        for column in columnDescriptions:
            if column.get("width") is not None:
                autoResize = False
                break
        if autoResize:
            self._setColumnAutoresizing()

    def _setColumnAutoresizing(self):
        # self._tableView.setColumnAutoresizingStyle_(AppKit.NSTableViewLastColumnOnlyAutoresizingStyle)
        self._tableView.setColumnAutoresizingStyle_(AppKit.NSTableViewUniformColumnAutoresizingStyle)

    def _makeColumnsWithColumnDescriptions(self, columnDescriptions, mainWindow, drawBorders, transparentBackground, font, widthIsHeader):
        # make sure that the column widths are in the correct format.
        self._handleColumnWidths(columnDescriptions)
        # create each column.
        tableAllowsSorting = self._allowsSorting
        tableWidth = 0
        for columnIndex, data in enumerate(columnDescriptions):

            title = data["title"]
            key = data.get("key", title)
            width = data.get("width")
            minWidth = data.get("minWidth", width)
            maxWidth = data.get("maxWidth", width)
            formatter = data.get("formatter")
            cell = data.get("cell")
            editable = data.get("editable")
            allowsSorting = data.get("allowsSorting", True)
            binding = data.get("binding", "value")
            font = data.get("font")
            textColor = data.get("textColor")
            alignment = data.get("alignment")
            truncateFromStart = data.get("truncateFromStart")
            keyPath = "arrangedObjects.%s" % key
            if font is not None:
                if isinstance(font, tuple):
                    font =AppKit.NSFont.fontWithName_size_(*font)
            # check for typing sensitivity.
            if data.get("typingSensitive"):
                self._typingSensitiveColumn = columnIndex
            # instantiate the column.
            column =AppKit.NSTableColumn.alloc().initWithIdentifier_(key)
            # # #####TEST
            if transparentBackground:
                myHeaderCell = TransparentNSTableHeaderCell.alloc().init()
                column.setHeaderCell_(myHeaderCell)
            # # #####TEST
            self._orderedColumnIdentifiers.append(key)
            # set the width resizing mask
            if width is not None:
                if width == minWidth and width == maxWidth:
                    mask =AppKit.NSTableColumnNoResizing
                else:
                    mask =AppKit.NSTableColumnUserResizingMask |AppKit.NSTableColumnAutoresizingMask
            else:
                mask =AppKit.NSTableColumnUserResizingMask |AppKit.NSTableColumnAutoresizingMask
            column.setResizingMask_(mask)
            # set the header cell

            column.headerCell().setTitle_(title)
            # setting custom font

            if font is not None and self._tableView.headerView() is not None:
                column.headerCell().setFont_(font)
            if truncateFromStart is not None and self._tableView.headerView() is not None:
                if truncateFromStart:
                    if isinstance(column.headerCell(), AppKit.NSTextFieldCell):
                        column.headerCell().setLineBreakMode_(3)

            if transparentBackground:
                    column.headerCell().setDrawsBackground_(False)
                    column.headerCell().setBackgroundColor_(NSColor.clearColor())
            # set the data cell
            if cell is None:
                cell = column.dataCell()
                cell.setDrawsBackground_(False)
                cell.setStringValue_("")  # cells have weird default values
                if truncateFromStart is not None:
                    if truncateFromStart:
                        if isinstance(cell, AppKit.NSTextFieldCell):
                            cell.setLineBreakMode_(3)
            else:
                column.setDataCell_(cell)
            # setting custom font
            if font is not None:
                cell.setFont_(font)

            if alignment is not None:
                cell.setAlignment_(_textAlignmentMap[alignment])

            # assign the formatter
            if formatter is not None:
                cell.setFormatter_(formatter)
            if self._arrayController is not None:
                bindingOptions = None
                if not tableAllowsSorting or not allowsSorting:
                    bindingOptions = {NSCreatesSortDescriptorBindingOption : False}
                # assign the key to the binding
                column.bind_toObject_withKeyPath_options_(binding, self._arrayController, keyPath, bindingOptions)

            # set the editability of the column.
            # if no value was defined in the column data,
            # base the editability on the presence of
            # an edit callback.
            if editable is None and self._editCallback is None:
                editable = False
            elif editable is None and self._editCallback is not None:
                editable = True
            if editable:
                if self._arrayController is not None:
                    self._arrayController.addObserver_forKeyPath_options_context_(self._editObserver, keyPath,AppKit.NSKeyValueObservingOptionNew, 0)
            else:
                column.setEditable_(False)
            # finally, add the column to the table view
            self._tableView.addTableColumn_(column)

            # applying textColor
            if textColor is not None:
                if isinstance(textColor,tuple):
                    color =AppKit.NSColor.colorWithCalibratedRed_green_blue_alpha_(*textColor)
                else:
                    color = textColor
                cell.setTextColor_(color)

            if transparentBackground:
                column.headerCell().setBackgroundColor_(NSColor.clearColor())
            if widthIsHeader:
                width = column.headerCell().attributedStringValue().size().width
                column.setWidth_(width+10)
                column.setMinWidth_(width+10)
                column.setMaxWidth_(width+10)
                tableWidth += width+14
            else:
                if width is not None:
                    # do this *after* adding the column to the table, or the first column
                    # will have the wrong width (at least on 10.3)
                    column.setWidth_(width)
                    column.setMinWidth_(minWidth)
                    column.setMaxWidth_(maxWidth)

        # force the columns to adjust their widths if possible. (needed in 10.10)
        if mainWindow is not None:
            x,y,w,h = mainWindow.window().getPosSize()

            if tableWidth+210+18 < w-25:
                x,y,w,h =  self.getPosSize()
                self.setPosSize((x,y,tableWidth,h))
        self._tableView.sizeToFit()
        self.tableWidth = tableWidth

def TMTextBox(posSize, text="", alignment="natural", selectable=False, sizeStyle="regular", fontAttr=None, color=None):
    txtBox = TextBox(posSize, text, alignment, selectable, sizeStyle)
    if fontAttr is not None:
        if isinstance(fontAttr, tuple):
            fontAttr =AppKit.NSFont.fontWithName_size_(*fontAttr)
        txtBox.getNSTextField().setFont_(fontAttr)
    if color is not None:
        if isinstance(color, tuple):
            color =AppKit.NSColor.colorWithCalibratedRed_green_blue_alpha_(*color)
        txtBox.getNSTextField().setTextColor_(color)

    return txtBox


