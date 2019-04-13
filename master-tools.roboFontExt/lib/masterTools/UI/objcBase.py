# coding: utf-8
from AppKit import NSColor, NSFont, NSTableHeaderCell, NSMakeRect, NSRectFill, NSTextFieldCell, NSSize


class TransparentNSTableHeaderCell(NSTableHeaderCell):
    def drawWithFrame_inView_(self, frame, view):

        NSColor.clearColor().set()
        NSRectFill(frame)

        extra_space = view.tableView().intercellSpacing().width + 2
        padded_frame = NSMakeRect(frame.origin.x + (extra_space / 2),
             frame.origin.y+5, frame.size.width - extra_space,
             frame.size.height)

        NSTableHeaderCell.drawInteriorWithFrame_inView_(self, padded_frame, view)

class VerticallyCenteredTextFieldCell(NSTextFieldCell):

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
    VerticallyCenteredTextFieldCell.alloc().init()
