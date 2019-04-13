from __future__ import print_function, division, absolute_import
from masterTools.UI.vanillaSubClasses import *
from masterTools.UI.glyphCellFactory import *
from masterTools.misc.masterSwitcher import *
from masterTools.features.masterCompatibilityTable import *

__all__ = [

    ]
def copy2clip(txt):
    from AppKit import NSPasteboard, NSStringPboardType
    pb = NSPasteboard.generalPasteboard()
    pb.declareTypes_owner_([NSStringPboardType],None)
    pb.setString_forType_(txt,NSStringPboardType)
__all__.append("copy2clip")
