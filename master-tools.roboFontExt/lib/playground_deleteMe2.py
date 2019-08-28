from AppKit import NSColor, NSViewBoundsDidChangeNotification, NSNotificationCenter
import AppKit
from pprint import pprint
import objc
from masterTools.helpers.solveCompatibilityOrderManually import ManualCompatibilityHelper
from masterTools.misc.MasterToolsProcessor import MasterToolsProcessor
from masterTools.UI.glyphCellFactory import GlyphCellFactoryWithNotDef
from masterTools.UI.vanillaSubClasses import MTDialog, MTList, MTVerticallyCenteredTextFieldCell
from vanilla import *
from masterTools.UI.settings import Settings
uiSettingsController = Settings()
glyphColor = uiSettingsController.getGlyphColor_forCurrentMode()
genericListPboardType = "genericListPboardType"
class DragAndDropReorder(MTDialog):

    def __init__(self, designspace):
        self.designspace = designspace
        self.glyphName = 'K'


        self.listview = Group((0,0,-0,-0))
        self.w = HUDFloatingWindow((400, 700),minSize=(400, 700))
        self.w.listview = self.listview
        self.setItems()

        self.w.open()

    def updateGlyph(self, name):
        self.glyphName = name
        self.setItems()

    def setItems(self):
        maxNumOfComponents = self.designspace.getMaxNumberOfComponentsInDesignSpace_forGlyph(self.glyphName)
        maxNumOfContours = self.designspace.getMaxNumberOfContoursInDesignSpace_forGlyph(self.glyphName)
        maxNumOfElements = maxNumOfContours
        if maxNumOfComponents > maxNumOfContours:
            maxNumOfElements = maxNumOfComponents
        columnWidth = 100
        
        items = [[] for i in range(maxNumOfElements)]

        for masterItem in self.designspace.fontMasters:
            font = masterItem['font']
            glyph = font[self.glyphName]
            for _element in [glyph.contours, glyph.components]:
                if _element == glyph.contours:
                    _element_name = 'contours'
                else: _element_name = 'components'
                for index in range(len(_element)):
                    selectionWithColor = {
                            _element_name:{index:NSColor.cyanColor()}
                        }
                    if index < len(_element):
                        items[index] += [dict(glyph=GlyphCellFactoryWithNotDef(
                                glyph.name,glyph.font, 240, 240, glyphColor=glyphColor, selectionWithColor=selectionWithColor,
                                ))]

        fontListColumnDescriptions = [
            dict(title=f"glyph",cell=ImageListCell(), width=columnWidth) 

        ]
        descriptionColumnDescriptions = [dict(title='fontName',cell=MTVerticallyCenteredTextFieldCell.alloc().init())]
        x,y,p = self.padding
        descriptionView = Group((0,0,-0,-0))
        descriptionView.title = TextBox((x,y,-p,self.txtH),f"master",alignment='center')
        y += self.txtH + p
        descriptionView.list = MTList((x,y,-0,-0),[dict(fontName=item['fontname']) for item in self.designspace.fontMasters],rowHeight=columnWidth,showColumnTitles=False,columnDescriptions=descriptionColumnDescriptions,transparentBackground=True)
        descriptionView.list.setSelection([])

        self.paneDescriptors=[dict(view=descriptionView,identifier=f"description")]
        # Doesn't work :(
        # descriptionView.list.getNSScrollView().contentView().setPostsBoundsChangedNotifications_(1)
        # self.notifiactionCenter = NSNotificationCenter.defaultCenter()
        # self.viewBoundsDidChange_selector = objc.selector(self.viewBoundsDidChange_,signature=b'v@:')
        # self.notifiactionCenter.addObserver_selector_name_object_(
        #     self,
        #     b'viewBoundsDidChange:',
        #     # self.viewBoundsDidChange_selector,
        #     NSViewBoundsDidChangeNotification,
        #     descriptionView.list.getNSScrollView().contentView())

        selfWindowDropSettings = dict(type=genericListPboardType,
                        allowDropOnRow=True,
                        allowDropBetweenRows=False,
                        operation=AppKit.NSDragOperationCopy,
                        callback=self.selfDropCallback)
        dragSettings = dict(type=genericListPboardType,
                        allowDropOnRow=True,
                        allowDropBetweenRows=False,
                        callback=self.dragCallback)
        for i in range(maxNumOfElements):
            y = 10
            
            _items = items[i]
            view = Group((0,0,-0,-0))
            view.title = TextBox((x,y,-p,self.txtH),f"index {i}",alignment='center')
            y += self.txtH + p
            view.list = MTList(
                (0,y,-0,-0),
                _items,
                columnDescriptions=fontListColumnDescriptions,
                rowHeight=columnWidth,
                showColumnTitles=False,
                allowsMultipleSelection=False,
                transparentBackground=True,
                selfWindowDropSettings=selfWindowDropSettings,
                dragSettings=dragSettings)
            view.list.setSelection([])
            self.paneDescriptors += [dict(view=view,identifier=f"index_{i}")]
            # Doesn't work :(
            # view.list.getNSScrollView().contentView().setPostsBoundsChangedNotifications_(1)
            # self.notifiactionCenter.addObserver_selector_name_object_(
            #     self,
            #     b'viewBoundsDidChange:',
            #     AppKit.NSViewBoundsDidChangeNotification,
            #     view.list.getNSScrollView().contentView())
        if hasattr(self.w.listview, 'columns'):
            del self.w.listview.columns
        self.w.listview.columns = SplitView((0, 0, -0, -0), self.paneDescriptors)


    # def viewBoundsDidChange_(self, bounds):
    # # Doesn't work :(
    # this method supposed to make sure that all scrolls are at the same line
    #     pass
    def dragCallback(self, sender, indexes):
        # print('dragging…', indexes)

        self.draggedItems = [sender.get()[i] for i in indexes]
        print(self.draggedItems)
    def selfDropCallback(self, sender, dropInfo):
        isProposal = dropInfo["isProposal"]
        if not isProposal:
            key = sender.get()[dropInfo['rowIndex']]
            test = []
            for item in self.draggedItems:
                if item not in test:
                    test += [item]
            print(test)
            return True
        return True
def main():
    dsPath = '../../test_designSpace/mutatorSans-master/MutatorSans.designspace'
    designspace = MasterToolsProcessor()
    designspace.read(dsPath)
    designspace.loadFonts()
    DragAndDropReorder(designspace)


if __name__ == '__main__':
    main()