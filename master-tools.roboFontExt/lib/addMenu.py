import os, sys
from AppKit import NSApp, NSMenuItem
from mojo.UI import MenuBuilder
from lib.UI.fileBrowser import RFPathItem

def add_menu(name, path):

    menubar = NSApp().mainMenu()
    newItem = menubar.itemWithTitle_(name)
    if not newItem:
        newItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(name, "", "")
        menubar.insertItem_atIndex_(newItem, menubar.numberOfItems()-1)
    recentList = []
    builder = MenuBuilder([])
    menu = builder.getMenu()
    menu.setTitle_(name)
    pathItem = RFPathItem(path, [".py"], isRoot=True)
    pathItem.getMenu(title=name, parentMenu=menu)
    newItem.setSubmenu_(menu)

menu_name = "master-tools"
libDir = os.getcwd()
sys.path.append(libDir)
scripts_path = os.path.join(libDir, 'masterToolsScripts')
add_menu(menu_name, scripts_path)
