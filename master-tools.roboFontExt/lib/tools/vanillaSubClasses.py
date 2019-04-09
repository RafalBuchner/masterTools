# coding: utf-8

from vanilla.vanillaList import *
from AppKit import NSFormatter, NSColor

class CompatibilityList(List):
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
                dragSettings=None,
                mainWindow=None):
        if items is not None and dataSource is not None:
            raise VanillaError("can't pass both items and dataSource arguments")

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
            items = NSMutableArray.arrayWithArray_(items)
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
                lineType = NSTableViewSolidVerticalGridLineMask | NSTableViewSolidHorizontalGridLineMask
            elif drawVerticalLines:
                lineType = NSTableViewSolidVerticalGridLineMask
            else:
                lineType = NSTableViewSolidHorizontalGridLineMask
            self._tableView.setGridStyleMask_(lineType)
        # set up the columns. also make a flag that will be used
        # when unwrapping items.
        self._orderedColumnIdentifiers = []
        self._typingSensitiveColumn = 0
        if not columnDescriptions:
            self._makeColumnWithoutColumnDescriptions()
            self._itemsWereDict = False
        else:
            self._makeColumnsWithColumnDescriptions(columnDescriptions, mainWindow, drawBorders, transparentBackground)
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
            self._arrayController.addObserver_forKeyPath_options_context_(self._selectionObserver, "selectionIndexes", NSKeyValueObservingOptionNew, 0)
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
        notLocal = NSDragOperationNone
        if otherApplicationDropSettings is not None:
            notLocal = otherApplicationDropSettings.get("operation", NSDragOperationCopy)
        self._tableView.setDraggingSourceOperationMask_forLocal_(notLocal, False)
        local = NSDragOperationNone
        for settings in (selfDropSettings, selfDocumentDropSettings, selfApplicationDropSettings):
            if settings is None:
                continue
            local = settings.get("operation", NSDragOperationCopy)
        self._tableView.setDraggingSourceOperationMask_forLocal_(local, True)

        if transparentBackground:
            self._tableView.setBackgroundColor_(NSColor.clearColor())
            self._tableView.headerView().setBackgroundColor_(NSColor.clearColor())
        # deletingBorders
        if drawBorders is False:
            self._tableView.enclosingScrollView().setBorderType_(0)
        # set the drag data
        self._dragSettings = dragSettings


    def _makeColumnsWithColumnDescriptions(self, columnDescriptions, mainWindow, drawBorders, transparentBackground):
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
            keyPath = "arrangedObjects.%s" % key
            # check for typing sensitivity.
            if data.get("typingSensitive"):
                self._typingSensitiveColumn = columnIndex
            # instantiate the column.
            column = NSTableColumn.alloc().initWithIdentifier_(key)
            self._orderedColumnIdentifiers.append(key)
            # set the width resizing mask

            mask = NSTableColumnNoResizing
            column.setResizingMask_(mask)
            # set the header cell
            column.headerCell().setTitle_(title)
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
                    self._arrayController.addObserver_forKeyPath_options_context_(self._editObserver, keyPath, NSKeyValueObservingOptionNew, 0)
            else:
                column.setEditable_(False)
            # finally, add the column to the table view
            self._tableView.addTableColumn_(column)
            width = column.headerCell().attributedStringValue().size().width
            if transparentBackground:
                column.headerCell().setBackgroundColor_(NSColor.clearColor())
            # do this *after* adding the column to the table, or the first column
            # will have the wrong width (at least on 10.3)
            column.setWidth_(width+10)
            column.setMinWidth_(width+10)
            column.setMaxWidth_(width+10)
            tableWidth += width+14
        # force the columns to adjust their widths if possible. (needed in 10.10)
        x,y,w,h = mainWindow.window().getPosSize()

        if tableWidth+210+18 < w-25:
            x,y,w,h =  self.getPosSize()
            self.setPosSize((x,y,tableWidth,h))
        self._tableView.sizeToFit()
        self.tableWidth = tableWidth
