'''
this script will help user manually solve the glyph's order problems
'''
from mojo.canvas import Canvas, CanvasGroup
from vanilla import *
from mojo.drawingTools import *
from fontTools.pens.cocoaPen import CocoaPen
from lib.cells.colorCell import RFPopupColorPanel, RFColorCell
from collections import OrderedDict
from pprint import pprint
from masterTools.misc.drawingTools import _drawBPoints, _drawPoint, _drawLine, _drawPSCurve
from masterTools.misc.sortingTools import reorderContourToIndex, reorderComponentToIndex
from masterTools.UI.vanillaSubClasses import MTButton
from masterTools.UI.objcBase import MTPopUpButtonMenuItem
from masterTools.UI.settings import Settings
from mojo.UI import MenuBuilder
from mojo.roboFont import CurrentGlyph, RFont
import masterTools.misc.RBMath as RBMath 
import AppKit
from fontParts.base import BaseFont
uiSettingsControler = Settings()
defaultColors = uiSettingsControler.defaultColors
'''
    - add component functionality:
        - component labeling in self.view.canvasView.canvas.list
            (add additional row for component)
        - add component max list
        - component drawing
        - component rearranging
    - add 'glyph is empty label' in self.view.canvasView.canvas
    - add master name caption in self.view.canvasView.canvas
'''

class SelectOrder(object):
    title = 'Compatibility Helper'
    key = ''.join(title)
    id = f"com.rafalbuchner.ProblemSolvingTools.{key}"
    #
    winMinSize = (700,370)
    winMaxSize = (6000,5000)
    txtH = 17
    btnH = 24
    padding = 10
    #
    margin = 75
    _strokeWidth=2
    selectedContourIndexes = []
    def __init__(self, posSize, designspace):
        self.designspace = designspace
        
        self.uiSettings = uiSettingsControler.getDict()
        self.glyphColor = uiSettingsControler.getGlyphColor_forCurrentMode()
        if CurrentGlyph() is not None:
            self.letterName = CurrentGlyph().name 
        else:
            self.letterName = 'K'
        # functionality attrs
        self.reorderingMode ='contours'
        self.selectedContourIndexes = {}
        self.closestPointOnPath = (-20000,-20000)
        self.closestElementsInfo = None
        self.cursorLoc = (-20000,-20000)
        self.currentLocOnMaster = (None, (-20000,-20000), None)
        self.orderSelected = False
        # drawing attrs
        self.scale = .25
        self.canvasSize=(self.maxGlyphWidth*self.scale, self.columnHeight*self.scale)
        self.displaySettings = dict(
                points=False, stroke=False, fill=True
            )

        self.view = Group(posSize)
        self.initCanvasUI()
        self.initInterfaceUI()


    def getView(self):
        return self.view
    
    def initCanvasUI(self):
        ### CANVAS GROUP
        x,y,p = [self.padding] * 3
        # backgroundColor = AppKit.NSColor.colorWithCalibratedRed_green_blue_alpha_(1,1,1,1)
        backgroundColor = None
        x = 0
        self.view.canvasView = Group((x,0,-300-p,-0))
        self.view.canvasView.scaleSlider = Slider(
            (0,0,self.txtH,300),minValue=0.001,maxValue=1,value=self.scale,callback=self.scaleSliderCallback)
        # y += p + self.txtH
        x += self.txtH
        
        self.view.canvasView.canvas = Canvas((x, y, -0, -p*2-self.btnH*2-p/2), delegate=self,canvasSize=self.canvasSize,autohidesScrollers=True,backgroundColor=backgroundColor,drawsBackground=True)
        
        colorCell = RFColorCell.alloc().initWithDoubleClickCallback_(self.colorDoubleClickCallback)
        columnDescriptions = [dict(title="element",width=70)]+[dict(title=f"{i}", cell=colorCell, width=20) for i in range(self.maxNumberOfContours)]
        contourRow = {f'{i}' : AppKit.NSColor.colorWithCalibratedRed_green_blue_alpha_(*defaultColors[i],1) for i in range(self.maxNumberOfContours)}
        contourRow['element'] = 'contour'
        listItem = [contourRow]
        self.view.canvasView.list = List((x,-p-self.btnH*2-p/2,-0,self.btnH*2+p/2),listItem,columnDescriptions=columnDescriptions)
    
    def initInterfaceUI(self):
        ### INTERFACE GROUP
        x,y,p = [self.padding] * 3
        self.view.interfaceView = Group((-300-p,0,-0,-0))
        # make it here
        
    def buildRightClickMenu(self):
        def _getLowestNumberOfContoursAndComponentsInSelectedMasterGlyphs():
            numOfContours   = []
            numOfComponents = []
            for _id in self.selectedContourIndexes:
                font = self.designspace.fontsById[_id]
                glyph = font[self.letterName]
                numOfContours   += [len(glyph.contours)]
                numOfComponents += [len(glyph.components)]

            if numOfContours:
                numOfContours = min(numOfContours)
            else: numOfContours = None

            if numOfComponents:
                numOfComponents = min(numOfComponents)
            else: numOfComponents = None

            return dict(contours=numOfContours, components=numOfComponents)

        if self.reorderingMode=='contours':
            num = _getLowestNumberOfContoursAndComponentsInSelectedMasterGlyphs().get('contours')

        elif self.reorderingMode=='components':
            num = _getLowestNumberOfContoursAndComponentsInSelectedMasterGlyphs().get('components')

        if num is not None:
            items = list(range(num))

        else: items = []

        
        self.builder = MenuBuilder([
                # self.chooseIndexPopUp,
                ("choose new index for selection", [(f'{i}', self.chooseElementOrderCallback) for i in items]),
            ])

        self.rightClickMenu = self.builder.getMenu()
        self.rightClickMenu.setAutoenablesItems_(False)

    def computeGlyphInfo(self):
        self.dimentions = OrderedDict()
        glyphWidths = []
        numberOfContours = []
        for font in self.designspace.fontsById.values(): 

            if self.letterName in font.keys():
                glyph = font[self.letterName]
                glyphWidths += [glyph.width]
                numberOfContours += [len(glyph)]

        self.maxGlyphWidth = max(glyphWidths)
        self.maxNumberOfContours = max(numberOfContours)

        absoluteHeight = 0
        for item in self.designspace.fontMasters:
            font = item['font']
            if self.letterName not in font.keys():
                self.dimentions[self.letterName] = None
                continue

            glyph = font[self.letterName]
            _x,_y,x_,y_=glyph.box
            height = y_ - _y + self.margin*2
            glyphMargin = (self.maxGlyphWidth - glyph.width) /2
            absoluteBottom = absoluteHeight
            absoluteHeight += height
            self.dimentions[item['uniqueID']] = (glyphMargin, height, absoluteBottom, absoluteHeight)
        self.columnHeight=absoluteHeight

    def showGlyphs(self):
        
        save()
        translate(0,self.margin)
        
        for item in self.designspace.fontMasters:
            #### can create the bugs
            if item not in self.designspace.includedFonts:
                continue

            font = item['font']
            
            if self.letterName not in font.keys():
                # put info for the user, 
                # that the glyph is not in the
                # master
                continue

            glyphMargin, height, _,_ = self.dimentions[ item['uniqueID'] ]
            selectedContourIndexes = self.selectedContourIndexes.get( item['uniqueID'] , None)

            glyph = font[self.letterName]
            save()
            translate(glyphMargin,0)
            for i, contour in enumerate(glyph):
                r,g,b = defaultColors[i]

                
                if self.displaySettings.get('fill'):
                    fill(r,g,b,.3)
                else: fill(None)

                if self.displaySettings.get('stroke'):
                    strokeWidth(self._strokeWidth/self.scale)
                    stroke(r,g,b,.3)
                else: stroke(None)
                
                Pen = CocoaPen(font)
                contour.draw(Pen)
                drawPath(Pen.path)
                if self.displaySettings.get('points'):
                    for point in contour.bPoints:
                        _drawBPoints(point, self.scale, (r,g,b,.3) ,s=6,l=self._strokeWidth)

            if selectedContourIndexes is not None:
                # drawing selection
                selectedContour = glyph[selectedContourIndexes]
                r,g,b = defaultColors[selectedContourIndexes]
                fill(r,g,b,.6)
                Pen = CocoaPen(font)
                selectedContour.draw(Pen)
                drawPath(Pen.path)

            restore()
            translate(0,height)
        restore()

    def mouseDown(self,event):
        masterID, _, _ = self.currentLocOnMaster

        if self.closestElementsInfo is None:
            return
        contourIndex, _, _ = self.closestElementsInfo
        if contourIndex is not None:
            if self.selectedContourIndexes.get(masterID) == contourIndex:
                contourIndex = None
            self.selectedContourIndexes[masterID] = contourIndex
            self.view.canvasView.canvas.update()
            if len(self.selectedContourIndexes.keys()) >  0:
                self.orderSelected = True

        
    def acceptsMouseMoved(self):
        return True

    def draw(self):

        key, pos, _ =self.currentLocOnMaster
        if key is not None:
            # testing hovering over the glyph
            glyphMargin,h,absB,_ = self.dimentions[key]
        
        
        scale(self.scale)
        # drawing rect while hovering over the master
        if key is not None:
            fill(.1,.1,1,.1)
            rect(0,absB,self.maxGlyphWidth,h)
            

        
        # draw cursor:
        _drawPoint(self.cursorLoc, self.scale,s=4)

        # draw masters:
        self.showGlyphs()

        # draw contour index and contour pointer:
        fill(0)
        if self.closestElementsInfo is not None:
            _pointerOffset = 20
            pointerOffset = -_pointerOffset/self.scale

            contourIndex, _, _ = self.closestElementsInfo
            color = defaultColors[contourIndex]
            x,y = self.closestPointOnPath
            stroke(*color)
            strokeWidth(8/self.scale)
            lineCap('round')
            line(self.cursorLoc, (x,y+absB))
            stroke(None)

            x,y = self.cursorLoc
            fill(*color,1)
            p = (x+3/self.scale,y+3/self.scale)
            _drawPoint((p[0]+pointerOffset,p[1]+pointerOffset), self.scale,s=30,shape='oval')
            fill(1)
            fontSize(17/self.scale)
            textBox(f'{contourIndex}', (p[0]+pointerOffset*1.75,p[1]+pointerOffset*1.75,30/self.scale,25/self.scale), align='center')
        

    def mouseMoved(self, event):
        # print(event.locationInWindow())
        p=self.padding


        x,y = self.view.canvasView.canvas.getNSView().convertPoint_fromView_(event.locationInWindow(),None)

        self.cursorLoc = (x*1/self.scale,
                        y*1/self.scale)
        x,y = self.cursorLoc


        for key in self.dimentions.keys():
            glyphLeftMargin,_,absBottom,absHeight = self.dimentions[key]
            if y >= absBottom and y< absHeight:
                self.currentLocOnMaster = (key, (x,y-absBottom), glyphLeftMargin)

        key, _, _ = self.currentLocOnMaster
        glyph = None
        if self.letterName in self.designspace.fontsById[key]:
            glyph = self.designspace.fontsById[key][self.letterName]

        if glyph is not None:
            self.detectClosestElementsAction( glyph)

        self.view.canvasView.canvas.update()


    def menu(self):
        self.buildRightClickMenu()
        return self.rightClickMenu
    # def scrollwheel(self, event):
    #     if self.scale + event.deltaY() > 0.001 and self.scale + event.deltaY() < 3 :
    #         print(event)
    #         self.scale += event.deltaY()
    #         self.view.canvasView.scaleSlider.set(self.scale)
    #         self.view.canvasView.canvas.update()
    ### Actions


    def detectClosestElementsAction(self,  glyph):
        _, _position, glyphLeftMargin = self.currentLocOnMaster
        position = (_position[0]-glyphLeftMargin, _position[1])
        closestPointsRef = []
        for contour in glyph:
            segs = contour.segments
            for segIndex, seg in enumerate(segs):

                # rebuilding segment into system 2 points for line and 4 for curve (RBMath
                # needs it):
                points = [segs[segIndex - 1][-1]]  # 1adding last point from previous segment

                for point in seg.points:
                    points.append(point)  # 2 adding rest of points of the segment

                if len(points) == 2:
                    P1, P2 = points

                    # making sure that extension doesn't take open segment of the contour into count
                    if P1.type == "line" and P2.type == "move":
                        continue

                    P1, P2 = ((P1.x, P1.y), (P2.x, P2.y))
                    closestPoint, info = RBMath.getClosestInfo(position, seg, P1, P2)

                if len(points) == 4:
                    P1, P2, P3, P4 = points
                    P1, P2, P3, P4 = ((P1.x, P1.y), (P2.x, P2.y), (P3.x, P3.y), (P4.x, P4.y))
                    closestPoint, info = RBMath.getClosestInfo(position, seg, P1, P2, P3, P4)

                closestPointsRef.append((closestPoint, info))
        distances = []
        for ref in closestPointsRef:
            point = ref[0]
            distance = RBMath.lenghtAB(position, point)
            distances.append(distance)
        indexOfClosestPoint = distances.index(min(distances))
        closestPointOnPathRef = closestPointsRef[indexOfClosestPoint]
        closestPointOnPath, self.closestElementsInfo = closestPointOnPathRef
        x,y = closestPointOnPath 

        # adding margin offset:
        self.closestPointOnPath = (
                        x+glyphLeftMargin,
                        y+self.margin
                            )


    def assignNewIndexAction(self, newIndex):
        if self.reorderingMode == 'contours':
            reorderFunction = reorderContourToIndex
        elif self.reorderingMode == 'components':
            reorderFunction = reorderComponentToIndex
        for _id in self.selectedContourIndexes:
            font = self.designspace.fontsById[_id]
            glyph = font[self.letterName]
            oldIndex = self.selectedContourIndexes[_id]
            if oldIndex is not None:
                reorderFunction(glyph, oldIndex, newIndex)
            self.selectedContourIndexes[_id] = None
            # if not font.hasInterface():
            #     help(font)
            #     font_savingObj = RFont(font,False)
            #     font_savingObj.save(font.path)
            #     font_savingObj.close()

    ### Callbacks
    def windowResizeCallback(self, sender):
        # x,y,w,h = sender.getPosSize()
        # w - self.padding * 2
        pass

    def colorDoubleClickCallback(self, sender):
        self.view.canvasView.canvas.getNSView().setFrameSize_(AppKit.NSSize(self.maxGlyphWidth*self.scale, self.columnHeight*self.scale))

    def scaleSliderCallback(self, sender):
        self.scale = sender.get()
        self.view.canvasView.canvas.getNSView().setFrameSize_(AppKit.NSSize(self.maxGlyphWidth*self.scale, self.columnHeight*self.scale))
        self.view.canvasView.canvas.update()

    def chooseElementOrderCallback(self,sender):
        newIndex = int(sender.title())
        self.assignNewIndexAction(newIndex)


    ### Dynamic Attrs

    @property
    def letterName(self):
        return self.__letterName

    @letterName.setter
    def letterName(self, letterName):
        self.__letterName = letterName
        self.computeGlyphInfo()
        if hasattr(self, 'w'):
            self.view.canvasView.canvas.update()


if __name__=='__main__':
    from masterTools.misc.MasterToolsProcessor import MasterToolsProcessor
    dsPath = '/Users/rafalbuchner/Documents/repos/scripts/RoboFont3.0/+GOOGLE/master-tools/test_designSpace/mutatorSans-master/MutatorSans.designspace'
    designspace = MasterToolsProcessor()
    designspace.read(dsPath)
    designspace.loadFonts()

    testObj = SelectOrder( designspace=designspace )
