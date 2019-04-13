# coding: utf-8
from vanilla import HUDFloatingWindow, FloatingWindow, TextBox, Sheet, Window, Group, GradientButton

#rom AppKit import NSColor, NSFont, NSTableHeaderCell, NSMakeRect, NSRectFill, NSSize, NSArrayController, NSTableViewLastColumnOnlyAutoresizingStyle, NSLeftTextAlignment, NSRightTextAlignment, NSCenterTextAlignment, NSJustifiedTextAlignment, NSNaturalTextAlignment
import AppKit
from defconAppKit.windows.baseWindow import BaseWindowController
from masterTools.UI.objcBase import *

from vanilla.vanillaList import *
from vanilla.vanillaBase import _breakCycles, _calcFrame, _setAttr, _delAttr, _flipFrame, \
        VanillaCallbackWrapper, VanillaError, VanillaBaseControl, osVersionCurrent, osVersion10_7, osVersion10_10
from vanilla.py23 import python_method

_textAlignmentMap = {
    "left":AppKit.NSLeftTextAlignment,
    "right":AppKit.NSRightTextAlignment,
    "center":AppKit.NSCenterTextAlignment,
    "justified":AppKit.NSJustifiedTextAlignment,
    "natural":AppKit.NSNaturalTextAlignment,
}
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
    def __init__(self, posSize, parentWindow, title="", minSize=None, maxSize=None, textured=False,
                autosaveName=None, closable=True, miniaturizable=True, initiallyVisible=True,
                fullScreenMode=None, titleVisible=True, fullSizeContentView=False, screen=None):
        if isinstance(parentWindow, Window):
            parentWindow = parentWindow._window
        self.parentWindow = parentWindow
        textured = bool(parentWindow.styleMask() & AppKit.NSTexturedBackgroundWindowMask)

        mask = AppKit.NSHUDWindowMask | AppKit.NSUtilityWindowMask | AppKit.NSTitledWindowMask | AppKit.NSBorderlessWindowMask
        if closable:
            mask = mask | AppKit.NSClosableWindowMask
        if miniaturizable:
            mask = mask | AppKit.NSMiniaturizableWindowMask
        if minSize or maxSize:
            mask = mask | AppKit.NSResizableWindowMask
        if textured:
            mask = mask | AppKit.NSTexturedBackgroundWindowMask
        if fullSizeContentView and osVersionCurrent >= osVersion10_10:
            mask = mask | AppKit.NSFullSizeContentViewWindowMask
        # start the window
        ## too magical?
        if len(posSize) == 2:
            l = t = 100
            w, h = posSize
            cascade = True
        else:
            l, t, w, h = posSize
            cascade = False
        if screen is None:
            screen = AppKit.NSScreen.mainScreen()
        frame = _calcFrame(screen.visibleFrame(), ((l, t), (w, h)))
        self._window = self.nsWindowClass.alloc().initWithContentRect_styleMask_backing_defer_screen_(
            frame, mask, AppKit.NSBackingStoreBuffered, False, screen)
        if autosaveName is not None:
            # This also sets the window frame if it was previously stored.
            # Make sure we do this before cascading.
            self._window.setFrameAutosaveName_(autosaveName)
        if cascade:
            self._cascade()
        if minSize is not None:
            self._window.setMinSize_(minSize)
        if maxSize is not None:
            self._window.setMaxSize_(maxSize)
        self._window.setTitle_(title)
        self._window.setLevel_(self.nsWindowLevel)
        self._window.setReleasedWhenClosed_(False)
        self._window.setDelegate_(self)
        self._bindings = {}
        self._initiallyVisible = initiallyVisible
        # full screen mode
        if osVersionCurrent >= osVersion10_7:
            if fullScreenMode is None:
                pass
            elif fullScreenMode == "primary":
                self._window.setCollectionBehavior_(AppKit.NSWindowCollectionBehaviorFullScreenPrimary)
            elif fullScreenMode == "auxiliary":
                self._window.setCollectionBehavior_(AppKit.NSWindowCollectionBehaviorFullScreenAuxiliary)
        # titlebar visibility
        if osVersionCurrent >= osVersion10_10:
            if not titleVisible:
                self._window.setTitleVisibility_(AppKit.NSWindowTitleHidden)
            else:
                self._window.setTitleVisibility_(AppKit.NSWindowTitleVisible)
        # full size content view
        if fullSizeContentView and osVersionCurrent >= osVersion10_10:
            self._window.setTitlebarAppearsTransparent_(True)

class MTDialog(BaseWindowController):
    txtH = 17
    btnH = 24
    padding = (10,10,10)
    window = HUDFloatingWindow
    settingsSheet = MTSheet
    toolbar = MTToolbar






class MTlist(List):
    """
    sepcialCellDescription = {column index:AppKit.NSTableCell subclass}
    """
    def __init__(self, posSize, items, dataSource=None, columnDescriptions=None, showColumnTitles=True,
                selectionCallback=None, doubleClickCallback=None, editCallback=None, menuCallback=None,
                enableDelete=False, enableTypingSensitivity=False,
                allowsMultipleSelection=True, allowsEmptySelection=True,
                allowsSorting=True,
                drawVerticalLines=False, drawHorizontalLines=False,
                autohidesScrollers=True, drawFocusRing=False, rowHeight=17.0,
                drawBorders=False,
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
        self._tableView.setColumnAutoresizingStyle_(AppKit.NSTableViewLastColumnOnlyAutoresizingStyle)

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

            if transparentBackground:
                    column.headerCell().setDrawsBackground_(False)
                    column.headerCell().setBackgroundColor_(NSColor.clearColor())
            # set the data cell
            if cell is None:
                cell = column.dataCell()
                cell.setDrawsBackground_(False)
                cell.setStringValue_("")  # cells have weird default values
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
                color =AppKit.NSColor.colorWithCalibratedRed_green_blue_alpha_(*textColor)
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

########
# test #
########

if __name__ == "__main__":
    pass

    # from vanilla import HUDFloatingWindow, Window
    # class ListDemo(object):
    #     def __init__(self):
    #
    #         font =AppKit.NSFont.systemFontOfSize_(17)
    #         self.w = Window((200, 200))
    #         columnDescriptions = [{"title": "One","font":NSFont.systemFontOfSize_(12)}, {"title": "Two","textColor":((0,1,0,1)),"font":("AndaleMono",12),"alignment":"right"}]
    #         self.w.myList = MTlist((20, 20, -20, -40),
    #                      [{"One": "A", "Two": "a"}, {"One": "B", "Two": "b"}],
    #                      columnDescriptions=columnDescriptions,
    #                      rowHeight=30, font=font,transparentBackground=True,
    #                      selectionCallback=self.selectionCallback)
    #         #self.w.txt = TMTextBox((20,-40,-20,20), text="Test 12344012", alignment="natural", selectable=False, sizeStyle="regular", fontAttr=("AndaleMono",17), color=(1,0,0,1))
    #
    #
    #         self.w.open()
    #     def selectionCallback(self, sender):
    #         #help(self.w.myList.getNSTableView())
    #         #print(self.w.myList.getNSTableView().setSelectionHighlightStyle_(1))
    #         self.w.myList.getNSTableView().setSelectionHighlightStyle_(500)
    #         #self.w.myList.getNSTableView().setAllowsColumnSelection_(True)
    #         pass
    #         # size =AppKit.NSSize(100, 200)
    #         # help(size)
    #         # self.w.myList.getNSTableView().setIntercellSpacing_(size)
    #
    # ListDemo()
    #
