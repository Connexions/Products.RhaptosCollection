from Products.CMFCore.utils import getToolByName

types_to_fix = ['Collection','SubCollection','ContentPointer','PublishedContentPointer']

def fixArchetypesRightsField(self):
    """Fix a bug where courses have a None in the rights field instead of an empty string"""
    portal = getToolByName(self, 'portal_url').getPortalObject()
    
    for wg in portal.GroupWorkspaces.objectValues() + portal.Members.objectValues(['Plone Folder']) + portal.content.objectValues(['Version Folder']):
        _fix_subobjects(wg)

def _fix_rights(object):
    if type(object.rights) is type(None):
        storage = object.getField('rights').getStorage()
        storage.set('rights', object, '')	

def _fix_subobjects(object):
    for o in object.objectValues(types_to_fix):
        _fix_rights(o)
        _fix_subobjects(o)

def setCollectionTypeToCourse(self):
    """Since we are now allowing people to change the collectionType and
    making 'Collection' the new default, hardcode all old versions to 'Course'.
    
    Also change the title of the Collection FTI to 'Collection'.
    """
    portal = getToolByName(self, 'portal_url').getPortalObject()
    for wg in portal.GroupWorkspaces.objectValues() + portal.Members.objectValues():
        for col in wg.objectValues(['Collection']):
            if not col.getParameters().has_key('collectionType'):
                col.setCollectionType('Course')

    for col_folder in portal.content.objectValues(['Version Folder']):
        for col in col_folder.objectValues(['Collection']):
            if not col.getParameters().has_key('collectionType'):
                col.setCollectionType('Course')

    tt = getToolByName(self, 'portal_types')
    tt.Collection.title = 'Collection'
    tt.Collection.description = 'A collection is a grouping of related modules.'
                      


