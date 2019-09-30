from __future__ import print_function, division, absolute_import

######################################################
######################################################
######################################################
# testing:

if __name__ == '__main__':
    import sys,os
    from AppKit import NSApp, NSMenu, NSMenuItem
    from mojo.UI import MenuBuilder
    from lib.UI.fileBrowser import RFPathItem
    from mojo.roboFont import OpenWindow
    currpath = os.path.join( os.path.dirname( __file__ ), '..' )
    sys.path.append( currpath )
    sys.path = list(set(sys.path))
    pathForBundle = os.path.abspath(os.path.join(__file__ ,"../../.."))    ####
    from masterTools.UI.designSpaceWindow import DesignSpaceWindow
    from masterTools.UI.settings import Settings
    __uiSettingsController = Settings()
    __uiSettings = __uiSettingsController.getDict()

    # def add_menu(name, path):
    #     menu = NSMenu.alloc().initWithTitle_(name)
    #     pathItem = RFPathItem(path, [".py"], isRoot=True)
    #     pathItem.getMenu(title=name, parentMenu=menu)
    #     menubar = NSApp().mainMenu()
    #     newItem = menubar.itemWithTitle_(name)
    #     if not newItem:
    #         newItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(name, "", "")
    #         menubar.insertItem_atIndex_(newItem, menubar.numberOfItems()-1)
    #     newItem.setSubmenu_(menu)
    def _openRecentCallback(sender):
            path = sender.getTitle()
            DSW = OpenWindow(DesignSpaceWindow)

            DSW.loadDesignSpaceFile(path)

    def add_menu(name, path):
 
        menubar = NSApp().mainMenu()
        newItem = menubar.itemWithTitle_(name)
        if not newItem:
            newItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(name, "", "")
            menubar.insertItem_atIndex_(newItem, menubar.numberOfItems()-1)
        recentList = []
        
        builder = MenuBuilder([('open recent',[])])
        menu = builder.getMenu()
        menu.setTitle_(name)
        pathItem = RFPathItem(path, [".py"], isRoot=True)
        pathItem.getMenu(title=name, parentMenu=menu)
        newItem.setSubmenu_(menu)

    menu_name = "masterTools-Dev"
    libDir = os.path.join( os.path.dirname( __file__ ), '..' )
    sys.path.append(libDir)
    scripts_path = os.path.join(libDir, 'masterToolsScripts')
    add_menu(menu_name, scripts_path)


    masterToolMenu = None
    openRecentMenu = None
    for item in NSApp().mainMenu().itemArray():
        if 'master' in item.title().lower() and 'tools' in item.title().lower():
            masterToolMenu = item
            break
    if masterToolMenu is not None:
        for item in masterToolMenu.submenu().itemArray():
            if 'open recent' == item.title().lower():
                openRecentMenu = item
                break
    openRecentMenu.submenu().setAutoenablesItems_(False)
    for path in __uiSettings.getRecentDesignspacePaths():
        openRecentMenu.submenu().addItemWithTitle_action_keyEquivalent_(path,'_openRecentCallback','')
######################################################
######################################################
######################################################
from masterTools.UI.vanillaSubClasses import *

from masterTools.UI.settings import Settings
from masterTools.misc.masterSwitcher import *
# from masterTools.misc.MasterToolsProcessor import *
# from masterTools.misc.MTMath import *
from masterTools.tools.masterCompatibilityTable import *



# __all__ = [ "copy2clip", "getDev", ]
####


########
# test #
########

if __name__ == "__main__":
    from masterTools.UI.designSpaceWindow import DesignSpaceWindow
    from mojo.roboFont import OpenWindow
    from mojo.UI import OutputWindow
    ow = OutputWindow()
    ow.clear()
    ow.show()
    o = OpenWindow(DesignSpaceWindow)

    ### test
    # from vanilla import *
    # from random import random
    # class ListDemo(object):

    #     def __init__(self):
    #         self.w = Window((500, 300),minSize=(100,100))
    #         self.w.l = MTList((0, 0, -0, -100),
    #                      [{"One": "A", "Two": "a", 'Three':'0', 'Four':'0a'}, {"One": "B", "Two": "b", "Three": "1", 'Four':'0a'}, {"One": "C", "Two": "c", "Three": "2", 'Four':'0a'},{"One": "D", "Two": "d", "Three": "3", 'Four':'0a'}],
    #                      columnDescriptions=[{"title": "One"}, {"title": "Two"}, {'title': 'Three'}, {'title': 'Four'}],
    #                      rowHeight=20,
    #                      # highlightDescriptions={(i,j) : (random(),random(),random())  for i in range(9) for j in range(9)}
    #                      )

            
            
    #         self.w.l.setCellHighlighting({
    #             (i,j) : (random(),random(),random())  for i in range(9) for j in range(9)
    #             })

    #         t = self.w.l.getNSTableView()

    #         columnIndex = 2
    #         highlightDescriptions = self.w.l.getHighlightDescriptions()
    #         for i in range(t.numberOfRows()):
    #             highlightDescriptions[(columnIndex,i)] = (0,.3,1,.4)
    #         self.w.l.setCellHighlighting(highlightDescriptions)
            # self.w.open()


        


    # ListDemo()
