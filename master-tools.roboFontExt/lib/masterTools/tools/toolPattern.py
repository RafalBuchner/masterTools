class ToolName(object):
    def __init__(self, designspace, toolBtn=None):
        self.designspace = designspace
        self.isActive = False
        
        if toolBtn is not None:
            self.toolBtn = toolBtn



    def start(self):
        self.initUI()
        # code goes here (if tool has a UI, you should add here self.window.open() )
        self.addObeservers()
        self.isActive = True

    def finish(self):
        if hasattr(self, "w"):
            if self.w._window is not None:
                self.w.close()
        self.removeObservers()
        self.isActive = False

    def addObeservers(self):
        pass

    def removeObservers(self):
        pass

    def initUI(self):
        pass

    def closeWindow(self, info):
        # binding to window
        self.removeObservers()
        self.isActive = False
        # resetting toolbar button status, when window is closed
        buttonObject = self.toolBtn.getNSButton()
        self.toolBtn.status = False
        buttonObject.setBordered_(False)

    # RF observers

    # code goes here

    # ui callbacks

    # code goes here

    # tool actions

    # code goes here
