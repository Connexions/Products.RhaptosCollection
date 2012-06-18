from Products.Archetypes.public import Schema
from Products.Archetypes.public import registerType
from Products.Archetypes.public import DisplayList
from Products.Archetypes.public import StringField, ComputedField
from Products.Archetypes.public import StringWidget, ComputedWidget

from Products.CMFCore import CMFCorePermissions

from BaseContentPointer import BaseContentPointer
from BaseContentPointer import schema as BaseSchema
from Products.RhaptosCollection.Field import VersionField
from Products.RhaptosCollection.Widget import VersionWidget
from Products.RhaptosCollection.Widget import CompactStringWidget, CompactSelectionWidget, URLWidget

import zLOG

schema = BaseSchema + Schema((
    StringField('moduleId',
                required=0,
                searchable=0,
                default='',
                widget=CompactStringWidget(modes=('view',),
                                           label="Module ID",
                                           i18n_domain="rhaptos"),
                #validators=('isModuleNumber',),
                ),
    ComputedField('repositoryLocation',
                searchable=0,
                expression='context.moduleLocation()',
                widget=URLWidget(modes=('view',),
                                 label=('Published Location'),
                                 i18n_domain="rhaptos"),
                ),
    ComputedField('moduleTitle',
                searchable=0,
                expression='context.getContent().title',
                widget=CompactStringWidget(label="Module Title",
                                           modes=('view',),
                                           i18n_domain="rhaptos"),
                ),
    VersionField('version',
                required=1,
                searchable=0,
                vocabulary='moduleVersions',
                widget=VersionWidget(modes=('edit',),
                                     i18n_domain="rhaptos"),
                #validators=('isModuleVersionNumber',),
                ),

     ))

class PublishedContentPointer(BaseContentPointer):
    """A sort of symbolic link to an external resource
    (specifically a published module.)
    """
    archetype_name = 'Published Module Reference'

    schema = schema

    aliases = {
        '(Default)'  : 'collection_composer',
        'edit'       : '',
        'gethtml'    : '',
        'index.html' : '',
        'properties' : '',
        'sharing'    : '',
        'view'       : 'collection_composer',
        }

    def getCatalogs(self):
        """ prevent adding this content to catalog """
        return []

    def isModule(self):
        return 1 # our contract for "modules"

    def computedTitle(self):
        try:
            orig_title = self.content.getRhaptosObject(self.getModuleId(), self.getVersion()).title
            return self.getOptionalTitle() or orig_title or "#untitled#"
        except (KeyError, AttributeError):
            return '#invalid module: "%s"#' % self.getModuleId()
        return self.getOptionalTitle() or "#untitled#"

    def setModuleId(self, value, **kw):
        """Change the value of the moduleId field, by delegating to the AT field mutator.
        Customized to update the catalog field Title.
        """
        retval = self.getField('moduleId').set(self, value, **kw)
        self.reindexObject(['Title', 'sortable_title', 'SearchableText'])
        return retval

    def moduleLocation(self):
        "return the URL for the pointed to module"
        return "%s/%s/%s/" % (self.content.absolute_url(),self.getModuleId(),self.getVersion())

    def moduleVersions(self):
        """A DisplayList of module versions"""
        retval = []
        try:
            retval = [(elt.version,elt.version) for elt in self.content.getHistory(self.getModuleId())]
        except:
            pass
        return DisplayList(retval)

    def getContent(self):
        """Return the actual object at which this object "points"."""
        try:
            return self.content.getRhaptosObject(self.getModuleId(), self.getVersion())
        except KeyError:
            pass
        return None

#    def post_validate(self, REQUEST, errors):
#    	moduleid = REQUEST['moduleId']
#        version = REQUEST['version']
#    	zLOG.LOG("PublishedContentPointer", zLOG.INFO, "module: %s v %s" % (moduleid, version))

registerType(PublishedContentPointer)
