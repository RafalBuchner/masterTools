from ufoProcessor import *
from mojo.roboFont import *
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

    def _instantiateFont(self, path):
        for font in AllFonts():
            if font.path == path and font.path is not None:
                return font
        return RFont(path, showInterface=False)


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

        self.fontMasters = []
        for info in self.getFonts():
            font = info[0]
            fontname = os.path.relpath(font.path, self.path)
            fontname = fontname[3:]
            self.fontMasters += [dict(
                include=True,
                fontname=fontname,
                font=info[0],
                path=info[0].path,
                designSpacePosition=info[1],
                positionString=" ".join([str(position)+": "+str(info[1][position]) for position in info[1]])
                )]
        self._fontsLoaded = True

    def getOpenedFont(self, rowIndex):
        item = self.fontMasters[rowIndex]
        font = item.get("openedFont")
        return font

    def setOpenedFont(self, rowIndex):
        item = self.fontMasters[rowIndex]
        assert item.get("openedFont") is None, "font was already opened"
        item["openedFont"] = OpenFont(item["path"])

    def delOpenedFont(self, rowIndex):
        item = self.fontMasters[rowIndex]
        assert item.get("openedFont") is not None, "font is NoneType, cannot delete"
        del item["openedFont"]
