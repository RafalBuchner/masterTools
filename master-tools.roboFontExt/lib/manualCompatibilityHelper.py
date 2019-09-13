from dragAndDropReorder import DragAndDropReorder
from selectOrder import SelectOrder
from vanilla import *
from masterTools.UI.vanillaSubClasses import MTFloatingDialog
from defconAppKit.windows.baseWindow import BaseWindowController
from masterTools.UI.settings import Settings
uiSettingsControler = Settings()

class ManualCompatiblityHelper(MTFloatingDialog, BaseWindowController):
    title = 'Manual Compatibility Helper'
    key = ''.join(title)
    id = f"com.rafalbuchner.ProblemSolvingTools.{key}"
    #
    winMinSize = (700,370)
    winMaxSize = (6000,5000)
    txtH = 17
    btnH = 24
    padding = 10
    def __init__(self, designspace):
        dragAndDropReorder = DragAndDropReorder((0,0,-0,-0),designspace)
        selectOrder = SelectOrder((0,0,-0,-0),designspace)

        self.uiSettings = uiSettingsControler.getDict()
        self.w = self.window(self.winMinSize, minSize=self.winMinSize, title=self.title ,maxSize=self.winMaxSize,autosaveName=self.id,
            darkMode=self.uiSettings["darkMode"])
        self.w.tabs = Tabs((10, 10, -10, -10), ["ordering pointer", "ordering table"],sizeStyle='mini')
        tab1 = self.w.tabs[0]
        tab1.view = dragAndDropReorder.getView()
        tab2 = self.w.tabs[1]
        tab2.view = selectOrder.getView()

        self.w.open()

    def windowResizeCallback(self, sender):
        DragAndDropReorder.windowResizeCallback(sender)
