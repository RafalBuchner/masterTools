from uuid import uuid4
from ufoProcessor import *
from mojo.events import addObserver, removeObserver, publishEvent
from mojo.roboFont import *
from pprint import pprint
from collections import OrderedDict
# from mojo.roboFont import AllFonts, RFont, OpenFont

class MasterToolsProcessor(DesignSpaceProcessor):

    fontClass = RFont
    layerClass = RLayer
    glyphClass = RGlyph
    libClass = RLib
    glyphContourClass = RContour
    glyphPointClass = RPoint
    glyphComponentClass = RComponent
    glyphAnchorClass = RAnchor
    kerningClass = RKerning
    groupsClass = RGroups
    infoClass = RInfo
    featuresClass = RFeatures

    def __init__(self, readerClass=None, writerClass=None, fontClass=None, ufoVersion=3, useVarlib=False):
        super(MasterToolsProcessor, self).__init__(readerClass=readerClass, writerClass=writerClass, fontClass=fontClass, ufoVersion=ufoVersion, useVarlib=useVarlib)
        self.openedFontsById = {}




    @property
    def includedFonts(self):
        self._includedFonts = [item for item in self.fontMasters if item["include"]]
        return self._includedFonts

    @property
    def openedIncludedFonts(self):
        self._openedIncludedFonts = []
        for item in self.includedFonts:
            opened = item.get("openedFont")
            if opened is None:
                continue
            self._openedIncludedFonts += [opened]
        return self._openedIncludedFonts

    def compareFonts(self):
        pass

    def compareGlyphs(self, fontNames, *glyphNames):
        pass

    def _instantiateFont(self, path):
        for _id in self.openedFontsById:
            font = self.openedFontsById[_id]
            if font.path == path:
                return font
        return RFont(path, showInterface=False)

    def loadFonts(self, reload=False):
        # Load the fonts and find the default candidate based on the info flag
        if self._fontsLoaded and not reload:
            return
        names = set()
        for i, sourceDescriptor in enumerate(self.sources):
            if sourceDescriptor.name is None:
                # make sure it has a unique name
                sourceDescriptor.name = "master.%d" % i
            if sourceDescriptor.name not in self.fonts:
                if os.path.exists(sourceDescriptor.path):
                    self.fonts[sourceDescriptor.name] = self._instantiateFont(sourceDescriptor.path)
                    self.problems.append("loaded master from %s, layer %s, format %d" % (sourceDescriptor.path, sourceDescriptor.layerName, getUFOVersion(sourceDescriptor.path)))
                    names |= set(self.fonts[sourceDescriptor.name].keys())
                else:
                    self.fonts[sourceDescriptor.name] = None
                    self.problems.append("source ufo not found at %s" % (sourceDescriptor.path))
        self.glyphNames = list(names)
        if not reload:
            self._setFontMasters()

    def _setFontMasters(self):
        self.fontMasters = []
        self.fontsById = OrderedDict()
        for info in self.getFonts():
            font = info[0]
            fontname = os.path.relpath(font.path, self.path)
            fontname = fontname[3:]
            uniqueID = str(uuid4())
            isFontOpened = False
            if font in AllFonts():
                self.openedFontsById[uniqueID] = font
                isFontOpened = True
            self.fontMasters += [dict(
                include=True,
                fontname=fontname,
                font=info[0],
                path=info[0].path,
                designSpacePosition=info[1],
                positionString=" ".join([str(position)+": "+str(info[1][position]) for position in info[1]]),
                uniqueID=uniqueID,
                opened=isFontOpened,
                )]
            self.fontsById[uniqueID] = font
        self._fontsLoaded = True
        publishEvent("MT.designspace.fontMastersChanged", designspace=self)

    def getFontIndexes(self, font):
        indexes =[]
        for i,item in enumerate(self.fontMasters):
            if font.path == item['path']:
                indexes += [i]
        return indexes

    def getCommonGlyphSet(self):
        glyphSet = []
        for item in self.fontMasters:
            glyphSet += list(item['font'].glyphOrder)
        glyphSet = list(set(glyphSet))
        glyphSet.sort()
        return glyphSet

    def getOpenedFont(self, rowIndex):
        item = self.fontMasters[rowIndex]
        hasInterface = item['font'].hasInterface()

        if hasInterface:
            return item['font']
        return None

    def setOpenedFont(self, rowIndex):
        item = self.fontMasters[rowIndex]
        # assert not item['font'].hasInterface(), "WARNING font was already opened"
        if item['uniqueID'] not in self.openedFontsById.keys():
            item['font'] = OpenFont(item['path'])
            publishEvent("MT.designspace.fontMastersChanged", designspace=self)
            item['font'].addObserver(self, 'includedFontChangedEvent', 'Font.Changed')
            self.openedFontsById[item['uniqueID']] = item['font']


    def delOpenedFont(self, rowIndex):
        item = self.fontMasters[rowIndex]
        font = self.openedFontsById.get(item['uniqueID'])
        if font is not None:
            font.removeObserver(self, 'Font.Changed')
            del self.openedFontsById[item['uniqueID']]
            
    
    def __del__(self):
        if len(self.openedFontsById) > 0:
            for font in self.openedFontsById:
                font.removeObserver(self, 'Font.Changed')


    # observers
    def includedFontChangedEvent(self, notification):
        changedOpenedFont = RFont(notification.object)
        
        for item in self.fontMasters:
            if item['font'].path == changedOpenedFont.path:
                item['font'] = changedOpenedFont
        publishEvent("MT.designspace.fontMastersChanged", designspace=self)
        # self.loadFonts(reload=True)

    def getMaxNumberOfContoursInDesignSpace_forGlyph(self, glyphName):
        numbersOfContours = []
        for item in self.fontMasters:
            numbersOfContours += [len(item['font'][glyphName].contours)]
        if numbersOfContours:
            return max(numbersOfContours)
        else:
            return 0    
    def getMaxNumberOfComponentsInDesignSpace_forGlyph(self, glyphName):
        numbersOfComponents = []
        for item in self.fontMasters:
            numbersOfComponents += [len(item['font'][glyphName].components)]
        if numbersOfComponents:
            return max(numbersOfComponents)
        else:
            return 0
    @property
    def fontMasters(self):
        return self.__fontMasters

    @fontMasters.setter
    def fontMasters(self, value):
        self.__fontMasters = value
        publishEvent("MT.designspace.fontMastersChanged", designspace=self)

