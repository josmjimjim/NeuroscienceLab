from threading import Lock

class SingletonMeta(type):
    """
    This is a thread-safe implementation of Singleton.
    """
    _instances = {}

    _lock: Lock = Lock()
    """
    We now have a lock object that will be used to synchronize threads during
    first access to the Singleton.
    """

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]

class Singleton(metaclass=SingletonMeta):

    def __init__(self, value = None, value_mean = None, url = None) :
        self.value = value
        self.value_mean = value_mean
        self.url = url

    def getData(self):
        return self.value, self.value_mean

    def getUrl(self):
        return self.url

    def hasData(self):
        if self.value == None:
            return False
        else:
            return True

    def hasUrl(self):
        if self.url == None:
            return False
        else:
            return True

    def loadData(self, data, data_mean):
        self.value = data
        self.value_mean = data_mean

    def loadUrl(self, url):
        self.url = url



if __name__ == "__main__":
    import pandas as pd

    d = {'col1': [1, 2], 'col2': [3, 4]}
    obj = pd.DataFrame(data=d)

    x = Singleton()
    y = Singleton('eggs')
    z = Singleton('spam')
    z.loadData(obj)
    z.loadUrl('tetettee')
    print(x.value)
    print(y.value)
    print(z.getData())
    print(z.hasData())
    print(x is y is z)