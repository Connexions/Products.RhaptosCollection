"""
Field for RhaptosCollection Product

Author: J. Cameron Cooper
(C) 2005 Rice University

This software is subject to the provisions of the GNU Lesser General
Public License Version 2.1 (LGPL).  See LICENSE.txt for details.
"""

from AccessControl import ClassSecurityInfo

from Products.Archetypes.public import ReferenceField, ObjectField, LinesField, Field
from Products.Archetypes.public import DisplayList

from Products.CMFCore.utils import getToolByName

import zLOG
def log(msg, severity=zLOG.INFO):
    zLOG.LOG("RhaptosCollection: Field", severity, msg)

class SortedLinesField(LinesField):
    """A field for containing a sorted set of unique lines"""

    security  = ClassSecurityInfo()
    
    security.declarePrivate('set')
    def set(self, instance, value, **kwargs):
        """
        If passed-in value is a string, split at line breaks and
        remove leading and trailing white space before storing in object
        with rest of properties.
        """
        __traceback_info__ = value, type(value)
        if type(value) == type(''):
            value =  value.split('\n')
        value = [v.strip() for v in value if v.strip()]
	#Uniquify and remove None from list
	value=filter(None,dict(map(None,value,[None])).keys())
	value.sort(lambda x,y: cmp(x.lower(),y.lower()))
        ObjectField.set(self, instance, value, **kwargs)

class VersionField(ObjectField):
    """A field for containing multiple fields."""
    _properties = Field._properties.copy()
    _properties.update({
        'type' : 'version',
        'default': 'latest',
        'searchable': 0,
        })

    security  = ClassSecurityInfo()
    
    security.declarePrivate('set')
    def set(self, instance, value, **kwargs):
        """ test"""
        #log("Set: value = %s, specific=%s" % (value, kwargs.get('specific','wer')))
        if value == 'specific':
            if kwargs.has_key('specific'):
                value = kwargs['specific']
            else:
                value = 'latest'
        ObjectField.set(self, instance, value, **kwargs)

class WorkspaceReferenceField(ReferenceField):
    """A field for containing a reference to a module in this workspace.

    If we're not in a workspace, no such limitation exists."""
    __implements__ = ReferenceField.__implements__

    def Vocabulary(self, content_instance=None):
        #If we have a method providing the list of types go with it,
        #it can always pull allowed_types if it needs to (not that we
        #pass the field name)
        value = ObjectField.Vocabulary(self, content_instance)
        if value:
            return value

        results = []
        catalog = getToolByName(content_instance, 'portal_catalog')
        try:
            ws_path = content_instance.workspacePath()
        except AttributeError:
            ws_path = "/"

        if self.allowed_types:  # we trust that all allowed_types are properly referencable and cataloged
            results = catalog(Type=self.allowed_types, path=ws_path)
        else:
            keys = catalog.uniqueValuesFor('UID')
            results = catalog(UID=keys, path=ws_path)  #... but this should never happen

        results = [(r, r.getObject()) for r in results]
        value = [(r.UID, obj and (str(obj.Title().strip()) or \
                                  str(obj.getId()).strip())  or \
                  log('Field %r: Object at %r could not be found' % \
                      (self.getName(), r.getURL())) or \
                  r.Title or r.UID) for r, obj in results]
        if not self.required:
            value.insert(0, ('', '<no reference>'))
        return DisplayList(value)

try:
    from Products.Archetypes.Registry import registerField

    registerField(SortedLinesField,
                  title='Sorted lines',
                  description=('Used for storing a set of lines in sorted order',))
    registerField(VersionField,
                  title='Rhaptos Module Version',
                  description=('Used for storing versions of modules.',))
    registerField(WorkspaceReferenceField,
                  title='Workspace Reference',
                  description=('Used for storing references to Referencable Objects within a workspace',))
except ImportError:
    pass   # we are probably in a < 1.2 version of Archetypes
