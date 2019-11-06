

def kGetPlaylistPlayers():
    return tuple()

def kGetVideoPlayers():
    return tuple()

class dummy_category_object(object):
    id = 1
    name = 'foo'
    def getId(self):
        return self.id
    def getName(self):
        return self.name

def kGetCategories(parent=None):
    obj = dummy_category_object()
    obj2 = dummy_category_object()
    obj2.id = 2
    obj2.name = 'bar'
    return [obj, obj2]

def kGetCategoryId(categoryName):
    return "fake id"

