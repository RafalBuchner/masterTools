from AppKit import NSColor, NSViewBoundsDidChangeNotification, NSNotificationCenter
import AppKit
from pprint import pprint
from copy import deepcopy
import objc
from masterTools.UI.glyphCellFactory import GlyphCellFactoryWithNotDef
from masterTools.UI.vanillaSubClasses import MTDialog, MTList, MTVerticallyCenteredTextFieldCell
from vanilla import *
from masterTools.UI.settings import Settings

uiSettingsController = Settings()
glyphColor = uiSettingsController.getGlyphColor_forCurrentMode()
genericListPboardType = "genericListPboardType"
class DragAndDropReorder(MTDialog):
    def __init__(self, possize, designspace):
        self.designspace = designspace
        self.draggedItemInfo = None
        self.glyphName = 'A'


        self.listview = Group(possize)
        self.listview = self.listview
        self.setItems()

    def getView(self):
        return self.listview
        
    def updateGlyph(self, name):
        self.glyphName = name
        self.setItems()

    def setItems(self):
        maxNumOfComponents = self.designspace.getMaxNumberOfComponentsInDesignSpace_forGlyph(self.glyphName)
        maxNumOfContours = self.designspace.getMaxNumberOfContoursInDesignSpace_forGlyph(self.glyphName)
        maxNumOfElements = maxNumOfComponents + maxNumOfContours
        columnWidth = 100
        
        # self.items = [[] for i in range(maxNumOfElements)]
        contoursItems   = [[] for i in range(maxNumOfContours)]
        componentsItems = [[] for i in range(maxNumOfComponents)]
        descriptionItems = []
        for masterItem in self.designspace.fontMasters:
            font = masterItem['font']
            glyph = font[self.glyphName]
            descriptionItems += [dict(fontName=masterItem['fontname'])]

            for _element in [glyph.contours, glyph.components]:
                if _element == glyph.contours:
                    _element_name = 'contours'
                    items = contoursItems
                else: 
                    _element_name = 'components'
                    items = componentsItems
                for index in range(len(_element)):
                    selectionWithColor = {
                            _element_name:{index:NSColor.cyanColor()}
                        }
                    if index < len(_element):
                        items[index] += [dict(glyph=GlyphCellFactoryWithNotDef(
                                glyph.name,glyph.font, 240, 240, glyphColor=glyphColor, selectionWithColor=selectionWithColor),fontName=masterItem['fontname'], 
                                glyphObj=glyph
                                )]

        fontListColumnDescriptions = [
            dict(title=f"glyph",cell=ImageListCell(), width=columnWidth) 

        ]
        descriptionColumnDescriptions = [dict(title='fontName',cell=MTVerticallyCenteredTextFieldCell.alloc().init())]
        x,y,p = self.padding
        descriptionView = Group((0,0,-0,-0))
        descriptionView.title = TextBox((x,y,-p,self.txtH),f"master",alignment='center')
        y += self.txtH + p

        descriptionView.list = MTList((x,y,-0,-0),
                    descriptionItems,
                    rowHeight=columnWidth,
                    showColumnTitles=False,
                    columnDescriptions=descriptionColumnDescriptions,
                    transparentBackground=True
            )
        descriptionView.list.setSelection([])

        self.paneDescriptors=[dict(view=descriptionView,identifier=f"description")]
        setattr(self, f'obj_description', descriptionView)

        selfWindowDropSettings = dict(type=genericListPboardType,
                        allowDropOnRow=True,
                        allowDropBetweenRows=False,
                        operation=AppKit.NSDragOperationCopy,
                        callback=self.selfDropCallback)
        dragSettings = dict(type=genericListPboardType,
                        allowDropOnRow=True,
                        allowDropBetweenRows=False,
                        callback=self.dragCallback)
        for i in range(maxNumOfContours):
            y = 10
            
            _items = contoursItems[i]
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
                        dragSettings=dragSettings, 
                        selectionCallback=self.selectionCallback,
                )
            _id = f"index_{i}"
            view.list.setSelection([])
            view.list.id = i
            view.list.elementType = 'contour'
            setattr(self, f'obj_{_id}', view)

            self.paneDescriptors += [dict(view=view,identifier=_id)]

        for i in range(maxNumOfComponents):
            y = 10
            
            _items = componentsItems[i]
            view = Group((0,0,-0,-0))
            view.title = TextBox((x,y,-p,self.txtH),f"component {i}",alignment='center')
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
                        dragSettings=dragSettings, 
                        selectionCallback=self.selectionCallback,
                )
            _id = f"component_{i}"
            view.list.setSelection([])
            view.list.id = i
            view.list.elementType = 'component'
            setattr(self, f'obj_{_id}', view)

            self.paneDescriptors += [dict(view=view,identifier=_id)]

        if hasattr(self.listview, 'columns'):
            del self.listview.columns
        self.listview.columns = SplitView((0, 0, -0, -0), 
            self.paneDescriptors, dividerStyle='thin'
            )

    def selectionCallback(self, sender):
        selectionID = sender.getSelection()
        if selectionID != []:
            selectionID = selectionID[0]
            for item in self.paneDescriptors:
                identifier = item['identifier']
                view = getattr(self, f'obj_{identifier}')
                if view.list == sender:
                    continue
                view.list.setSelection([selectionID])


    def dragCallback(self, sender, indexes):
        self.draggedItemInfo = (sender.elementType, sender.id, sender.get()[indexes[0]] ,sender.get()[indexes[0]]['fontName'], indexes)

    def selfDropCallback(self, sender, dropInfo):
        isProposal = dropInfo["isProposal"]
        if not isProposal:
            if self.draggedItemInfo is not None:
                _elementType, _id, draggedItem, fontname, draggedIndexes = self.draggedItemInfo
                if _elementType != sender.elementType:
                    return True
                draggedList = getattr(self, f'obj_index_{_id}').list
                draggedItems = draggedList.get()

                dropItems = sender.get()
                dropId = sender.id
                itemToReplace = None
                for item in dropItems:
                    if item['fontName'] == fontname:
                        itemToReplace = item
                dropItemsNew = []
                for i,item in enumerate(dropItems):
                    if i not in draggedIndexes:
                        dropItemsNew += [item]
                    else:
                        dropItemsNew += [draggedItem]
                draggedItemsNew = []
                sender.set(dropItemsNew)
                for i,item in enumerate(draggedItems):
                    if i not in draggedIndexes:
                        draggedItemsNew += [item]
                    else:
                        draggedItemsNew += [itemToReplace]

                # print(draggedItemsNew)
                draggedList.set(draggedItemsNew)
                # dropItems.replace
                self.draggedItemInfo = None

            # test = []
            # for item in self.draggedItems:
            #     if item not in test:
            #         test += [item]
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