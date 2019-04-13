"""
    Vast part of the code has been borrowed
    from @letterror, orginal code will be found here:
    https://github.com/LettError/editThatNextMasterRoboFontExtension

    If you're editing masters or whatever
    and you want to switch to the same glyph in the other master
    and you spend a lot of time moving glyph windows around
    or you've had to divide your massive pixel real estate into small lots.

    Add this script to RF and wire it to a key command
    and then woosh woosh woosh cycle between the masters.
    The other script, "editThatNextMaster.py" wooshes the other direction.

    The order in which these scripts woosh through the fonts: alphabetically sorted filepath.

    With massive help from @typemytype
    @letterror
    20160930
    v6


"""

import AppKit
import random
from mojo.UI import *
from mojo.roboFont import CurrentFont, CurrentGlyph, AllFonts, OpenWindow, OpenFont, version

#import addSomeGlyphsWindow
#reload(addSomeGlyphsWindow)
#from addSomeGlyphsWindow import AddSomeGlyphsWindow

def copySelection(g):
    pointSelection = []
    compSelection = []
    anchorSelection = []
    for ci, c in enumerate(g.contours):
        for pi, p in enumerate(c.points):
            if p.selected:
                pointSelection.append((ci, pi))
    for compi, comp in enumerate(g.components):
        if comp.selected:
            compSelection.append(compi)
    for anchori, anchor in enumerate(g.anchors):
        if anchor.selected:
            anchorSelection.append(anchori)
    return pointSelection, compSelection, anchorSelection

def applySelection(g, pointSelection, compSelection, anchorSelection):
    # reset current selected points
    for ci, c in enumerate(g.contours):
        c.selected = False
    for ci, c in enumerate(g.components):
        c.selected = False
    for ai, a in enumerate(g.anchors):
        a.selected = False
    for ci, pi in pointSelection:
        if g.contours and len(g.contours) >= ci + 1:
            if len(g.contours[ci].points) >= pi + 1:
                g.contours[ci].points[pi].selected = True
    for ci in compSelection:
        if g.components and len(g.components) >= ci + 1:
            g.components[ci].selected = True
    for ai in anchorSelection:
        if g.anchors and len(g.anchors) >= ai + 1:
            g.anchors[ai].selected = True

def getCurrentFontAndWindowFlavor():
    """ Try to find what type the current window is and which font belongs to it."""
    windows = [w for w in AppKit.NSApp().orderedWindows() if w.isVisible()]
    skip = ["PreferencesWindow", "ScriptingWindow"]
    for window in windows:
        if hasattr(window, "windowName"):
            windowName = window.windowName()
            if windowName in skip:
                continue
            if hasattr(window, "document"):
                return window.document().font.path, windowName
    return None, None

def getGlyphWindowPosSize():
    w = CurrentGlyphWindow()
    if w is None:
        return
    x,y, width, height = w.window().getPosSize()
    settings = getGlyphViewDisplaySettings()
    view = w.getGlyphView()
    viewFrame = view.visibleRect()
    viewScale = w.getGlyphViewScale()
    return (x, y), (width, height), settings, viewFrame, viewScale

def setGlyphWindowPosSize(glyph, pos, size, animate=False, settings=None, viewFrame=None, viewScale=None, layerName=None):
    OpenGlyphWindow(glyph=glyph, newWindow=False)
    w = CurrentGlyphWindow()
    view = w.getGlyphView()
    w.window().setPosSize((pos[0], pos[1], size[0], size[1]), animate=animate)
    if viewScale is not None:
        w.setGlyphViewScale(viewScale)
    if viewFrame is not None:
        view.scrollRectToVisible_(viewFrame)
    if settings is not None:
        setGlyphViewDisplaySettings(settings)
    if layerName is not None:
        w.setLayer(layerName, toToolbar=True)

def setSpaceCenterWindowPosSize(font):
    w = CurrentSpaceCenterWindow()
    posSize = w.window().getPosSize()
    c = w.getSpaceCenter()
    rawText = c.getRaw()
    prefix = c.getPre()
    suffix = c.getAfter()
    gnameSuffix = c.getSuffix()
    size = c.getPointSize()
    w = OpenSpaceCenter(font, newWindow=False)
    new = CurrentSpaceCenterWindow()
    new.window().setPosSize(posSize)
    w.setRaw(rawText)
    w.setPre(prefix)
    w.setAfter(suffix)
    w.setSuffix(gnameSuffix)
    w.setPointSize(size)

def resizeOpenedFont(currentFont,pathToOpen):
    fontWindow = CurrentFontWindow()
    selectedGlyphs = currentFont.selection
    currentFontWindowQuery = fontWindow.getGlyphCollection().getQuery()
    selectedSmartList = fontWindow.fontOverview.views.smartList.getSelection()
    posSize = fontWindow.window().getPosSize()
    nextMaster = OpenFont(pathToOpen, showInterface=True)
    nextWindow = nextMaster.document().getMainWindow()
    nextMaster.selection = [s for s in selectedGlyphs if s in nextMaster]
    nextWindow.setPosSize(posSize)
    nextWindow.show()
    # set the selected smartlist
    fontWindow = CurrentFontWindow()
    try:
        fontWindow.fontOverview.views.smartList.setSelection(selectedSmartList)
        fontWindow.getGlyphCollection().setQuery(currentFontWindowQuery)    # sorts but does not fill it in the form
    except:
        pass

def switchMasterTo(nextMaster):
    currentPath, windowType = getCurrentFontAndWindowFlavor()
    f = CurrentFont()
    if windowType == "FontWindow":
        fontWindow = CurrentFontWindow()
        selectedGlyphs = f.selection
        currentFontWindowQuery = fontWindow.getGlyphCollection().getQuery()
        selectedSmartList = fontWindow.fontOverview.views.smartList.getSelection()
        posSize = fontWindow.window().getPosSize()
        nextWindow = nextMaster.document().getMainWindow()
        nextMaster.selection = [s for s in selectedGlyphs if s in nextMaster]
        nextWindow.setPosSize(posSize)
        nextWindow.show()
        # set the selected smartlist
        fontWindow = CurrentFontWindow()
        try:
            fontWindow.fontOverview.views.smartList.setSelection(selectedSmartList)
            fontWindow.getGlyphCollection().setQuery(currentFontWindowQuery)    # sorts but does not fill it in the form
        except:
            pass
    elif windowType == "SpaceCenter":
        setSpaceCenterWindowPosSize(nextMaster)
    elif windowType == "GlyphWindow":
        g = CurrentGlyph()
        selectedPoints, selectedComps, selectedAnchors = copySelection(g)
        currentMeasurements = g.naked().measurements
        if g is not None:
            # wrap possible UFO3 / fontparts objects
            if version >= "3.0":
                # RF 3.x
                currentLayerName = g.layer.name
            else:
                # RF 1.8.x
                currentLayerName = g.layerName
            if not g.name in nextMaster:
                #OpenWindow(AddSomeGlyphsWindow, f, nextMaster, g.name)
                AppKit.NSBeep()
                return None
            nextGlyph = nextMaster[g.name]
            applySelection(nextGlyph, selectedPoints, selectedComps, selectedAnchors)
            nextGlyph.naked().measurements = currentMeasurements
            if nextGlyph is not None:
                rr = getGlyphWindowPosSize()
                if rr is not None:
                    p, s, settings, viewFrame, viewScale = rr
                    setGlyphWindowPosSize(nextGlyph, p, s, settings=settings, viewFrame=viewFrame, viewScale=viewScale, layerName=currentLayerName)
    elif windowType == "SingleFontWindow":
        selectedPoints = None
        selectedComps = None
        currentMeasurements = None
        nextGlyph = None
        fontWindow = CurrentFontWindow()
        selectedGlyphs = f.selection
        nextWindow = nextMaster.document().getMainWindow()
        nextWindow = nextWindow.vanillaWrapper()
        g = CurrentGlyph()
        if g is not None:
            selectedPoints, selectedComps, selectedAnchors = copySelection(g)
            currentMeasurements = g.naked().measurements
            nextGlyph = nextMaster[g.name]
            #print("SingleFontWindow", fontWindow, selectedGlyphs, g, selectedPoints, currentMeasurements)
        # copy the posSize
        posSize = fontWindow.window().getPosSize()
        nextWindow.window().setPosSize(posSize)
        nextWindow.window().show()
        # set the new current glyph
        nextWindow.setGlyphByName(g.name)
        # set the viewscale
        currentView = fontWindow.getGlyphView()
        viewFrame = currentView.visibleRect()
        viewScale = currentView.getGlyphViewScale()
        nextView = nextWindow.getGlyphView()
        nextWindow.setGlyphViewScale(viewScale)
        nextView.scrollRectToVisible_(viewFrame)
        # maybe the viewframe needs to be seen as a factor of the rect

        nextMaster.selection = [s for s in selectedGlyphs if s in nextMaster]
        if nextGlyph is not None:
            applySelection(nextGlyph, selectedPoints, selectedComps, selectedAnchors)
            nextGlyph.naked().measurements = currentMeasurements

        rawText = fontWindow.spaceCenter.getRaw()
        prefix = fontWindow.spaceCenter.getPre()
        suffix = fontWindow.spaceCenter.getAfter()
        gnameSuffix = fontWindow.spaceCenter.getSuffix()
        size = fontWindow.spaceCenter.getPointSize()

        nextWindow.spaceCenter.setRaw(rawText)
        nextWindow.spaceCenter.setPre(prefix)
        nextWindow.spaceCenter.setAfter(suffix)
        nextWindow.spaceCenter.setSuffix(gnameSuffix)
        nextWindow.spaceCenter.setPointSize(size)

        for n in dir(nextWindow):
            print(n)
