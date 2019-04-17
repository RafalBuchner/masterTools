import os
import sys
from AppKit import NSApp, NSMenu, NSMenuItem
from lib.UI.fileBrowser import RFPathItem
import mojo

# from designspace editor by Letterror

DEVELOP = True

if DEVELOP:
    pathForBundle = os.path.dirname(__file__)
    #sys.path = list(set(sys.path))
    resourcePathForBundle = os.path.join(os.path.dirname(pathForBundle), "resources")
    masterToolsBundle = mojo.extensions.ExtensionBundle(path=pathForBundle, resourcesName=resourcePathForBundle)
else:
    masterToolsBundle = mojo.extensions.ExtensionBundle("master-tools")

####

def add_menu(name, path):
    # create a new menu
    menu = NSMenu.alloc().initWithTitle_(name)
    # create a path item that will build the menu and connect all the callbacks
    pathItem = RFPathItem(path, [".py"], isRoot=True)
    pathItem.getMenu(title=name, parentMenu=menu)
    # get the main menu
    menubar = NSApp().mainMenu()
    # search if the menu item already exists
    newItem = menubar.itemWithTitle_(name)
    if not newItem:
        # if not, create one and append it before `Help`
        newItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(name, "", "")
        menubar.insertItem_atIndex_(newItem, menubar.numberOfItems()-1)
    # set the menu as submenu
    newItem.setSubmenu_(menu)

menu_name = "masterTools-Beta"
libDir = os.getcwd()
sys.path.append(libDir)
scripts_path = os.path.join(libDir, 'masterToolsScripts')
add_menu(menu_name, scripts_path)
