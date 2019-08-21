from vanilla import Window, List, Popover, TextBox

class PopoverExample:

    def __init__(self):
        self.w = Window((120, 120))
        self.w.list = List((0, 0, -0, -0),
                ['eggs', 'bacon', 'ham', 'beans'],
                selectionCallback=self.showPopoverCallback)
        self.w.open()

    def showPopoverCallback(self, sender):
        selection = sender.getSelection()
        if not selection:
            return
        index = sender.getSelection()[0]
        relativeRect = sender.getNSTableView().rectOfRow_(index)
        pop = Popover((140, 180))
        pop.text = TextBox((10, 10, -10, -10), 'spam '*20)
        pop.open(parentView=sender, preferredEdge='right', relativeRect=relativeRect)

PopoverExample()