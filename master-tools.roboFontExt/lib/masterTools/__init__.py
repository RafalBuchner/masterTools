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
# from masterTools.misc.MasterToolsProcessor import *
# from masterTools.misc.MTMath import *
from masterTools.tools.masterCompatibilityTable import *

def copy2clip(txt):
    from AppKit import NSPasteboard, NSStringPboardType
    pb = NSPasteboard.generalPasteboard()
    pb.declareTypes_owner_([NSStringPboardType],None)
    pb.setString_forType_(txt,NSStringPboardType)

def getDev():
    return DEVELOP
__all__ = [ "copy2clip", "getDev", ]
####


########
# test #
########

if __name__ == "__main__":
    from masterTools.UI.designSpaceWindow import DesignSpaceWindow
    from mojo.UI import OutputWindow
    from mojo.roboFont import OpenWindow
    ow = OutputWindow()
    ow.clear()
    ow.show()
    o = OpenWindow(DesignSpaceWindow)


    from vanilla import HUDFloatingWindow, Window
    from random import random

    # class ListDemo(object):
    #     def __init__(self):
    #         self.w = Window((200, 200))
    #         columnDescriptions = [{"title": "One","font":NSFont.systemFontOfSize_(12)},
    #                               {"title": "Two","textColor":((0,1,0,1)),"font":("AndaleMono",12),"alignment":"right"},
    #                               {"title": "Three","textColor":((0,1,0,1)),"font":("AndaleMono",12),"alignment":"right"},
    #                               {"title": "Four","textColor":((0,1,0,1)),"font":("AndaleMono",12),"alignment":"right"},
    #                               ]
    #         self.w.myList = MTList((20, 20, -20, -40),
    #                      [{"One": "A", "Two": "a", "Three":"C","Four":"D"},
    #                       {"One": "B", "Two": "b", "Three":"c","Four":"d"}],
    #                      columnDescriptions=columnDescriptions,
    #                      rowHeight=30,transparentBackground=True,
    #                      selectionCallback=self.selectionCallback )
    #         self.myDelegate = MTTableDelegate.alloc().init()
    #         table = self.w.myList.getNSTableView()
    #
    #         self.w.open()
    #     def selectionCallback(self, sender):
    #         cellDescription = {
    #               (0,0):CheckBoxListCell("dupa")
    #             }
    #         self.w.myList.setCellHighlighting(cellDescription)
    #
    #
    # ListDemo()

    class ListDemo(object):
        def __init__(self):

            columnDescriptions = [{"title": "One","font":NSFont.systemFontOfSize_(12)},{"title": "Two","textColor":((0,1,0,1)),"font":("AndaleMono",12),"alignment":"right"},{"title": "Three","textColor":((0,1,0,1)),"font":("AndaleMono",12),"alignment":"right"},{"title": "Four","textColor":((0,1,0,1)),"font":("AndaleMono",12),"alignment":"right"},]

            self.w = FloatingWindow((400, 700), minSize=(100,100))
            self.w.list = MTList(
                            (0,0,-0,-0),
                            [{"One": "A", "Two": "a", "Three":"C","Four":"D"},
                            {"One": "B", "Two": "b", "Three":"c","Four":"d"}],# test
                            rowHeight=250,
                            columnDescriptions=columnDescriptions,
                            selectionCallback=self.selectionCallback
            )
            self.w.open()
        def selectionCallback(self, sender):
            path = '/Users/rafalbuchner/Dropbox/tests/Book-Rafal-03.ufo'
            # path = '/Users/rafalbuchner/Documents/repos/work/+GAMER/gamer/+working_files/regular/G-Re-Medium-02.ufo'
            font = OpenFont(path, False)
            glyph=GlyphCellFactory(font['a'], 20,   20, glyphColor=NSColor.blackColor())
            print(type(glyph))
            cellDescription = {
                  (0,0):glyph
                }
            self.w.list.setCellHighlighting(cellDescription)
    ListDemo()





