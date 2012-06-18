from Products.Archetypes.public import Schema
from Products.Archetypes.public import registerType
from Products.Archetypes.public import ReferenceWidget

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName

from BaseContentPointer import BaseContentPointer
from BaseContentPointer import schema as BaseSchema
from Products.RhaptosCollection.Field import WorkspaceReferenceField

import zLOG
def log(msg, severity=zLOG.INFO):
    zLOG.LOG("RhaptosCollection: ContentPointer", severity, msg)

schema = BaseSchema + Schema((
    WorkspaceReferenceField('module',
                allowed_types=('Module'),
                relationship='is',
                required=0,
                widget=ReferenceWidget(label="Module in Workspace",
                                       modes=('view',))
                ),
    ))

class ContentPointer(BaseContentPointer):
    """A sort of symbolic link to an external resource
    (specifically a RhaptosModuleEditor.)
    """
    archetype_name = 'Workspace Module Reference'

    schema = schema

    aliases = {
        '(Default)'  : 'view',
        'edit'       : '',
        'gethtml'    : '',
        'index.html' : '',
        'properties' : '',
        'sharing'    : '',
        'view'       : 'view',
        }

    def isModule(self):
        return 1 # our contract for "modules"

    def computedTitle(self):
        try:
            module_title = self.getContent().title
        except AttributeError, e:
            module_title = "broken"
            #log(e)
        return self.getOptionalTitle() or module_title

    def moduleLocation(self):
        m = self.getContent()
        if m:
            return m.absolute_url()
        else:
            return ""
        
    def getContent(self):
        """Return the actual object at which this object "points"."""
        return getToolByName(self, 'archetype_tool').getObject(self.getModule())

    def getModuleId(self):
        """Return the ID of the object which this object "points"."""
        return self.getContent().getId()

registerType(ContentPointer)
