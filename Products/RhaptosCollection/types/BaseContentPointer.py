from zope.interface import implements
from DateTime import DateTime
from Products.Archetypes.public import BaseSchema, Schema
from Products.Archetypes.public import BaseFolder
from Products.Archetypes.public import StringField, ComputedField
from Products.Archetypes.public import IdWidget, StringWidget, ComputedWidget
from Products.Archetypes.interfaces.base import IBaseFolder
from Products.LinkMapTool.LinkMapTool import ExtendedLink

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.PortalContent import PortalContent
from Products.CMFCore.Expression import Expression

from CollectionBase import CollectionBase
from Products.RhaptosCollection.interfaces import ICollectionContained

from Products.RhaptosCollection.Widget import CompactStringWidget

schema = BaseSchema + Schema((
        StringField('id',
                required=1,
                mode="rw",
                accessor="getId",
                mutator="setId",
                default=None,
                widget=CompactStringWidget(modes=(),
                                label_msgid="label_name",
                                description_msgid="help_name",
                                i18n_domain="plone",),
                ),
        ComputedField('title',
                accessor='Title',
                searchable=1,
                expression='context.computedTitle()',
                widget=CompactStringWidget(modes=()),
                ),
        StringField('optionalTitle',
                required=0,
                searchable=0,
                default='',
                widget=CompactStringWidget(label="Alternate Title",
                                           description='Enter an alternate name for this module, by which it will be displayed when viewed as part of your course.',
                                           modes=('edit',),
                                           i18n_domain="rhaptos"),
                ),
    ))

class BaseContentPointer(BaseFolder):
    """A sort of symbolic link to an external resource
    (specifically a RhaptosModuleEditor or published module.)
    """
    __implements__ = (IBaseFolder, PortalContent.__implements__)
    implements(ICollectionContained)

    schema = schema

    content_icon = 'module_icon_arrow.gif'

    no_rename = 1

    use_folder_tabs = 0
    
    actions = (
               {'id': 'view',
                'title': 'Edit',
                'action': Expression('string:${object_url}/collection_composer'),
                'permissions': (CMFCorePermissions.View,)},
               {'id': 'edit',
                'title': 'Edit',
                'action': Expression('string:${object_url}/collection_composer'),
                'visible': 0,
                'permissions': (CMFCorePermissions.ModifyPortalContent,)},
               {'id': 'links',
                'title': 'Links',
                'action': Expression('string:${object_url}/collection_composer?panel=collection_links'),
                'permissions': (CMFCorePermissions.ModifyPortalContent,)},
              )

    def Title(self):
        return self.schema['title'].get(self)

    def computedTitle(self):
    	return self.getOptionalTitle()

    def getContent(self):
        """Return the actual object at which this object "points"."""
        pass

    def resourcename(self, fragmentary=0):   # ignore fragmentary since modules aren't used like this
        return self.UID()

    def panel(self):
        return 'cp_edit'

    def getLinks(self, sequence=1):
        """Return list of links for a specific module"""
        links = self.objectValues('Extended Link')
        if sequence:
            sequence = self.nearestCourse().containedModules()
            index = sequence.index(self)
            # 'Previous' link
            if index > 0:
                prev = sequence[index - 1]
                link = ExtendedLink('previous', target=prev.moduleLocation(), title=prev.Title(),
                                    category='previous', strength=5)
                links.append(link)
            # 'Next' link
            if index < len(sequence) -1:
                next = sequence[index + 1]
                link = ExtendedLink('next', target=next.moduleLocation(), title=next.Title(),
                                    category='next', strength=5)
                links.append(link)

        return links

    def addLink(self, target, title, category, strength):
        """Add a link object"""
        now=DateTime()
        id = 'Link.'+now.strftime('%Y-%m-%d')+'.'+now.strftime('%M%S')
        count = 0
        while id in self.objectIds():
            id = 'Link.'+now.strftime('%Y-%m-%d')+'.'+now.strftime('%M%S')+'.'+str(count)
            count = count + 1

        self._setObject(id, ExtendedLink(id), suppress_events=True)
        l = getattr(self, id)
        l.edit(self.absolute_url(), target, title, category, strength)
        return l

    def _notifyOfCopyTo(self, container, op=0):
        """Let Zope know that we can't be pasted just anywhere"""

        if not isinstance(container, CollectionBase):
            raise "Bad Request", "Module references can only occur inside courses"
        
    def notifyWorkflowCreated(self, *args, **kw):
        """Do nothing since these don't participate in normal workflow"""
        pass
