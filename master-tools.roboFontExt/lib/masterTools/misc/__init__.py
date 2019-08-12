
def copy2clip(txt):
    from AppKit import NSPasteboard, NSStringPboardType
    pb = NSPasteboard.generalPasteboard()
    pb.declareTypes_owner_([NSStringPboardType],None)
    pb.setString_forType_(txt,NSStringPboardType)
    
DEVELOP = True
def getDev():
    return DEVELOP