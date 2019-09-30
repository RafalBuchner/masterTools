from vanilla import Window
from mojo.canvas import Canvas, CanvasGroup
from mojo.drawingTools import rect

class CanvasExample:

    def __init__(self):
        self.w = Window((300, 300), title='Canvas', minSize=(200, 200))
        self.w.canvas = Canvas((0, 0, -0, -0), delegate=self)
        self.w.open()

    def draw(self):
        rect(10, 10, 100, 100)

class CanvasGroupExample:

    def __init__(self):
        self.w = Window((300, 300), title='CanvasGroup', minSize=(200, 200))
        self.w.canvas = CanvasGroup((0, 0, -0, -0), delegate=self)
        self.w.open()

    def draw(self):
        rect(10, 10, 100, 100)

CanvasExample()
CanvasGroupExample()