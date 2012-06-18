from zope.interface import implements

from Products.Archetypes.public import BaseSchema, Schema
from Products.Archetypes.public import registerType
from Products.Archetypes.public import StringField
from Products.RhaptosCollection.Widget import CompactStringWidget

from CollectionBase import CollectionBase
from Products.RhaptosCollection.interfaces import ICollectionContained

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.Expression import Expression

import zLOG
def log(msg, severity=zLOG.INFO):
    zLOG.LOG("RhaptosCollection: SubCollection", severity, msg)

schema = BaseSchema +  Schema((
    StringField('title',
                default='(Untitled)',
                searchable=1,
                required=1,
                widget=CompactStringWidget(description='Enter a descriptive title for the section.',
                                           i18n_domain="rhaptos"),
                ),
    ))
    
class SubCollection(CollectionBase):
    """A collection of objects
    """
    implements(ICollectionContained)
    archetype_name = 'Section'
    allowed_content_types = ['ContentPointer', 'PublishedContentPointer', 'SubCollection']

    schema = schema

    actions = (
               {'id': 'view',
                'title': 'Contents',
                'action': Expression('string:${object_url}/collection_composer'),
                'permissions': (CMFCorePermissions.View,)},
               {'id': 'edit',
                'title': 'Edit',
                'action': Expression('string:${object_url}/collection_composer?panel=base_edit'),
                'permissions': (CMFCorePermissions.ModifyPortalContent,)},
             )

    aliases = {
        '(Default)'  : '',
        'edit'       : 'base_edit',
        'gethtml'    : '',
        'index.html' : '',
        'properties' : '',
        'sharing'    : '',
        'view'       : 'collection_composer',
        }

    def isGroup(self):
        return 1 # our contract for "chapters": existence of the method proves groupness

    def _notifyOfCopyTo(self, container, op=0):
        """Let Zope know that we can't be pasted just anywhere"""

        if not isinstance(container, CollectionBase):
            raise "Bad Request", "Module references can only occur inside courses"

registerType(SubCollection)
