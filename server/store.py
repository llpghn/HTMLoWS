"""
Dummy store in dem alle Daten gespeichert werden. Soll mit auf der Flux-Architektur aufbauen.
"""

class Store:
    store = {}

    def __init__(self):
        print("Create Store")

    def set(self, key, value):
        self.store[key] = value

    def get(self, key):
        if key in self.store:
            return self.store[key]
        return False

    def getall(self):
        return self.store


    def checkKey(self, key):
        if key in self.store:
            return True
        else:
            return False