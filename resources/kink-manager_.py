# coding=utf-8
from vanilla import *
from defconAppKit.windows.baseWindow import BaseWindowController
from mojo.events import addObserver, removeObserver
from mojo.drawingTools import *
import math

import countPoints

def rotate( P,angle, originPoint):
    """Rotates x/y around x_orig/y_orig by angle and returns result as [x,y]."""
    alfa = angle
    px,py=P
    originPointX, originPointY = originPoint

    x = ( px - originPointX ) * math.cos( alfa ) - ( py - originPointY ) * math.sin( alfa ) + originPointX
    y = ( px - originPointX ) * math.sin( alfa ) + ( py - originPointY ) * math.cos( alfa ) + originPointY

    return x, y

def angle(p1, p2):
        p1x, p1y = p1
        p2x, p2y = p2
        return math.atan2(p2x - p1x, p2y - p1y)

def lenghtAB(A,B):
    """Returns distance value between two points: A and B"""
    bx,by = B
    ax,ay = A
    sqA = (bx - ax) **2
    sqB = (by - ay) **2
    sqC = sqA + sqB
    if sqC > 0:
        lengthAB = math.sqrt(sqC)
        return lengthAB
    else:
        return 0
def dPoint(p, s, txt=""):
    r = s/2
    x, y = p
    rect(x-r, y-r, s, s)
    if txt:
        text(txt,x+s,y+s)

class KinksManager(BaseWindowController):

    def __init__(self):
        self.w = FloatingWindow((200, 45), "KinksManager")
        self.w.startStopButton = Button((10, 10, -10, 22), "Start", callback=self.startStopButtonCallback)
        # setup basic windwo behavoir (this is an method from the BaseWindowController)
        self.w.open()
        self.setUpBaseWindowBehavior()
        self.g = CurrentGlyph()
        self.vanillaView = None
        self.bPointsInfo = []

    def rb_removeObservers(self):
        # gruped removeObserver methods
        removeObserver(self,"viewDidChangeGlyph")
        removeObserver(self,"viewWillChangeGlyph")
        removeObserver(self,"draw")
        self.g.removeObserver(self,"Glyph.Changed")

    def windowCloseCallback(self, sender):
        # this receives a notification whenever the window is closed
        # remove the observers
        self.rb_removeObservers()
        # and send the notification to the super
        super(KinksManager, self).windowCloseCallback(sender)

    def startStopButtonCallback(self, sender):
        if sender.getTitle() == "Start":
            self.g.prepareUndo("Show Curvature")
            self.checkInflections()
            self.g.performUndo()
            self.g.update()

            sender.setTitle("Stop")
            # here I'm adding my observers

            self.g.addObserver(self, "rb_somethingChanged", "Glyph.Changed")
            addObserver(self, "rb_willChangeGlyphView", "viewWillChangeGlyph")
            addObserver(self, "rb_didChangeGlyphView", "viewDidChangeGlyph")
            addObserver(self, "rb_draw", "draw")
        else:
            self.g.prepareUndo("Show Curvature")
            self.checkInflections()
            self.g.performUndo()
            self.g.update()
            # set "Start" as title for the button
            sender.setTitle("Start")
            self.rb_removeObservers()

    def rb_draw(self, info):

        if  len(self.bPointsInfo) > 0:
            accuracyAngle = 2 # IMPORTANT, you should make a slider, or combobox
            accuracyRatio = 3
            scale = info['scale']
            selectedInfo = self.bPointsInfo[0]
            bPoint = selectedInfo[0][1]
            pointIn = selectedInfo[0][0]
            pointOut = selectedInfo[0][2]
            angleBp = selectedInfo[1]
            ratioInBP = selectedInfo[2][0]
            fill(1,0,0,.3)
            dPoint(pointIn,20*scale,'pointIn')
            dPoint(bPoint,20*scale,'bPoint')
            dPoint(pointOut,20*scale,'pointOut')





    def rb_didChangeGlyphView(self,info):
        # managing different glyphs in the font (adding change-observer to newly opened glyph)
        self.g = info['glyph']
        try:
            self.g.addObserver(self, "rb_somethingChanged", "Glyph.Changed")
            self.checkInflections()
        except:
            pass


    def rb_willChangeGlyphView(self,info):
        # managing different glyphs in the font (removing change-observer from just closed glyph)
        self.g.removeObserver(self,"Glyph.Changed")

    def rb_somethingChanged(self, info):
        self.checkInflections()

    def checkInflections(self):

        allfonts = AllFonts().getFontsByFamilyName(CurrentFont().info.familyName)

        if countPoints.compatibilityCheck(self.g, allfonts):

            gName = self.g.name
            self.bPointsInfo = [] # 0 - anchor | 1 - angle | 2 - ratio
            for font in allfonts:
                for c_i in range(len(self.g)):
                    c = self.g[c_i]
                    points = c.points

                    for p_i in range(len(points)):

                        p = points[p_i]
                        if p.selected:
                            pSel = p

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
                                nearer = p_i
                                middle = i_one
                                further = i_two

                            elif pSel.type == "line" or pSel.type == "curve":
                                nearer = p_i-1
                                middle = p_i
                                further = i_one


                            g_ref = font[gName]
                            p_ref = g_ref[c_i].points

                            bpIn,bpAn,bpOut = (p_ref[nearer],p_ref[middle],p_ref[further])
                            bpIn = (bpIn.x,bpIn.y)
                            bpAn = (bpAn.x,bpAn.y)
                            bpOut = (bpOut.x,bpOut.y)


                            lenIn  = lenghtAB(bpAn,bpIn)
                            lenOut = lenghtAB(bpAn,bpOut)
                            whole = lenIn+lenOut
                            ratioIn = lenIn/whole
                            ratioOut = lenOut/whole
                            self.bPointsInfo.append(((bpIn,bpAn,bpOut), angle(bpIn,bpOut),(ratioIn,ratioOut)))



KinksManager()
