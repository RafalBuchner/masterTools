# coding=utf-8
from vanilla import *
from defconAppKit.windows.baseWindow import BaseWindowController
from mojo.events import addObserver, removeObserver
from mojo.drawingTools import *
from mojo.roboFont import CurrentGlyph, CurrentFont
import math

import masterTools.misc.countPoints as countPoints
from masterTools.misc.MTMath import *


class KinkManager(object):
    def __init__(self, designspace):
        self.designspace = designspace
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

    def finish(self):
        self.glyph.prepareUndo("Show Curvature")
        self.checkInflections()
        self.glyph.performUndo()
        self.glyph.update()
        # set "Start" as title for the button
        self.mt_removeObservers()
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

            for info in self.bPointsInfo[1:]:
                index = self.bPointsInfo.index(info)
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
                ratioIn,ratioOut = info[2]

                unit = 400
                lengthOfLine = unit*scale
                A,B = ((-lengthOfLine/2,-shift*(index+1)),(lengthOfLine/2,-shift*(index+1)))

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
