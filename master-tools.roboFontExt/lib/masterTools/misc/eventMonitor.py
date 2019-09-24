import AppKit

_specialCases = [
    ("w", AppKit.NSCommandKeyMask),  # close window, dont subscribe afterwards
    ("s", AppKit.NSCommandKeyMask),  # close window, dont subscribe afterwards
    ("`", AppKit.NSCommandKeyMask),  # jump to next window, dont subscribe afterwards
    ("`", AppKit.NSCommandKeyMask | AppKit.NSShiftKeyMask),  # jump to prev window, don't subscribe afterwards
]

_specialKeys = {
    'cmd' : AppKit.NSCommandKeyMask,
    'shift' : AppKit.NSShiftKeyMask,
    'alt' : AppKit.NSAlternateKeyMask,
    'ctrl' : AppKit.NSControlKeyMask,
}

class KeyEventMonitor(object):
    
    '''
    arguments: bindings (dict)
        bindings = {
            keyStroke : action method
        }
        
        keyStroke = (baseKey, *specialkeys)
        baseKey = any key on the alphabetical/numerical keyboard
        specialkeys = 'cmd', 'shift', 'alt' or 'ctrl'

        action method = method or function that reacts to the shortcut

        '''
    def __init__(self, bindings):
        self.monitor = None
        self.bindings = bindings
        
    def subscribe(self):
        self.unsubscribe()
        self.monitor = AppKit.NSEvent.addLocalMonitorForEventsMatchingMask_handler_(AppKit.NSKeyDownMask, self.eventHandler)


    def unsubscribe(self):
        if self.monitor is not None:
            AppKit.NSEvent.removeMonitor_(self.monitor)
        self.monitor = None
    
    def eventHandler(self, event):
        inputKey = event.charactersIgnoringModifiers()
        eventModifiers = event.modifierFlags()
        
        # check if inputKey and eventModifiers match with your shortcuts
        found = False
        for hotkey in self.bindings:
            
            assert isinstance(hotkey, tuple)
            baseKey = hotkey[0]
            specialkeys = hotkey[1:]

            for keyName in specialkeys:
                eventModifiers &= _specialKeys[keyName]

            if inputKey == baseKey and eventModifiers:
                self.bindings[hotkey](hotkey)
                found = True
            

        if not found:
            self.unsubscribe()
            AppKit.NSApp().sendEvent_(event)
            if (inputKey, eventModifiers) not in _specialCases:
                # don't resubscribe when the window is closed
                self.subscribe()