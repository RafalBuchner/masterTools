from AppKit import NSApp

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
def cb():
    print('cb')
openRecentMenu.submenu().addItemWithTitle_action_keyEquivalent_('blabla','cb','')
openRecentMenu.submenu().setAutoenablesItems_(False)
            