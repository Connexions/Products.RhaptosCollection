## event handling: Zope 3-style event management
from Products.CMFCore.utils import getToolByName

def collectionContentsModified(obj, evt):
    """When SubCollections or ContentPointers are updated, tell the containing Collection
    it is modified
    """
    factorytool = getToolByName(obj, 'portal_factory')
    col = obj.nearestCourse()
    if col.state not in ('published') and not factorytool.isTemporary(obj) and not col.doingMassUpdate():
        col.logAction('save')