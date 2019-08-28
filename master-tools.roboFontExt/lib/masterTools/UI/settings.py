# from ..masterTools import getDev
import AppKit
from mojo.extensions import ExtensionBundle
from vanilla import *
from pprint import pprint
from masterTools.UI.vanillaSubClasses import MTDialog
from masterTools.UI.glyphCellFactory import GlyphCellFactory
from mojo.extensions import setExtensionDefault, getExtensionDefault, ExtensionBundle
from vanilla.vanillaBase import osVersionCurrent, osVersion10_14
# print(masterTools.UI.vanillaSubClasses)
# if getDev():
import sys
import os
currpath = os.path.join(os.path.dirname(__file__), '../..')
sys.path.append(currpath)
sys.path = list(set(sys.path))
pathForBundle = os.path.abspath(os.path.join(__file__, "../../../.."))
resourcePathForBundle = os.path.join(pathForBundle, "resources")
bundle = ExtensionBundle(path=pathForBundle, resourcesName=resourcePathForBundle)
# else:
#     bundle = ExtensionBundle("master-tools")

empty_glyph_cell_100x100 = bundle.getResourceImage("empty-glyph-cell-100x100", ext='pdf')
empty_glyph_cell_50x50 = bundle.getResourceImage("empty-glyph-cell-100x100", ext='pdf')

key = "com.rafalbuchner.MasterTools"
"""TODO
> set preview letter for masters

> divide the settings into global (GUI) and local,
that can be changed right after the closing the settingsPanel

"""


class Settings(object):
    defaultColors = [(0.9, 0.1, 0.29),
                           (0.24, 0.71, 0.29),
                           (1.0, 0.88, 0.1),
                           (0.0, 0.51, 0.78),
                           (0.96, 0.51, 0.19),
                           (0.57, 0.12, 0.71),
                           (0.27, 0.94, 0.94),
                           (0.94, 0.2, 0.9),
                           (0.82, 0.96, 0.24),
                           (0.98, 0.75, 0.75),
                           (0.0, 0.5, 0.5),
                           (0.9, 0.75, 1.0),
                           (0.67, 0.43, 0.16),
                           (1.0, 0.98, 0.78),
                           (0.5, 0.0, 0.0),
                           (0.67, 1.0, 0.76),
                           (0.5, 0.5, 0.0),
                           (1.0, 0.84, 0.71),
                           (0.0, 0.0, 0.5),
                           (0.5, 0.5, 0.5),
                           ]
    darkBackground = (0.1513, 0.1513, 0.1513, 1)

    def __init__(self):

        self.currentDesignspacePath = None
        self.recentDesignspacePaths = []

        self.__default = (
            dict(
                darkMode=False,
                restoreLastDesignSpace=False,
                previewGlyphName="a",
                lastDesignspace=None,
                masterColors=self.defaultColors
            )
        )
        self.__dict = self.__default  # for now
        if getExtensionDefault(key) is not None:
            for setting in self.__dict:
                if setting in getExtensionDefault(key).keys():
                    self.__dict[setting] = getExtensionDefault(key)[setting]


    def getDict(self):
        return self.__dict

    ############
    # PANEL
    ############
    def closeSettingsPanel(self):
        if self.currentDesignspacePath is not None:
            self.__dict['lastDesignspace'] = self.currentDesignspacePath
        self.__dict['recentDesignspacePaths'] = self.recentDesignspacePaths
        setExtensionDefault(key, self.__dict)

    def settingsPanel(self, parentWindow, startY=None):
        txtH, btnH = MTDialog.txtH, MTDialog.btnH
        x, y, p = MTDialog.padding
        px, py, pw, ph = parentWindow.getPosSize()

        offset = 0
        if startY is not None:
            offset -= startY

        sGroup = Group((0, 0, pw, ph + offset))
        self.c1 = Group((0, 0, pw / 2 + p / 2, ph + offset))
        self.c2 = Group((pw / 2, 0, pw / 2 - p / 2, ph + offset))

        if startY is None:
            y = p
            yc2 = p
        else:
            y = startY
            yc2 = startY
        #############
        # column 1
        #############
        # darkModeOption
        self.c1.darkMode_obj = CheckBox((x, y, -p, btnH),
                                        "dark mode",
                                        callback=self.checkboxCallback)
        self.c1.darkMode_obj.id = "darkMode"

        self.updateSavedSettingsInThePanel(self.c1.darkMode_obj)

        y += btnH + p

        self.c1.restoreLastDesignSpace_obj = CheckBox((x, y, -p, btnH),
                                                      "open last designspace at start",
                                                      callback=self.checkboxCallback)
        self.c1.restoreLastDesignSpace_obj.id = "restoreLastDesignSpace"
        self.updateSavedSettingsInThePanel(self.c1.restoreLastDesignSpace_obj)

        y += btnH + p

        #############
        # column 2
        #############
        y = yc2  # resetting y value for item placements

        self.c2.previewGlyphName_title = TextBox((x, y, -p, btnH), "preview glyph name")
        y += btnH + p

        self.c2.previewGlyphName_obj = EditText((x, y, -p, btnH),
                                                callback=self.editTextCallback)
        self.c2.previewGlyphName_obj.id = "previewGlyphName"
        self.updateSavedSettingsInThePanel(self.c2.previewGlyphName_obj)

        ############
        # updating
        ############
        # updating the values from dict:
        # self.updateSavedSettingsInThePanel()

        sGroup.c1 = self.c1
        sGroup.c2 = self.c2
        parentWindow.group = sGroup

    def updateSavedSettingsInThePanel(self, obj):
        title = obj.id
        settingValue = self.__dict.get(title)

        if isinstance(obj, PopUpButton):
            if isinstance(settingValue, str):
                obj.setTitle(settingValue)

        if isinstance(obj, CheckBox):
            if isinstance(settingValue, int) or isinstance(settingValue, bool):
                obj.set(settingValue)

        if isinstance(obj, EditText):
            if isinstance(settingValue, str):
                obj.set(settingValue)

    def editTextCallback(self, sender):
        value = sender.get()
        self.__dict[sender.id] = value

    def popUpCallback(self, sender):
        index = sender.get()
        value = sender.getItems()[index]
        self.__dict[sender.id] = value

    def checkboxCallback(self, sender):
        trueFalse = sender.get()
        value = False
        if trueFalse == 1:
            value = True
        self.__dict[sender.id] = value

    #####
    # global functions / actions
    #####
    # def getRecentDesignspacePaths(self):
    #     self.recentDesignspacePaths = self.__dict.get('recentDesignspacePaths', [])
    #     print('>>> ', self.recentDesignspacePaths)
    #     return list(reversed(self.recentDesignspacePaths))

    def setRecentDesignspacePaths(self, path):
        self.currentDesignspacePath = path
        if path not in self.recentDesignspacePaths:
            self.recentDesignspacePaths.append(path)
        else:
            self.recentDesignspacePaths.append(
                    self.recentDesignspacePaths.pop(
                        self.recentDesignspacePaths.index(path)
                        )
                ) 
        if len(self.recentDesignspacePaths) > 10:
            self.recentDesignspacePaths.pop(0)

    def getGlyphCellPreview_inFont(self, font, size=(100, 100), glyphColor=None):
        '''
            returns preview glyph based on previewGlyphName
            if it cannot find previewGlyphName in the font, it tries
            to looks for the closest glyph in font
        '''
        if glyphColor is None:
            glyphColor = self.getGlyphColor_forCurrentMode()
        if size == (100, 100):
            glyphcell = empty_glyph_cell_100x100
        elif size[1] == 40:
            glyphcell = empty_glyph_cell_50x50
        else:
            glyphcell = None
        width, height = size
        glyphExampleName = self.__dict["previewGlyphName"]
        # system for finding representation glyph in the master list
        if glyphExampleName in font.keys():
            glyphcell = GlyphCellFactory(
                font[glyphExampleName], width, height, glyphColor=glyphColor, bufferPercent=.01)

        elif glyphExampleName[0].upper() + glyphExampleName[1:] in font.keys() and glyphcell in (empty_glyph_cell_100x100, empty_glyph_cell_50x50):
            glyphcell = GlyphCellFactory(font[glyphExampleName[0].upper(
            ) + glyphExampleName[1:]], width, height, glyphColor=glyphColor, bufferPercent=.01)

        elif glyphExampleName[0].lower() + glyphExampleName[1:] in font.keys() and glyphcell in (empty_glyph_cell_100x100, empty_glyph_cell_50x50):
            glyphcell = GlyphCellFactory(font[glyphExampleName[0].lower(
            ) + glyphExampleName[1:]], width, height, glyphColor=glyphColor, bufferPercent=.01)
        else:
            if len(font.keys()) > 0 and glyphcell in (empty_glyph_cell_100x100, empty_glyph_cell_50x50):
                glyphWithContoursFound = False
                for glyph in font:
                    if len(glyph) > 0:
                        glyphWithContoursFound = True
                        glyphcell = GlyphCellFactory(
                            glyph, width, height, glyphColor=glyphColor, bufferPercent=.01)
                        break
                if not glyphWithContoursFound:
                    glyphcell = GlyphCellFactory(
                        font[font.keys()[0]], width, height, glyphColor=glyphColor, bufferPercent=.01)
        return glyphcell

    def getGlyphColor_forCurrentMode(self):
        glyphColor = AppKit.NSColor.secondaryLabelColor()
        if osVersionCurrent >= osVersion10_14 and self.__dict["darkMode"]:
            # maybe shitty way, but works…
            glyphColor = AppKit.NSColor.whiteColor()
        return glyphColor
