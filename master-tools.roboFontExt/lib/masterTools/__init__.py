from __future__ import print_function, division, absolute_import
import importlib
import mojo

######################################################
######################################################
######################################################
# testing:
DEVELOP = True
if __name__=='__main__':
    import sys,os
    from AppKit import NSApp, NSMenu, NSMenuItem
    from lib.UI.fileBrowser import RFPathItem
    currpath = os.path.join( os.path.dirname( __file__ ), '..' )
    sys.path.append(currpath)
    sys.path = list(set(sys.path))
    pathForBundle = os.path.abspath(os.path.join(__file__ ,"../../.."))    ####
    def add_menu(name, path):
        menu = NSMenu.alloc().initWithTitle_(name)
        pathItem = RFPathItem(path, [".py"], isRoot=True)
        pathItem.getMenu(title=name, parentMenu=menu)
        menubar = NSApp().mainMenu()
        newItem = menubar.itemWithTitle_(name)
        if not newItem:
            newItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(name, "", "")
            menubar.insertItem_atIndex_(newItem, menubar.numberOfItems()-1)
        newItem.setSubmenu_(menu)
    menu_name = "masterTools-BetaDev"
    libDir = os.path.join( os.path.dirname( __file__ ), '..' )
    sys.path.append(libDir)
    scripts_path = os.path.join(libDir, 'masterToolsScripts')
    add_menu(menu_name, scripts_path)
######################################################
######################################################
######################################################




from masterTools.UI.vanillaSubClasses import *
from masterTools.UI.glyphCellFactory import *
from masterTools.UI.settings import Settings
from masterTools.misc.masterSwitcher import *
from masterTools.features.masterCompatibilityTable import *






def copy2clip(txt):
    from AppKit import NSPasteboard, NSStringPboardType
    pb = NSPasteboard.generalPasteboard()
    pb.declareTypes_owner_([NSStringPboardType],None)
    pb.setString_forType_(txt,NSStringPboardType)



def getDev():
    return DEVELOP
__all__ = [ "copy2clip", "getDev", ]



####


