# coding=utf-8
from vanilla import *
from defconAppKit.windows.baseWindow import BaseWindowController
from mojo.events import addObserver, removeObserver, publishEvent
from mojo.drawingTools import *
from mojo.roboFont import CurrentGlyph, CurrentFont
import math
from mojo.canvas import CanvasGroup

from defconAppKit.windows.baseWindow import BaseWindowController

from masterTools.UI.settings import Settings
from masterTools.UI.vanillaSubClasses import MTList,  MTFloatingDialog
import masterTools.misc.countPoints as countPoints
from masterTools.misc.MTMath import *

class KinkingCanvas(CanvasGroup):
    def __init__(self, posSize, kManager):
        super().__init__(posSize, self)
        self.posSize = posSize
        self.kManager = kManager
        addObserver(self, 'kinkManagerChanged', 'mt.KinkManager.changed') # description

    def kinkManagerChanged(self,data):
        self.kManager = data['data']
        self.draw()

    def draw(self):
        def _drawLinePoint(p,s,color,shift=0):
            x,y=p
            save()
            stroke(*color)
            translate(x,y)
            line((0,s/2-shift),(0,-s/2-shift))
            restore()

        def _drawPoint(p,s,color):
            x,y=p
            save()
            stroke(None)
            fill(*color)
            translate(x,y)
            oval(-s/2,-s/2,s,s)
            restore()


        if  self.kManager.selectedInfo is not None:
            accuracyAngle = 2 # IMPORTANT, you should make a slider, or combobox
            accuracyRatio = 3
            scale = 1
            selectedInfo = self.kManager.selectedInfo
            bPoint = selectedInfo[0][1]
            pointIn = selectedInfo[0][0]
            pointOut = selectedInfo[0][2]
            angleBp = selectedInfo[1]
            ratioInBP = selectedInfo[2][0]


            for index, info in enumerate(self.kManager.bPointsInfo):
                
                angle = info[1]
                # if round(angle,accuracyAngle) == round(angleBp,accuracyAngle):
                #     color = [0,0.9,0.5,.4]
                #     angle = angleBp-2*math.pi
                # else:
                color = (1,0.1,0,.4)

                # _drawAngle(bPoint,pointIn,pointOut)

                # draw ratio
                # x,y = bPoint

                shift = 30*scale
                shift_offset = shift
                x,y = (self.getNSView().frame().size.width/2,shift*index+shift_offset)
                # _drawLinePoint((x,y),10*scale,color)
                
                # ratioIn,ratioOut = info[2]

                unit = 120
                lengthOfLine = unit
                A,B = ((x-lengthOfLine/2,y),(x+lengthOfLine/2,y))

                strokeWidth(3*scale)
                stroke(*color)

                _drawLinePoint(A,10*scale,color)
                _drawLinePoint(B,10*scale,color)
                line(A,B)
                _drawLinePoint(((ratioIn*unit-unit/2)*scale,y),16*scale,color)

                # if index == 1:
                #     # drawing current reference
                #     line((-lengthOfLine/2,-shift),(lengthOfLine/2,-shift))
                #     _drawLinePoint((-lengthOfLine/2,-shift),10*scale,color)
                #     _drawLinePoint((lengthOfLine/2,-shift),10*scale,color)
                #     _drawLinePoint(((ratioInBP*unit-unit/2)*scale,-shift),len(self.kManager.bPointsInfo)*40*scale,color,(len(self.kManager.bPointsInfo)*40*scale)/2-5*scale)


                # restore()


class KinkManager(MTFloatingDialog, BaseWindowController):
    id = 'mt.tools.KinkManager'
    winMinSize = (250,200)
    winMaxSize = (250,6000)
    padding = 10

    def __init__(self, designspace, toolBtn):
        self.designspace = designspace
        self.toolBtn = toolBtn
        self.glyph = None
        self.isActive = False


    def mt_removeObservers(self):
        # gruped removeObserver methods
        removeObserver(self,"viewDidChangeGlyph")
        removeObserver(self,"viewWillChangeGlyph")
        removeObserver(self,"MT.designspace.fontMastersChanged")
        removeObserver(self,"draw")
        self.glyph.removeObserver(self,"Glyph.Changed")

    def windowCloseCallback(self, sender):
        # this receives a notification whenever the window is closed
        # remove the observers
        self.mt_removeObservers()
        # and send the notification to the super
        super(KinksManager, self).windowCloseCallback(sender)

    def start(self, designspace):
        self.mt_updateFonts(
            {
                "designspace" : designspace
            }
        )
        self.glyph = CurrentGlyph()
        self.bPointsInfo = []
        self.selectedInfo = None

        self.glyph.prepareUndo("Show Curvature")
        self.checkInflections()
        self.glyph.performUndo()
        self.glyph.update()
        self.isActive = True

        # here I'm adding my observers

        self.glyph.addObserver(self, "mt_glyphChanged", "Glyph.Changed")
        addObserver(self, "mt_willChangeGlyphView", "viewWillChangeGlyph")
        addObserver(self, "mt_didChangeGlyphView", "viewDidChangeGlyph")
        addObserver(self, "mt_draw", "draw")
        addObserver(self, "mt_updateFonts", "MT.designspace.fontMastersChanged")

        self.initUI()

    def initUI(self):
        self.uiSettingsControler = Settings()
        self.uiSettings = self.uiSettingsControler.getDict()
        self.glyphColor = self.uiSettingsControler.getGlyphColor_forCurrentMode()
        x, y, p = (self.padding, self.padding, self.padding)

        self.w = self.window(self.winMinSize,
                        "KinkManager",
                        minSize=self.winMinSize,
                        maxSize=self.winMaxSize,
                        autosaveName=self.id,
                        darkMode=self.uiSettings["darkMode"],
                        closable=True,
                        noTitleBar=True)
        self.w.canvas = KinkingCanvas((0,0,-0,-0), self)
        self.w.open()

        self.w.bind('close', self.closeWindow)

    def closeWindow(self, info):
        # binding to window
        self.mt_removeObservers()
        self.isActive = False
        # resetting toolbar button status, when window is closed
        buttonObject = self.toolBtn.getNSButton()
        self.toolBtn.status = False
        buttonObject.setBordered_(False)

    def finish(self):
        self.glyph.prepareUndo("Show Curvature")
        self.checkInflections()
        self.glyph.performUndo()
        self.glyph.update()
        # set "Start" as title for the button
        self.mt_removeObservers()
        if hasattr(self, "w"):
            if self.w._window is not None:
                self.w.close()
        self.isActive = False

    def mt_updateFonts(self, sender):
        self.designspace = sender['designspace']
        self.allfonts = [item['font'] for item in self.designspace.includedFonts]

    def mt_draw(self, info):
        def _drawLinePoint(p,s,color,shift=0):
            x,y=p
            save()
            stroke(*color)
            translate(x,y)
            line((0,s/2-shift),(0,-s/2-shift))
            restore()

        def _drawPoint(p,s,color):
            x,y=p
            save()
            stroke(None)
            fill(*color)
            translate(x,y)
            oval(-s/2,-s/2,s,s)
            restore()

        def _drawAngle(anchor,pointIn,pointOut):
            x,y = anchor
            x1 = lenghtAB(pointIn,anchor)
            x2 = lenghtAB(pointOut,anchor) *-1


            line_ref = (
                rotate((x1,0),-math.pi/2 - angle,(0,0)),
                rotate((x2,0),-math.pi/2 - angle,(0,0))
                )

            save()
            translate(x,y)

            _drawPoint(line_ref[0],10*scale,color)
            _drawPoint(line_ref[1],10*scale,color)

            fill(None)
            strokeWidth(5*scale)
            stroke(*color)
            line(*line_ref)
            stroke(None)
            fill(*color)

            restore()
        # if  len(self.bPointsInfo) > 0:
        if  self.selectedInfo is not None:
            accuracyAngle = 2 # IMPORTANT, you should make a slider, or combobox
            accuracyRatio = 3
            scale = info['scale']
            selectedInfo = self.selectedInfo
            bPoint = selectedInfo[0][1]
            pointIn = selectedInfo[0][0]
            pointOut = selectedInfo[0][2]
            angleBp = selectedInfo[1]
            ratioInBP = selectedInfo[2][0]


            for index, info in enumerate(self.bPointsInfo):
                
                angle = info[1]
                if round(angle,accuracyAngle) == round(angleBp,accuracyAngle):
                    color = [0,0.9,0.5,.4]
                    angle = angleBp-2*math.pi
                else:
                    color = (1,0.1,0,.4)

                _drawAngle(bPoint,pointIn,pointOut)

                # draw ratio
                x,y = bPoint
                shift = 30*scale
                shift_offset = shift
                ratioIn,ratioOut = info[2]

                unit = 400
                lengthOfLine = unit*scale
                A,B = ((-lengthOfLine/2,- (shift*(index+1) + shift_offset)),(lengthOfLine/2,- (shift*(index+1) + shift_offset)))

                if round(ratioIn,accuracyRatio) == round(ratioInBP,accuracyRatio):
                    color = [0,0.9,0.5,.4]
                else:
                    color = (1,0.1,0,.4)

                strokeWidth(3*scale)
                stroke(*color)

                save()
                translate(x,y)

                _drawLinePoint(A,10*scale,color)
                _drawLinePoint(B,10*scale,color)
                line(A,B)
                _drawLinePoint(((ratioIn*unit-unit/2)*scale,-shift*(index+1)),10*scale,color)

                if index == 1:
                    # drawing current reference
                    line((-lengthOfLine/2,-shift),(lengthOfLine/2,-shift))
                    _drawLinePoint((-lengthOfLine/2,-shift),10*scale,color)
                    _drawLinePoint((lengthOfLine/2,-shift),10*scale,color)
                    _drawLinePoint(((ratioInBP*unit-unit/2)*scale,-shift),len(self.bPointsInfo)*40*scale,color,(len(self.bPointsInfo)*40*scale)/2-5*scale)


                restore()



    def mt_didChangeGlyphView(self,info):
        # managing different glyphs in the font (adding change-observer to newly opened glyph)
        self.glyph = info['glyph']
        try:
            self.glyph.addObserver(self, "mt_glyphChanged", "Glyph.Changed")
            self.checkInflections()
        except:
            pass


    def mt_willChangeGlyphView(self,info):
        # managing different glyphs in the font (removing change-observer from just closed glyph)
        self.glyph.removeObserver(self,"Glyph.Changed")

    def mt_glyphChanged(self, info):
        self.checkInflections()
        publishEvent('mt.KinkManager.changed', data=self) # description

    def checkInflections(self):


        if countPoints.compatibilityCheck(self.glyph, self.allfonts):

            gName = self.glyph.name
            self.bPointsInfo = [] # 0 - anchor | 1 - angle | 2 - ratio

            for font in self.allfonts:
                for c_i, c in enumerate(self.glyph):
                    points = c.points

                    for p_i, p in enumerate(points):
                        if p.selected:
                            pSel = p

                            nearer = None
                            middle = None
                            further = None
                            i_one = None
                            i_two = None
                            # avoiding situation when one of 3 points has index 0
                            if p_i+1 > len(points)-1:
                                i_one = -1
                            else:
                                i_one = p_i + 1

                            if p_i+2 > len(points)-1:
                                nearer = -1
                                middle = 0
                                further = 1
                            else:
                                i_two = p_i + 2

                            if points[i_one].type == "offcurve" and pSel.type == "offcurve" and points[i_one] != pSel:
                                nearer = p_i-2
                                middle = p_i-1
                                further = p_i

                            elif (points[i_one].type == "curve" or points[i_one].type == "line") and pSel.type == "offcurve":
                                # dragged
                                nearer = p_i
                                middle = i_one
                                further = i_two

                            elif pSel.type == "line" or pSel.type == "curve":
                                nearer = p_i-1
                                middle = p_i
                                further = i_one


                            g_ref = font[gName]
                            p_ref = g_ref[c_i].points
                            if nearer is not None:
                                bpIn,bpAn,bpOut = (p_ref[nearer],p_ref[middle],p_ref[further])
                                bpIn = (bpIn.x,bpIn.y)
                                bpAn = (bpAn.x,bpAn.y)
                                bpOut = (bpOut.x,bpOut.y)


                                lenIn  = lenghtAB(bpAn,bpIn)
                                lenOut = lenghtAB(bpAn,bpOut)
                                whole = lenIn+lenOut
                                ratioIn = lenIn/whole
                                ratioOut = lenOut/whole
                                info = ((bpIn,bpAn,bpOut), angle(bpIn,bpOut),(ratioIn,ratioOut))
                                self.bPointsInfo.append(info)
                                if font == CurrentFont():
                                    self.selectedInfo = info


if __name__ == "__main__":
    KinkManager()
