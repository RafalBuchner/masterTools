from masterTools.helpers.dragAndDropReorder import DragAndDropReorder
from masterTools.helpers.selectOrder import SelectOrder
from masterTools.misc.eventMonitor import KeyEventMonitor
from vanilla import *
from mojo.events import addObserver, removeObserver
from masterTools.UI.vanillaSubClasses import MTDialog
from defconAppKit.windows.baseWindow import BaseWindowController
from mojo.roboFont import CurrentGlyph, CurrentFont
from masterTools.UI.settings import Settings
uiSettingsControler = Settings()

class ManualCompatiblityHelper(MTDialog, BaseWindowController):
    title = 'Manual Compatibility Helper'
    key = ''.join(title)
    id = f"com.rafalbuchner.ProblemSolvingTools.{key}"
    #
    winMinSize = (500,270)
    winMaxSize = (6000,5000)
    txtH = 17
    btnH = 24
    padding = 10
    def __init__(self, designspace):
        super().__init__()
        self.designspace = designspace
        self.dragAndDropReorder = DragAndDropReorder((0,0,-0,-0),designspace)
        
        self.selectOrder = SelectOrder((0,0,-0,-0),designspace)

        x,y,p = [self.padding] * 3
        glyphname = None
        if CurrentGlyph():
            glyphname = CurrentGlyph().name
        else: glyphname = designspace.getCommonGlyphSet()[0]        

        self.uiSettings = uiSettingsControler.getDict()
        self.w = self.window(self.winMinSize, minSize=self.winMinSize, title=self.title ,maxSize=self.winMaxSize,autosaveName=self.id,
            darkMode=self.uiSettings["darkMode"])
        # self.w.dragAndDropReorder = DragAndDropReorder((0,0,-0,-0),designspace)
        self.w.info = Box((10,10,-10,80))
        self.w.info.glyphnameTxtBox = TextBox((x,y,-p,self.txtH), f'glyph name: {glyphname}')
        self.w.tabs = Tabs((10, 90, -10, -10), [ "order contours",
            # "ordering pointer",
            ],sizeStyle='mini')
        tab1 = self.w.tabs[0]
        tab1.dragAndDropReorderView = self.dragAndDropReorder.getView()
        # tab2 = self.w.tabs[1]
        # tab2.view = self.selectOrder.getView()
        
        self.updateGlyph(glyphname)
        self.dragAndDropReorder.updateGlyph(glyphname)

        self.w.open()
        addObserver(self, 'currentGlyphChangedCallback', 'currentGlyphChanged')
        self.setUpBaseWindowBehavior()
        bindings = {
            (',',):self.changeCurrentGlyphBackward,
            ('.',):self.changeCurrentGlyphForward,
        }
        self.keyEventMonitor = KeyEventMonitor(bindings)
        self.keyEventMonitor.subscribe()



    #  BASE EVENT CONTROLLER BINDINGS  
    def windowSelectCallback(self, sender):
        print('subscribe')
        self.keyEventMonitor.subscribe()

    def windowDeselectCallback(self, sender):
        print('unsubscribe')
        self.keyEventMonitor.unsubscribe()

    def windowCloseCallback(self, sender):
        super().windowCloseCallback(sender)
        removeObserver(self, 'currentGlyphChanged')
        self.keyEventMonitor.unsubscribe()

    # KEY EVENT CONTROLLER BINDINGS
    def changeCurrentGlyphForward(self, keystroke):
        self.changeCurrentGlyph( 1)
    def changeCurrentGlyphBackward(self, keystroke):
        self.changeCurrentGlyph( -1)

    def changeCurrentGlyph(self, step):
        if CurrentFont() is not None and self.currentGlyphName in CurrentFont().glyphOrder:
            glyphOrder = CurrentFont().glyphOrder
        else:
            glyphOrder = self.designspace.getCommonGlyphSet()

        index = glyphOrder.index(self.currentGlyphName)
        if index + step < len(glyphOrder):
            newName = glyphOrder[index + step]
        else:
            newName = glyphOrder[0]
        self.updateGlyph(newName)

    # WINDOW BINDINGS
    def windowResizeCallback(self, sender):
        DragAndDropReorder.windowResizeCallback(sender)

    # DATA CALLBACKS
    def currentGlyphChangedCallback(self, info):
        self.updateGlyph(info['glyph'].name)

    def updateGlyph(self, name):
        self.currentGlyphName = name

        self.dragAndDropReorder.updateGlyph(name)
        self.w.info.glyphnameTxtBox.set(f'glyph name: {name}')

    def __name__(self):
        return self.id
