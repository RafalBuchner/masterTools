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
    def __init__(self):
        self.__default = (
            dict(
            darkMode=False


            )

        )
        if getExtensionDefault(key) is None:
            self.__dict = self.__default # for now
        else:
            self.__dict = getExtensionDefault(key)

    def getDict(self):
        return self.__dict





    ############
    # PANEL
    ############
    def closeSettingsPanel(self):
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
        self.darkModeOptions = ["dark mode","light mode"]
        self.c1.darkMode_obj = PopUpButton((x, y, -p, btnH),
                              self.darkModeOptions,
                              callback=self.darkModeCallback)
        self.c1.darkMode_obj.title = "darkMode"
        self.updateSavedSettingsInThePanel(self.c1.darkMode_obj)

        #############
        ## column 2
        #############
        y = yc2 #resetting y value for item placements


        ############
        # updating
        ############
        # updating the values from dict:
        # self.updateSavedSettingsInThePanel()

        sGroup.c1 = self.c1
        sGroup.c2 = self.c2
        parentWindow.group = sGroup


    def updateSavedSettingsInThePanel(self, obj):
        if obj is not None:
            title = obj.title
            settingValue = self.__dict[title]
            if isinstance(obj, PopUpButton):
                obj.setTitle(settingValue)




    def darkModeCallback(self,sender):
        name = self.darkModeOptions[sender.get()]
        value = False
        if name == "dark mode":
            value = True
        self.__dict["darkMode"] = value
