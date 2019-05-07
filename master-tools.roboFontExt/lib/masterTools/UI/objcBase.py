# coding: utf-8
from AppKit import NSColor, NSFont, NSTableHeaderCell, NSMakeRect, NSRectFill, NSTextFieldCell, NSSize, NSMenuItem, NSBox, NSPanel, NSWindow, NSObject
from vanilla import Group, TextBox, Slider
from vanilla.vanillaList import VanillaTableViewSubclass
from mojo.events import publishEvent

class MTTableDelegate(NSObject):
    def tableView_willDisplayCell_forTableColumn_row_(self, tableView, cell, column, rowId):
        info = tableView.getTableCellHighlight()
        ids = (tableView.tableColumns().index(column),rowId)
        target_rgbValues = info.get(ids)
        if target_rgbValues is not None:
            cell.setDrawsBackground_(True)

            if len(target_rgbValues) == 3:
                r,g,b = target_rgbValues
                target_backgroundColor = NSColor.colorWithCalibratedRed_green_blue_alpha_(r,g,b,1)
            elif len(target_rgbValues) == 4:
                r,g,b,a = target_rgbValues
                target_backgroundColor = NSColor.colorWithCalibratedRed_green_blue_alpha_(r,g,b,a)
        else:  cell.setDrawsBackground_(False)

        target_columnId, target_rowId = ids
        if rowId == target_rowId and tableView.tableColumns()[target_columnId].identifier() == column.identifier() and target_rgbValues is not None:
            cell.setBackgroundStyle_(0)
            cell.setBackgroundColor_(target_backgroundColor)

class MTTableViewSubclass(VanillaTableViewSubclass):
    def init(self):
        super(MTTableViewSubclass, self).init()
        self._tableCellHighlight = {}
        return self

    def getTableCellHighlight(self):
        return self._tableCellHighlight

    def setTableCellHighlight_(self, info):
        """
        :param info: list(dict(rowId,columnId,backgroundColor))
        :return: None
        """

        self._tableCellHighlight = info

class MTSliderAxisMenuItem(NSMenuItem):

    def __new__(cls, *arg, **kwargs):
        return cls.alloc().initWithTitle_action_keyEquivalent_("doodle.axisSpace", None, "")

    def __init__(self, axisname, value, minValue, maxValue, callback):
        self.axisname = axisname
        self._callback = callback
        self._menuGroup = Group((0, 0, 0, 0))

        self._menuGroup.text = TextBox((20, 0, 100, 18), axisname, sizeStyle="small")
        self._menuGroup.slider = Slider((20, 16, 200, 18), value=value, minValue=minValue, maxValue=maxValue, sizeStyle="small", callback=self.sliderCallback_, tickMarkCount=11, stopOnTickMarks=True)
        self._menuGroup.slider.axisName = axisname
        self._view = self._menuGroup.getNSView()
        self._view.setFrame_(NSMakeRect(0, 0, 250, 35))

        self.setView_(self._view)

    def getSlider(self):
        return self._menuGroup.slider

    def sliderCallback_(self, sender):
        if self._callback:
            self._callback(sender)

# go to objc folder
class MTInteractiveSBox(NSBox):
    count = 0
    rightMenu = None

    def worksWhenModal(self):
        return True

    def menuForEvent_(self,event):

        origin = self.frameOrigin()
        point = event.locationInWindow()
        x,y = (point.x-origin.x,point.y-origin.y)
        publishEvent("MT.prevRightMouseDown", cursorpos=(x,y))

        if self.rightMenu is not None:
            return self.rightMenu

    def mouseDragged_(self,event):
        # # print(event)
        windowView = self.window().contentView()
        origin = self.convertPoint_toView_(self.frameOrigin(), windowView)
        w,h = (self.frameSize().width,self.frameSize().height)
        point = event.locationInWindow()
        rect = NSMakeRect(origin.x,origin.y,w,h)
        self.count += 1

        if self.mouse_inRect_(point,rect):
            point = event.locationInWindow()
            x,y = (point.x-origin.x,point.y-origin.y)
            publishEvent("MT.prevMouseDragged", cursorpos=(x,y),framesize=(w,h))


# go to objcBase
class MTPanel(NSPanel):
    count = 0
    def mouseDragged_(self,event):
        # # print(event)
        origin = self.frameOrigin()
        w,h = (self.frame().size.width,self.frame().size.height)
        point = event.locationInWindow()
        rect = NSMakeRect(origin.x,origin.y,w,h)
        self.count += 1

        point = event.locationInWindow()
        x,y = (point.x-origin.x,point.y-origin.y)

# go to objcBase
class MTWindow(NSWindow):
    def validateMenuItem_(self, menuItem):
        return True

def setTemplateImages(*imageObjects):
    for img in imageObjects:
        img.setTemplate_(True)

class TransparentNSTableHeaderCell(NSTableHeaderCell):
    def drawWithFrame_inView_(self, frame, view):

        NSColor.clearColor().set()
        NSRectFill(frame)

        extra_space = view.tableView().intercellSpacing().width + 2
        padded_frame = NSMakeRect(frame.origin.x + (extra_space / 2),
             frame.origin.y+5, frame.size.width - extra_space,
             frame.size.height)

        NSTableHeaderCell.drawInteriorWithFrame_inView_(self, padded_frame, view)

class MTVerticallyCenteredTextFieldCell(NSTextFieldCell):

    mIsEditingOrSelecting = False

    def drawingRectForBounds_(self, theRect):
        # Get the parent's idea of where we should draw
        newRect = super().drawingRectForBounds_(theRect)

        # When the text field is being
        # edited or selected, we have to turn off the magic because it screws up
        # the configuration of the field editor.  We sneak around this by
        # intercepting selectWithFrame and editWithFrame and sneaking a
        # reduced, centered rect in at the last minute.
        if self.mIsEditingOrSelecting is False:
            # Get our ideal size of current text
            textSize = self.cellSizeForBounds_(theRect)

            # Center in the proposed rect
            heightDelta = newRect.size.height - textSize.height
            if heightDelta > 0:
                newRect.size.height -= heightDelta
                newRect.origin.y += heightDelta/2

        return newRect

    def selectWithFrame_inView_editor_delegate_start_length_(self, aRect, controlView, textObj, anObject,selStart,selLength):
        aRect = self.drawingRectForBounds_(aRect)
        self.mIsEditingOrSelecting = True
        super().selectWithFrame_inView_editor_delegate_start_length_( aRect, controlView, textObj, anObject,selStart,selLength)
        self.mIsEditingOrSelecting = False

    def editWithFrame_inView_editor_delegate_event_(self, aRect, controlView, textObj, anObject,theEvent):
        aRect = self.drawingRectForBounds_(aRect)
        self.mIsEditingOrSelecting = True
        super().editWithFrame_inView_editor_delegate_event_( aRect, controlView, textObj, anObject,theEvent)
        self.mIsEditingOrSelecting = False


if __name__=="__main__":
    pass
