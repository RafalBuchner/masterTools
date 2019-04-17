class Settings(object):
    def __init__(self):
        self.__default = (
            dict(
            darkMode=False


            )

        )
        self.__dict = self.__default # for now

    def getDict(self):
        return self.__dict
