from mojo.extensions import ExtensionBundle
from masterTools.UI.vanillaSubClasses import *
from masterTools.UI.glyphCellFactory import *
from vanilla import *
def getBundle():
    import sys, os
    currpath = os.path.join( os.path.dirname( __file__ ), '' )
    sys.path.append(currpath)
    sys.path = list(set(sys.path))
    pathForBundle = os.path.abspath(os.path.join(__file__ ,"../.."))
    resourcePathForBundle = os.path.join(pathForBundle, "resources")
    bundle = ExtensionBundle(path=pathForBundle, resourcesName=resourcePathForBundle)
    return bundle
bundle = getBundle()

kink_icon        = bundle.getResourceImage("kink-icon", ext='pdf')
glyphs_icon      = bundle.getResourceImage("glyphs-icon", ext='pdf')
problem_icon     = bundle.getResourceImage("problem-icon", ext='pdf')
settings_icon    = bundle.getResourceImage("settings-icon", ext='pdf')
closeIcon        = bundle.getResourceImage("close-icon", ext='pdf')
closed_font_icon = bundle.getResourceImage("closed-font-icon", ext='pdf')
opened_font_icon = bundle.getResourceImage("opened-font-icon", ext='pdf')

class ListDemo(object):
    def __init__(self):

        path = '/Users/rafaelbuchner/Downloads/Anaheim/new/Anaheim-Regular BB17.ufo'
        # path = '/Users/rafalbuchner/Documents/repos/work/+GAMER/gamer/+working_files/regular/G-Re-Medium-02.ufo'
        font = OpenFont(path, False)
        glyph=GlyphCellFactory(font['g'], 50,   50, glyphColor=NSColor.blackColor())
        columnDescriptions = [{"title": "One","font":NSFont.systemFontOfSize_(12),'image':glyph},{"title": "Two","textColor":((0,1,0,1)),"font":("AndaleMono",12),"alignment":"right"},{"title": "Three","textColor":((0,1,0,1)),"font":("AndaleMono",12),"alignment":"right"},{"title": "Four","textColor":((0,1,0,1)),"font":("AndaleMono",12),"alignment":"right"},]

        self.w = FloatingWindow((400, 700), minSize=(100,100))
        self.w.list = MTList(
                        (0,0,-0,-0),
                        [{"One": "A", "Two": "a", "Three":"C","Four":"D"},
                        {"One": "B", "Two": "b", "Three":"c","Four":"d"}],
                        columnDescriptions=columnDescriptions,
                        selectionCallback=self.selectionCallback,
                        headerHeight=50
                        # transparentBackground=True
        )
        # tv = self.w.list.getNSTableView()

        # c1,c2,c3,c4 = tv.tableColumns()
        # c2.headerCell().setImage_(glyph)
        # # help(c1.headerCell())
        
        self.w.open()

    def selectionCallback(self, sender):
        tv = self.w.list.getNSTableView()
        c1,c2,c3,c4 = tv.tableColumns()
        print(c2.headerCell().imageRectForBounds_())
        # help(c1.headerCell())
        # print(c1.headerCell().cellSize(), c1.headerCell().controlView())
        # print(c2.headerCell().cellSize())
        # print(c3.headerCell().cellSize())

       
ListDemo()