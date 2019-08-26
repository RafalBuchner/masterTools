from vanilla import *
class ActionPopUpButtonDemo(object):
    def __init__(self):
        self.w = Window((100, 40))
        items = [
                dict(title="first", callback=self.firstCallback),
                dict(title="second", callback=self.secondCallback),
                dict(title="third", items=[
                        dict(title="sub first", callback=self.subFirstCallback)
                    ])
            ]
        self.w.actionPopUpButton = ActionButton((10, 10, 30, 20),
                              items,
                              )
        self.w.open()
    def firstCallback(self, sender):
        print("first")
    def secondCallback(self, sender):
        print("second")
    def subFirstCallback(self, sender):
        print("sub first")
ActionPopUpButtonDemo()
