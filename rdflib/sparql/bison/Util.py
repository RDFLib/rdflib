class ListRedirect(object):
    """
    A utility class for lists of items joined by an operator.  ListRedirects with length 1
    are a special case and are considered equivelant to the item instead of a list containing it.
    The reduce function is used for normalizing ListRedirect to the single item (and calling reduce on it recursively)
    """
    reducable = True
    def __getattr__(self, attr):
        if hasattr(self._list, attr):
            return getattr(self._list, attr)
        raise AttributeError, '%s has no such attribute %s' % (repr(self), attr)
    
    def reduce(self):
        if self.reducable and len(self._list) == 1:
            singleItem = self._list[0]
            if isinstance(singleItem,ListRedirect):
                return singleItem.reduce()
            else:
                return singleItem
        else:
            return type(self)([isinstance(item,ListRedirect) and item.reduce() or item for item in self._list])

#Utility function for adding items to the front of a list
def ListPrepend(item,list):
    #print "adding %s to front of %s"%(item,list)
    return [item] + list