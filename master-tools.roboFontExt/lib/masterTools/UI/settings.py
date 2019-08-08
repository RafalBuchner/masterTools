from vanilla import *
from masterTools.UI.vanillaSubClasses import MTDialog
from mojo.extensions import setExtensionDefault, getExtensionDefault
key = "com.rafalbuchner.MasterTools"
"""TODO
> set preview letter for masters

> divide the settings into global (GUI) and local,
that can be changed right after the closing the settingsPanel

"""
class Settings(object):
    defaultMasterColors = [(0.9, 0.1, 0.29),
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
    def __init__(self):

        self.currentDesignspacePath = None

        self.__default = (
            dict(
            darkMode=False,
            restoreLastDesignSpace=False,
            previewGlyphName="a",
            lastDesignspace=None,
            masterColors=self.defaultMasterColors
            )
        )
        self.__dict = self.__default # for now
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
        setExtensionDefault(key, self.__dict)

    def settingsPanel(self,parentWindow,startY=None):
        txtH,btnH = MTDialog.txtH, MTDialog.btnH
        x,y,p = MTDialog.padding
        px,py,pw,ph = parentWindow.getPosSize()

        offset = 0
        if startY is not None:
            offset -= startY

        sGroup = Group((0,0,pw,ph+offset))
        self.c1 = Group((0,0,pw/2+p/2,ph+offset))
        self.c2 = Group((pw/2,0,pw/2-p/2,ph+offset))

        if startY is None:
            y = p
            yc2 = p
        else:
            y = startY
            yc2 = startY
        #############
        ## column 1
        #############
        ## darkModeOption
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
        ## column 2
        #############
        y = yc2 #resetting y value for item placements

        self.c2.previewGlyphName_title = TextBox((x, y, -p, btnH),"preview glyph name")
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


    def editTextCallback(self,sender):
        value = sender.get()
        self.__dict[sender.id] = value

    def popUpCallback(self,sender):
        index = sender.get()
        value = sender.getItems()[index]
        self.__dict[sender.id] = value

    def checkboxCallback(self,sender):
        trueFalse = sender.get()
        value = False
        if trueFalse == 1:
            value = True
        self.__dict[sender.id] = value
        # print(self.__dict)




