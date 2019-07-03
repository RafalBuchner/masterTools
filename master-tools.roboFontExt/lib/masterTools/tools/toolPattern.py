class ToolName(object):
    def __init__(self, designspace):
        self.designspace = designspace
        self.isActive = False


    def start(self):
        self.initUI()
        # code goes here (if tool has a UI, you should add here self.window.open() )
        self.addObeservers()
        self.isActive = True

    def finish(self):
        if hasattr(self, "window"):
            self.window.close()
        # code goes here (if tool has a UI, you should add here self.window.close() )
        self.removeObservers()
        self.isActive = False

    def addObeservers(self):
        pass

    def removeObservers(self):
        pass

    def initUI(self):
        pass

    def closeUI(self):
        # binding to window
        self.finish()
    # RF observers

    # code goes here

    # ui callbacks

    # code goes here

    # tool actions

    # code goes here
