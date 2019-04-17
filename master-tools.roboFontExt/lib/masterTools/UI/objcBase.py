# coding: utf-8
from AppKit import NSColor, NSFont, NSTableHeaderCell, NSMakeRect, NSRectFill, NSTextFieldCell, NSSize, NSMenuItem

class MTSliderAxisMenuItem(NSMenuItem):

    def __new__(cls, *arg, **kwargs):
        return cls.alloc().initWithTitle_action_keyEquivalent_("doodle.lineSpace", None, "")

    def __init__(self, value, callback):
        self._callback = callback
        self._menuGroup = Group((0, 0, 0, 0))

        self._menuGroup.text = TextBox((20, 0, 100, 18), "Line Space:", sizeStyle="small")
        self._menuGroup.slider = Slider((20, 16, 120, 18), value=value, minValue=0, maxValue=400, sizeStyle="small", callback=self.sliderCallback_)

        self._view = self._menuGroup.getNSView()
        self._view.setFrame_(AppKit.NSMakeRect(0, 0, 150, 35))

        self.setView_(self._view)

    def sliderCallback_(self, sender):
        if self._callback:
            self._callback(sender)

# go to objc folder
class MTInteractiveSBox(AppKit.NSBox):
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
        origin = self.frameOrigin()
        w,h = (self.frameSize().width,self.frameSize().height)
        point = event.locationInWindow()
        rect = AppKit.NSMakeRect(origin.x,origin.y,w,h)
        self.count += 1
        if self.mouse_inRect_(point,rect):
            point = event.locationInWindow()
            x,y = (point.x-origin.x,point.y-origin.y)
            publishEvent("MT.prevMouseDragged", cursorpos=(x,y))


# go to objcBase
class MTPanel(AppKit.NSPanel):
    count = 0
    def mouseDragged_(self,event):
        # # print(event)
        origin = self.frameOrigin()
        w,h = (self.frame().size.width,self.frame().size.height)
        point = event.locationInWindow()
        rect = AppKit.NSMakeRect(origin.x,origin.y,w,h)
        self.count += 1

        point = event.locationInWindow()
        x,y = (point.x-origin.x,point.y-origin.y)

# go to objcBase
class MTWindow(AppKit.NSWindow):
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
