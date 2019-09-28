# from masterTools.misc.MasterToolsProcessor import MasterToolsProcessor # for testing
from mojo.roboFont import CurrentFont # for testing
from mojo.UI import OpenGlyphWindow # for testing
from mojo.events import addObserver, removeObserver # for testing
import AppKit
from vanilla.vanillaBase import osVersionCurrent, osVersion10_14
from defconAppKit.windows.baseWindow import BaseWindowController
from masterTools.UI.settings import Settings

from masterTools.UI.vanillaSubClasses import MTList,  MTFloatingDialog
from masterTools.UI.objcBase import MTVerticallyCenteredTextFieldCell
from masterTools.UI.glyphCellFactory import GlyphCellFactoryWithNotDef

from defconAppKit.controls.glyphCollectionView import GlyphCollectionView

from vanilla import *
from pprint import pprint
from designspaceProblems import DesignSpaceChecker
from designspaceProblems.problems import DesignSpaceProblem
from random import random

'''
    TODO: if I have bigger clipview than the screen, 
    the scrolling appear. It messes up the popup views
'''

# from mojo.events import addObserver, removeObserver
# from mojo.canvas import CanvasGroup
# from mojo.UI import AllGlyphWindows
# from mojo.roboFont import AllFonts, RGlyph, CurrentGlyph

key = "com.rafalbuchner.MasterTools.IncompatibleGlyphsBrowser"

class IncompatibleGlyphsBrowser(MTFloatingDialog, BaseWindowController):
    id = "com.rafalbuchner.IncompatibleGlyphsBrowser"
    winMinSize = (100,70)
    winMaxSize = (6000,5000)
    txtH = 17
    btnH = 24
    padding = 10

    def __init__(self, designspace, toolBtn):
        self.designspace = designspace

        
        self.isActive = False
        self.toolBtn = toolBtn

    def start(self):
        self.auditList = {}
        self.initUI()
        self.w.open()
        self.addObservers()
        self.isActive = True
        self.w.bind('close', self.closeWindow)


    def finish(self):
        if hasattr(self, "w"):
            if self.w._window is not None:
                self.w.close()
        self.removeObservers()
        self.isActive = False

    def addObservers(self):
        addObserver(self, 'testIncompaibility', 'fontBecameCurrent')

    def removeObservers(self):
        removeObserver(self, 'fontBecameCurrent')

    def initUI(self):
        self.problemChecker = DesignSpaceChecker(self.designspace)


        self.uiSettingsControler = Settings()
        self.uiSettings = self.uiSettingsControler.getDict()
        self.glyphColor = self.uiSettingsControler.getGlyphColor_forCurrentMode()


        x, y, p = self.padding, self.padding, self.padding

        self.w = self.window(self.winMinSize,
        "Incompatible Glyphs Browser",
        minSize=self.winMinSize,
        maxSize=self.winMaxSize,
        autosaveName=self.id,
        darkMode=self.uiSettings["darkMode"],
        closable=True,
        noTitleBar=True)

        # view = Group((0,0,-0,-0))

        self.w.foundTxtBox = TextBox((x,y,-p,self.txtH*2),'')
        self.testIncompaibility()
        y += self.txtH*2 + p
        self.w.view = Group((0,y,-0,-0))
        columnDescriptions = [
                                dict(title='glyph', cell=ImageListCell(),width=100),
                                dict(title='name', cell=MTVerticallyCenteredTextFieldCell.alloc().init(),width=100), 
                                dict(title='problems', cell=MTVerticallyCenteredTextFieldCell.alloc().init(),minWidth=500,width=500),
                                ]
        self.w.view.glyphs = MTList((0,0,-0,-0),self.items,
            columnDescriptions=columnDescriptions,
            rowHeight=45,selectionCallback=self.showPopoverCallback,
            allowsMultipleSelection=False,
            showColumnTitles=False,doubleClickCallback=self.doubleClickCallback)
        self.w.view.glyphs.setSelection([])

        self.w.open()
        self.w.bind('resize', self.windowResizeCallback)
        self.windowResizeCallback(self.w)
        

    def windowResizeCallback(self, window):
        x,y,w,h = window.getPosSize()
        if self.items:
            biggestNumOfProblems = max([len(item['problems'].split('\n')) for item in self.items])
        table = self.w.view.glyphs.getNSTableView()
        glyphCellColumn = table.tableColumns()[0]
        problemsColumn = table.tableColumns()[-1]
        glyphCellColumn.setResizable_(False)
        if w < 300:
            problemsColumn.setHidden_(True)
            problemsColumn.setResizable_(True)
            problemsColumn.setMinWidth_(500)
            problemsColumn.setWidth_(500)
            glyphCellColumn.setWidth_(100)
            table.setRowHeight_(45)
        else:
            problemsColumn.setHidden_(False)
            problemsColumn.setResizable_(False)
            glyphCellColumn.setWidth_(100)
            if self.txtH*biggestNumOfProblems > 45:
                table.setRowHeight_(self.txtH*biggestNumOfProblems)


    def doubleClickCallback(self, sender):
        selection = sender.getSelection()[0]
        glyphName = self.lettersWithIssues[selection]
        glyph = self.currfont[glyphName]
        
        if CurrentFont() is None:
            for rowIndex,item in enumerate(self.designspace.fontMasters):
                if item['font'] == glyph.font:
                    self.designspace.setOpenedFont(rowIndex)
        OpenGlyphWindow(glyph)


    def showPopoverCallback(self, sender):
        selection = sender.getSelection()
        x,y,p = [self.padding]*3
        if not selection:
            return
        for i in selection:
            problems = self.items[i]['problems']
            height = len(problems.split('\n')) * self.txtH + p*2
            index = sender.getSelection()[0]
            relativeRect = sender.getNSTableView().rectOfRow_(index)
            # offset = sender.getNSScrollView().documentView().frame().size.height
            # offset -= sender.getNSScrollView().documentView().frame().size.height*sender.getNSScrollView().verticalScroller().floatValue()
            # offset = sender.getNSScrollView().documentView().frame().size.height%height*sender.getNSScrollView().verticalScroller().floatValue()
            # offset = sender.getNSScrollView().frame().size.height*sender.getNSScrollView().verticalScroller().floatValue()
            # offset = (sender.getNSScrollView().contentView().frame().size.height+sender.getNSScrollView().frame().size.height*sender.getNSScrollView().verticalScroller().floatValue())-sender.getNSScrollView().frame().size.height
            offset = sender.getNSScrollView().contentView().documentVisibleRect().origin.y
            relativeRect.origin.y -= offset
            # relativeRect.origin.y += offset
            print('&&&&&&&&&&&&&&&&')
            print(sender.getNSScrollView().contentView().documentVisibleRect())
            # print(offset)
            # print(relativeRect, sender.getNSScrollView().documentView().frame())

            self.pop = Popover((400, height), behavior='transient')
            self.pop.text = TextBox((x, y, -p, -p), problems)
            self.pop.open(parentView=sender, preferredEdge='right', relativeRect=relativeRect)
        
        

    def closeWindow(self, info):
        # binding to window
        self.removeObservers()
        self.isActive = False
        # resetting toolbar button status, when window is closed
        buttonObject = self.toolBtn.getNSButton()
        self.toolBtn.status = False
        buttonObject.setBordered_(False)

  

    # RF observers

    # code goes here

    # ui callbacks

    # code goes here

    # tool actions

    def testIncompaibility(self, sender=None):
        self.currfont = CurrentFont()
        if self.currfont is None:
            self.currfont = self.designspace.fontMasters[0]['font']

        self.problemChecker.ds.loadFonts()
        self.problemChecker.nf = self.problemChecker.ds.getNeutralFont()
        self.problemChecker.checkGlyphs()
        _categories = DesignSpaceProblem._categories
        _problems  =  DesignSpaceProblem._problems
        problems = [dict(category=_categories[problem.category],problem=_problems[(problem.category,problem.problem)],data=problem.data) for problem in self.problemChecker.problems]
        self.glyph_problems = {}
        for problemDescription in problems:
            data = problemDescription['data']
            glyph = data['glyphName']
            if glyph not in self.glyph_problems.keys():
                self.glyph_problems[glyph] = []
            _data = " -> "
            for dataCategory in data:
                if dataCategory == 'glyphName':
                    continue
                _data += dataCategory+': '+data[dataCategory]
            if _data == " -> ":
                _data = ''
            if '– '+problemDescription['problem'] + _data not in self.glyph_problems[glyph]:
                self.glyph_problems[glyph] += ['– '+problemDescription['problem'] + _data]


        glyphsOrder = []
        for fontName, fontObj in self.problemChecker.ds.fonts.items():
            if fontObj is None:
                continue
            for glyphName in fontObj.glyphOrder:
                if not glyphName in glyphsOrder:
                    glyphsOrder += [glyphName]


        self.lettersWithIssues = []
        for glyphName in glyphsOrder:
            if glyphName in self.glyph_problems.keys():
                self.lettersWithIssues +=[glyphName]

        self.items = []
        for glyphName in self.lettersWithIssues:
            data = ""
            cell = GlyphCellFactoryWithNotDef(glyphName,self.currfont, 150, 150, glyphColor=self.glyphColor, bufferPercent=.01)
            self.items += [dict(
                            glyph=cell,
                            problems='\n'.join(self.glyph_problems[glyphName]),
                            name=glyphName,
                            )]
        countTxt = f'{len(problems)} problems\n{len(self.lettersWithIssues)} glyphs'
        self.w.foundTxtBox.set(countTxt)



