"""
Object for representing collections of Rhaptos content.

Author: J. Cameron Cooper (jccooper@rice.edu)
Copyright (C) 2006-8 Rice University. All rights reserved.

This software is subject to the provisions of the GNU Lesser General
Public License Version 2.1 (LGPL).  See LICENSE.txt for details.
"""

import httplib, urllib, socket
from httplib import InvalidURL

from webdav.Lockable import ResourceLockedError
from OFS.PropertySheets import PropertySheet
from Persistence import Persistent
from Globals import package_home
from Products.RhaptosCollection.config import LICENSES, LANGUAGES, LANGS_NOSUB, LANGS_COMBINED
from Products.RhaptosCollection.config import WORKSPACE_TYPES, COLLECTION_EDITING_TYPES, COLLECTION_DISPLAY_NAMES
from Products.RhaptosCollection.config import PROCESS_MODES
from Products.RhaptosCollection.config import GLOBALS
from Products.RhaptosCollection.config import PROJECTNAME
from Products.RhaptosCollection.Field import SortedLinesField
from Products.RhaptosCollection.Widget import CompactStringWidget, URLWidget, SubjectWidget, LanguageWidget
from Products.RhaptosCollection.Widget import CompactSelectionWidget, CompactDateTimeWidget, CollectionTypeWidget
from Products.RhaptosCollection.Widget import CNXMLWidget

from Products.MasterSelectWidget.MasterSelectWidget import MasterSelectWidget

from CollectionBase import CollectionBase
#import SubCollection, BaseContentPointer
from Products.RhaptosCollection.interfaces import ICollection
from Products.CNXMLDocument.newinterfaces import IMDML

from Products.Archetypes.public import BaseSchema, Schema
from Products.Archetypes.public import StringField, TextField, ComputedField, DateTimeField
from Products.Archetypes.public import LinesField, FileField, BooleanField, IntegerField
from Products.Archetypes.public import SelectionWidget, TextAreaWidget, ComputedWidget
from Products.Archetypes.public import LinesWidget, StringWidget, FileWidget, BooleanWidget
from Products.Archetypes.public import CalendarWidget, RichWidget, MultiSelectionWidget, IntegerWidget
from Products.Archetypes.public import OrderedBaseFolder, registerType
from Products.Archetypes.public import DisplayList
from Products.Archetypes.interfaces.base import IBaseFolder
from Products.Archetypes.interfaces.orderedfolder import IOrderedFolder

from Products.CMFCore.utils import _getViewFor, _getAuthenticatedUser
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.Expression import Expression
from Products.CMFCore import permissions as CMFCorePermissions
from Products.CMFCore.CMFCorePermissions import View, ModifyPortalContent

from ComputedAttribute import ComputedAttribute
from DateTime import DateTime
from AccessControl import ClassSecurityInfo
from zope.interface import implements

from Products.PloneLanguageTool import availablelanguages

from Products.RhaptosCollaborationTool.CollaborationManager import CollaborationManager

from cStringIO import StringIO
from zipfile import ZipFile, ZIP_DEFLATED

PrintPermission = "Print Collection"
CMFCorePermissions.setDefaultRoles(PrintPermission, ('Manager',)) # + Member, see Install

import re
rxcountpages = re.compile(r"$\s*/Type\s*/Page[/\s]", re.MULTILINE|re.DOTALL)

import os
import mimetypes
from Products.MimetypesRegistry.MimeTypeItem import ICONS_DIR

from Products.validation.config import validation
from Products.validation.validators.ExpressionValidator import ExpressionValidator

# these should really go somewhere else...
def getLanguageWithSubtypes(self,lang,*args,**kwargs):
    """get language codes w/ subtypes"""
    c = availablelanguages.countries
    locales = [(l[0],c[l[0][3:].upper()]) for l in availablelanguages.combined.items() if l[0].startswith(lang)]
    locales.sort(lambda x, y: cmp(x[1], y[1]))

    if len(locales):
        locales.insert(0,(lang,'None'))
    else:
        locales = [(lang,'(none available)')]
    return DisplayList(locales)

def getLanguagesWithoutSubtypes(self):
    """get language codes that have no subtypes"""
    sl={}.fromkeys([l[:2] for l in availablelanguages.combined.keys()]).keys()
    langs = [l for l in availablelanguages.languages.keys() if l not in sl]
    langs.sort()
    return langs

import zLOG
def log(msg, severity=zLOG.INFO):
    zLOG.LOG("RhaptosCollection: Collection", severity, msg)

schema = BaseSchema.copy()
schema.delField('language')
schema = schema +  Schema((
    StringField('license',
                #required=1,
                searchable=0,
                vocabulary=LICENSES,
                enforceVocabulary=1,
                widget=CompactSelectionWidget(modes=('view',),
                                              i18n_domain="rhaptos"),
                ),
    StringField('title',
                searchable=1,
                required=1,
                widget=CompactStringWidget(description='Enter a descriptive title for the collection, leaving out course codes or institution names.',
                                           i18n_domain="rhaptos"),
                ),
    StringField('master_language',
               searchable=1,
               required=1,
               vocabulary = LANGUAGES,
               widget=LanguageWidget(slave_fields=({'name': 'language',
                                                    'action': 'vocabulary',
                                                    'vocab_method': 'getLanguageWithSubtypes',
                                                    'control_param': 'lang'},
                                                    {'name': 'language',
                                                    'action': 'disable',
                                                    'hide_values': LANGS_NOSUB
                                                    },),
               label = 'Language',
               helper_css=('language_locale.css',),
               description='Select the primary language for this collection.',
               i18n_domain="rhaptos",)
               ),
    StringField('language',
               searchable=1,
               vocabulary = LANGS_COMBINED,
               widget=CompactSelectionWidget(label='Regional Variant (optional)',
               description='The language subtype for this content, if applicable.',
               helper_js=('language_locale.js',),
               i18n_domain="rhaptos",
               modes=('view',),              
               ),
               ),
    # These next few fields should probably be in a separate schemata since we want
    # them speparate fromm the others, but it simplifies the archetypes page templates
    # if we just use one for now.
    StringField('institution',
                searchable=1,
                #schemata='Special-Purpose Fields',
                widget=CompactStringWidget(i18n_domain="rhaptos",
                                           description='An institution or organization with which this collection is associated. Example: a university at which a course is being taught.',),
                ),
    StringField('code',
                searchable=1,
                #schemata='Special-Purpose Fields',
                widget=CompactStringWidget(description='A formal designation for the collection, if applicable. Course codes and report numbers will be common. Examples: ELEC 301; TR07-03',
                                           label='Code or Number',
                                           i18n_domain="rhaptos"),
                ),
    StringField('instructor',
                searchable=1,
                #schemata='Special-Purpose Fields',
                widget=CompactStringWidget(description='For the Course subtype only: the names of people who will be teaching the course, if different from the course author(s).',
                                           i18n_domain="rhaptos"),
                ),
    StringField('homepage',
                searchable=1,
                #schemata='Special-Purpose Fields',
                widget=URLWidget(description="A URL for a web page associated with the collection. For example, a link to a course's syllabus.",
                                 label='External Web Page',
                                 i18n_domain="rhaptos"),
                validators=('isURL',),
                ),
    StringField('version',
                default='**new**',
                searchable=0,
                widget=CompactStringWidget(modes=('view',)),
                ),
    IntegerField('minorVersion',
                default=0,
                searchable=0,
                widget=IntegerWidget(modes=('view',)),
                ),
    StringField('state',
                searchable=0,
                widget=CompactStringWidget(modes=('view',)),
                default='created',
                ),
    ComputedField('collectionType',
                  searchable=1,
                  vocabulary = COLLECTION_EDITING_TYPES,
                  mode='rw',
                  expression="context.getParameters().has_key('collectionType') and context.getParameters()['collectionType'] or ''",
                  mutator='setCollectionType',
                  accessor='getCollectionType',
                  widget=CollectionTypeWidget(label='Collection Subtype',
                                                description='Optional: Choose a subtype for this collection. <a href="/help/reference/collection-subtypes">(help)</a>',
                                                i18n_domain="rhaptos"),
                ),
    LinesField('subject',
               searchable=1,
               vocabulary = 'getAvailableSubjects',
               widget=SubjectWidget(label='Subject(s)',
                                           format='checkbox',
                                           description='Select the subject categories that apply to this collection. <a href="/help/reference/subjects">(help)</a>',
                                           i18n_domain="rhaptos"),
               default='',
               ),
    DateTimeField('created',
                #required=1,
                searchable=1,
                widget=CompactDateTimeWidget(modes=('view',)),
                ),
    DateTimeField('revised',
                #required=1,
                searchable=1,
                widget=CompactDateTimeWidget(modes=('view',)),
                ),
    LinesField('authors',
                #required=1,
                searchable=1,
                widget=LinesWidget(modes=('view',)),
                ),
    LinesField('maintainers',
                #required=1,
                searchable=1,
                widget=LinesWidget(modes=('view',)),
                ),
    LinesField('licensors',
                #required=1,
                searchable=1,
                widget=LinesWidget(modes=('view',)),
                ),
    LinesField('pub_authors',
                #required=1,
                searchable=0,
                widget=LinesWidget(modes=('view',)),
                ),
    LinesField('pub_maintainers',
                #required=1,
                searchable=0,
                widget=LinesWidget(modes=('view',)),
                ),
    LinesField('pub_licensors',
                #required=1,
                searchable=0,
                widget=LinesWidget(modes=('view',)),
                ),
    LinesField('collaborators',
                #required=1,
                searchable=0,
                widget=LinesWidget(modes=('view',)),
                ),
    LinesField('parentAuthors',
                searchable=0,
                widget=LinesWidget(modes=('view',)),
                ),
    SortedLinesField('keywords',
               searchable=1,
               widget=LinesWidget(description='Enter each keyword on its own line. Keywords are not displayed on the content, but are used behind the scenes to help people find it in searches.',
                                  label="Keywords (one per line)",
                                  i18n_domain="rhaptos"),
               # there is a KeywordWidget -  for controlled vocabs
               ),
    TextField('abstract',
              searchable=1,
              #required=1,
              allowable_content_types=(),
              widget=CNXMLWidget(description="Enter a summary of the collection and/or its objectives. May contain a limited set of CNXML. <a href='/help/authoring/authorguide#summary'>(help)</a>",
                                    label="Summary",
                                    i18n_domain="rhaptos"),
              ),
    DateTimeField('lastPrinted',
                searchable=0,
                widget=CompactDateTimeWidget(modes=()),
                ),
    IntegerField('printedFilePages',
                searchable=0,
                widget=StringWidget(modes=()),
                ),
    BooleanField('orderable',
                 default=1,
                 searchable=0,
                 write_permission=CMFCorePermissions.ManagePortal,  # expose to Managers only; maybe authors later
                 widget=BooleanWidget(label="Allow print-on-demand ordering?",
                                      description="If so, this collection will display the 'Order Printed Copy' button.",)
                 ),
    BooleanField('harvestable',
                 default=1,
                 searchable=0,
                 write_permission=CMFCorePermissions.ManagePortal,  # expose to Managers only; maybe authors later
                 widget=BooleanWidget(label="Allow automated metadata harvesting?",
                                      description="If so, this collection will be available via the OAI-PMH feed",)
                 ),
    StringField('GoogleAnalyticsTrackingCode',
                searchable=1,
                validators=(ExpressionValidator(expression="python:len(value.split('-')) == 3 and value.split('-')[0] == 'UA' and value.split('-')[1].isdigit() and value.split('-')[2].isdigit()",errormsg="Expecting a tracking code like 'UA-1234567-1'"),),
                widget=CompactStringWidget(label="Google Analytics Tracking Code",
                                           description='Enter the Google Analytics Tracking Code (e.g. UA-xxxxxxx-x) for this content to track usage.<br/><em>Note that this code will track only the collection home page, not the modules therein.</em> <a href="/help/reference/GoogleAnalyticsTrackingCode">(help)</a>' ,
                                           i18n_domain="rhaptos"),
                ),
    ))


class Collection(CollectionBase, CollaborationManager):
    """A collection is an ordered grouping of modules, for use as a book, course guide, report, etc.
    """
    implements(ICollection, IMDML)

    try:
        __implements__ = (CollectionBase.__implements__, CollaborationManager.__implements__)
    except:
        pass  # in case CollabMan grows an interface

    archetype_name = 'Collection'
    allowed_content_types = ['ContentPointer', 'PublishedContentPointer', 'SubCollection']

    schema = schema

    content_icon = 'repository_icon.gif'

    security  = ClassSecurityInfo()

    actions = (
               {'id': 'view',
                'title': 'Contents',
                'action': Expression('string:${object_url}/collection_composer'),
                'permissions': (CMFCorePermissions.View,)},
               {'id': 'edit',
                'title': 'Metadata',
                'action': Expression('string:${object_url}/collection_metadata'),
                'permissions': (CMFCorePermissions.ModifyPortalContent,)},
               {'id': 'roles',
                'title': 'Roles',
                'action': Expression('string:${object_url}/content_roles'),
                'permissions': (CMFCorePermissions.View,)},
               {'id': 'parameters',
                'title': 'Parameters',
                'action': Expression('string:${object_url}/collection_parameters'),
                'permissions': (CMFCorePermissions.View,)},
               {'id': 'preview',
                'title': 'Preview',
                'action': Expression('string:${object_url}/preview'),
                'permissions': (CMFCorePermissions.View,)},
               {'id': 'publish',
                'title': 'Publish',
                'action': Expression('string:${object_url}/collection_publish'),
                'permissions': (CMFCorePermissions.View,)},
              )

    aliases = {
        '(Default)'  : '(Default)',
        'edit'       : 'file_edit_form',
        'gethtml'    : '',
        'index.html' : '',
        'properties' : 'base_metadata',
        'sharing'    : 'folder_localrole_form',
        'view'       : '(Default)',
        }

    _properties=({'id':'title', 'type': 'string', 'mode': 'w'},
                 {'id':'authors','type':'lines', 'mode': 'w'},
                 {'id':'maintainers','type':'lines', 'mode': 'w'},
                 {'id':'licensors','type':'lines', 'mode': 'w'},
                 {'id':'pub_authors','type':'lines', 'mode': 'w'},
                 {'id':'pub_maintainers','type':'lines', 'mode': 'w'},
                 {'id':'pub_licensors','type':'lines', 'mode': 'w'},
                 {'id':'collaborators','type':'lines', 'mode': 'w'},
                 {'id':'parentAuthors','type':'lines', 'mode': 'w'},
                 {'id':'language','type':'string', 'mode': 'w'},
                 {'id':'collectionType','type':'string', 'mode': 'w'},
                 {'id':'subject','type':'lines', 'mode': 'w'},
                 )

    roles = ComputedAttribute(lambda self: self.getRolesDict(),1)

    optional_roles = {'Translator':'Translators'}

    # in modules, these are public (rather, unsecured) attributes, and the collaboration request system
    # uses that to display this info about content you don't have read access to (like content in someone
    # else's workspace); so, we make the AT attributes public so Collections work in role requests
    security.declarePublic('Title')
    security.declarePublic('title')
    security.declarePublic('state')
    security.declarePublic('license')

    def initializeArchetype(self, **kwargs):
        CollectionBase.initializeArchetype(self, **kwargs)
        user = _getAuthenticatedUser(self).getUserName()

        self.objectId = None

        langs = self.portal_languages.getLanguageBindings()

        # Setup dynamic default properties
        self._defaults = {'title' : '(Untitled)',
                          'created': DateTime(),
                          'revised': DateTime(),
                          'authors' : [user],
                          'maintainers' : [user],
                          'licensors' : [user],
                          'pub_authors' : [user],
                          'pub_maintainers' : [user],
                          'pub_licensors' : [user],
                          'collaborators' : [user],
                          'parentAuthors' : [],
                          'language': langs[0],
                          'collectionType': 'Course',
                          'subject':(),
                          'keywords':[],
                          'abstract':'',
                          'code':'',
                          'institution':'',
                          'coursecode':'',
                          'instructor':'',
                          'parameters':{},
                          }

        # Store object properties
        for key, value in self._defaults.items():
            setattr(self, key, value)

        self.logAction('create', 'Created Collection')

        # No initial parentage
        self._parent_id = None
        self._parent_version = None

        # Propertysheet to hold parameters
        self.parameters = PropertySheet('parameters')

        # New annotation folder
        self.manage_addProduct['ZAnnot'].manage_addZAnnot('annotations')


    def __setstate__(self, state):
        """Upgrade annotation instances"""
        Persistent.__setstate__(self, state)

        # Set objectId
        if not hasattr(self, 'objectId'):
            if self.state == 'created':
                setattr(self, 'objectId', None)
            elif self.state != 'public':
                setattr(self, 'objectId', self.id)
        if not hasattr(self,'collectionType'):
            self.collectionType = 'Course'
        

    def __call__(self):
        """Figure out what to display and do it"""
        #zLOG.LOG('Collection', zLOG.INFO, "In view: %s" % self.state)
        if self.isPublic():
            view = _getViewFor(self, 'preview')
        else:
            view = _getViewFor(self, 'contents')

        return view()

    def isPublic(self):
        """Boolean answer true iff collection is in versioned repository.
        Based currently on value of 'state' attribute.
        """
        return self.state == 'public'

    def setInstitution(self, value, **kwargs):
        """Intercept incoming values for institution to strip spaces (which makes for bad URLs
        etc.) Probably a good candidate for a custom string field some time in the future when
        we want more than one of these.
        """
        return self.getField("institution").set(self, value.strip(), **kwargs)

    def incrementMinorVersion(self):
        """Increment the minor version used to track contained module changes between collection
        versions. Returns the new value.
        """
        self.setMinorVersion(self.getMinorVersion()+1)

    def getCollectionType(self, display=None):
        """Return the collectionType.  If no display is specified, return the raw value.
        If a display is specified, return on of the display versions on the collectionType
        instead of the raw value.
        Possible values for display are: 'short', 'full', 'editing'
        """
        c_type = self.getParameters().has_key('collectionType') and self.getParameters()['collectionType'] or ''
        if display is not None and c_type:
            if display == 'full':
                return COLLECTION_DISPLAY_NAMES[c_type][0]
            elif display == 'editing':
                return COLLECTION_DISPLAY_NAMES[c_type][1]
            elif display == 'short':
                return COLLECTION_DISPLAY_NAMES[c_type][2]
            else:
                raise KeyError, "%s is not a valid display type.  Its must be one of: 'full','short', or 'editing'"%display
        else:
            return c_type

    def setCollectionType(self, value, **kwargs):
        """Store the collectionType as a parameter as well as the property"""
        p = getattr(self, 'parameters', None)  # p might be false on initialization
        if p is not None:
            if p.hasProperty('collectionType'):
                p.manage_changeProperties({'collectionType':value})
            else:
                t = type(value)
                p.manage_addProperty('collectionType', value, t)

    def _workspace(self):
        """Get the absolute path to and object for the nearest workspace.

        See util.WORKSPACE_TYPES for the types we consider a Workspace.

        Returns (obj, path)
        """
        retval = ""
        obj = self
        while not retval:
            obj = obj.getParentNode()
            obj_path = obj.getPhysicalPath()
            try:
                if obj.portal_type in WORKSPACE_TYPES:
                    retval = obj_path
            except AttributeError:
                pass
            if len(obj_path) == 1:
                retval = obj_path
        return obj, '/'.join(retval)

    def nearestWorkspace(self):
        """Get the object for the nearest workspace.

        See util.WORKSPACE_TYPES for the types we consider a Workspace.
        """
        return self._workspace()[0]

    def workspacePath(self):
        """Get the absolute path to and object for the nearest workspace.

        We count on all children inheriting this so that Field.WorkspaceReferenceField
        will work. See util.WORKSPACE_TYPES for the types we consider a Workspace.
        """
        return self._workspace()[1]

    def getParameters(self):
        """Return parameters as a mapping key -> value"""
        d = {}
        for param in self.parameters.propertyIds():
            d[param] = self.parameters.getProperty(param)
        return d


    def url(self):
        """Return a full url to this object; part of ad hoc content API. See also ModuleView."""
        return self.absolute_url()

    def annotations_url(self):
        return self.url() + "/annotations"

    def nearestCourse(self):
        return self

    def nearestRhaptosObject(self):
        return self

    def preview(self):
        """Preview the course"""
        
        utool = getToolByName(self, 'portal_url')
        portal = utool.getPortalObject()
        cookie_context = "/%s" % portal.content.virtual_url_path()
        #log("Setting courseURL cookie to\n\t%s\nwith context\n\ts%s" % (self.url(),cookie_context))
        self.REQUEST.RESPONSE.setCookie('courseURL', self.url(), path=cookie_context)

        # If they ask for it as RDF, give to them
        format = self.REQUEST.get('format', None)
        if format == 'rdf':
            self.REQUEST.RESPONSE.setHeader('Cache-Control', 'max-age=84600, s-maxage=31536000, public, must-revalidate')
            self.REQUEST.RESPONSE.setHeader('Content-Type', 'application/xml')
            return self.rdf()
        else:
            return self.collection_view()

    getLanguageWithSubtypes = getLanguageWithSubtypes

    getLanguagesWithoutSubtypes = getLanguagesWithoutSubtypes

    def getMaster_language(self):
        return self.language[:2]

    def setMaster_language(self, ll):
        pass

    def get_language_locale(self):
        return self.language

    def set_language_locale(self, ll):
        self.language_locale = ll
        self.language = ll

    def getAvailableSubjects(self):
        """The vocabulary for the subject field.  Queries the Database to find out the available subjects."""
        return [s.tag for s in self.portal_moduledb.sqlGetTags(scheme='ISKME subject')]

    def getRolesDict(self):
        """Return the optional roles for this object"""

        role_dict = {}
        opt_roles = getattr(self,'optional_roles',{})
        for role in opt_roles.keys():
            role_name = role.lower()+'s'
            users = list(getattr(self,role_name,[]))
            if users:
                role_dict[role_name] = list(getattr(self,role_name,[]))
        return role_dict

    def resetOptionalRoles(self):
        """Set all the optional roles on the object to empty"""
        opt_roles = getattr(self,'optional_roles',{})
        for role in opt_roles.keys():
            role_name = role.lower()+'s'
            setattr(self,role_name,[])
            setattr(self,'pub_'+role_name,[])

    # Arg.  Stupid CollaborationManager requires this
    def _writeMetadata(self):
        pass
    
    # Same problem as with _writeMetadata above :(
    def editMetadata(self):
        pass

    def getPublishedObject(self):
        """Return the currently published version of this object or
           None if it is newly created"""
        try:
            return self.content.aq_inner.getRhaptosObject(self.objectId)
        except KeyError:
            return None

    def getBaseObject(self):
        """Return the object this working copy is based on"""
        try:
            return self.content.getRhaptosObject(self.objectId, self.version)
        except KeyError:
            return None

    def setBaseObject(self, objectId):
        """Set reference to the object of which this is a version """
        self.objectId = objectId

    def setParent(self, parent):
        if parent:
            self._parent_id = parent.objectId
            self._parent_version = parent.version
        else:
            self._parent_id = self._parent_version = None

    def getParent(self):
        if self._parent_id:
            try:
                return self.content.getRhaptosObject(self._parent_id, self._parent_version)
            except KeyError:
                return None

    def getParentId(self):
        return self._parent_id    

    def wrapAbstract(self, terms, open_wrap_tag='<b>', close_wrap_tag='</b>'):
        """Wrap matches to list of terms with tags. Returns tuple of (excerpt,wrappedtext)"""
        q = '&'.join(terms)
        res = self.portal_moduledb.sqlWrapText(text=self.abstract, query=q,
                    open_wrap_tag='OPEN_CNX_WRAP_TAG',
                    close_wrap_tag='CLOSE_CNX_WRAP_TAG')
        headline,abstract =res.tuples()[0]
        cutoff = 20

        headline_start = abstract.find(headline)

        if headline_start != -1:
            headline_end = headline_start + len(headline)
            head = abstract[:headline_start]
            tail = abstract[headline_end:]

            if len(' '.join(head.split()[2:])) > cutoff:
                headline = ' '.join(head.split()[:2])+" ... "+headline
            else:
                headline = head+headline

            if len(' '.join(tail.split()[:-2])) > cutoff:
                headline = headline+" ... "+' '.join(tail.split()[-2:])
            else:
                headline = headline + tail

        return (headline.replace('OPEN_CNX_WRAP_TAG',open_wrap_tag).replace('CLOSE_CNX_WRAP_TAG',close_wrap_tag),
                abstract.replace('OPEN_CNX_WRAP_TAG',open_wrap_tag).replace('CLOSE_CNX_WRAP_TAG',close_wrap_tag))

    def wrapBodyText(self, terms, open_wrap_tag='<b>', close_wrap_tag='</b>'):
        pass

    def sortTitle(self):
        """title stripped of initial articles, for sorting"""

        t=self.Title()
        ARTICLES = ['the', 'a', 'an']
        for a in ARTICLES:
            compare = a + ' '
            if t.lower().startswith(compare) and t[len(compare):]:
                return t[len(compare):]
        else:
            return t


    def updateMetadata(self):
        # Copy metadata from published object
        item = self.getPublishedObject().latest

        def_roles = [r.lower()+'s' for r in self.default_roles]
        opt_roles = [r.lower()+'s' for r in getattr(self,'optional_roles', {}).keys()]
        collab = []
        roles={}

        # Default ordering for roles: Authors before Maintainers before Licensors... optional roles last
        for role in def_roles:
            for u in list(getattr(item,role)):
                if u not in collab:
                    collab.append(u)
        for role in opt_roles:
            users = list(item.roles.get(role,()))
            if users:
                for u in users:
                    if u not in collab:
                        collab.append(u)

        # Ordering role lists to maintain consistency with the collaborators field
        for role in def_roles:
            role_list = list(roles.setdefault(role,[]))
            for c in collab:
                if c in getattr(item,role):
                    role_list.append(c)
                    roles[role]=role_list

        for role in opt_roles:
            role_list = list(roles.setdefault(role,[]))
            for c in collab:
                users = list(item.roles.get(role,()))
                if users:
                    if c in users:
                        role_list.append(c)
                        roles[role]=role_list

        self.setTitle(item.Title())
        self.setCreated(item.getCreated())
        self.setRevised(item.getRevised())
        self.setAuthors(roles['authors'])
        self.setMaintainers(roles['maintainers'])
        self.setLicensors(roles['licensors'])
        self.setPub_authors(roles['authors'])
        self.setPub_maintainers(roles['maintainers'])
        self.setPub_licensors(roles['licensors'])
        self.setCollaborators(collab)
        self.setVersion(item.getVersion())
        # !! Use of getAbstract accessor v. important--item.abstract is BaseUnit (File-ish),
        # item.getRawAbstract() is a string, and we want to pass string to mutator, not BaseUnit,
        # because if we pass BaseUnit, both Collections end up pointing at the same object
        # item.getAbstract() strips tags, so we can't use them now that we accept CNXML
        self.setAbstract(item.getRawAbstract())
        self.setKeywords(item.getKeywords())
        self.setLicense(item.getLicense())
        self.setInstitution(item.getInstitution())
        self.setInstructor(item.getInstructor())
        self.setCode(item.getCode())
        self.setHomepage(item.getHomepage())
        self.setParentAuthors(item.getParentAuthors())
        self.setSubject(item.getSubject())
        self.setLanguage(item.getLanguage())

        self.setOrderable(item.getOrderable())

        for role in opt_roles:
            setattr(self,role,list(roles[role]))
            setattr(self,'pub_'+role,list(roles[role]))

        # Cancel any pending collaboration requests
        self.deleteCollaborationRequests()

        # Copy parameters
        self.parameters.manage_delProperties(self.parameters.propertyIds())
        for prop in item.parameters.propertyIds():
            value = item.parameters.getProperty(prop)
            t = item.parameters.getPropertyType(prop)
            self.parameters._setProperty(prop, value, t)

        # Set the correct parent module
        self.setParent(item.getParent())

        self.objectId = item.objectId
        
    def getMetadata(self):
        """Return the metdata for this collection as a dictionary.
        See also this method in RhaptosModuleEditor.ModuleEditor
        """
        repos = getToolByName(self, 'content')
        
        metadata = {}
        metadata['repository'] = repos.absolute_url()
        metadata['objectId'] = self.objectId
        metadata['version'] = self.getVersion()
        metadata['url'] = self.absolute_url()
        metadata['title'] = self.Title()
        metadata['abstract'] = self.getAbstract()
        metadata['created'] = self.getCreated()
        metadata['revised'] = self.getRevised()
        metadata['roles'] = self.roles
        metadata['keywords'] = self.getKeywords()
        metadata['subject'] = self.getSubject()
        metadata['license'] = self.getLicense()
        metadata['language'] = self.getLanguage()
        metadata['homepage'] = self.getHomepage()
        metadata['institution'] = self.getInstitution()
        metadata['coursecode'] = self.getCode()
        metadata['instructor'] = self.getInstructor()
        
        metadata['authors'] = self.getAuthors()
        metadata['maintainers'] = self.getMaintainers()
        metadata['licensors'] = self.getLicensors()
        #metadata['collaborators'] = self.getCollaborators()  # not used in MDML?
        
        # translators, editors typically
        for role, members in self.roles.items():
            metadata[role] = members
        
        metadata['pub_authors'] = self.getPub_authors()
        metadata['pub_maintainers'] = self.getPub_maintainers()
        metadata['pub_licensors'] = self.getPub_licensors()
        pobj = self.getParent()
        if pobj:
            metadata['parent'] = pobj.getMetadata()
        else:
            metadata['parent'] = pobj
        metadata['parentAuthors'] = self.getParentAuthors()
        return metadata

    def checkout(self, objectId=None):
        """Checkout a copy from the repository"""

        # If an objectId was specified, use it. otherwise use what
        # we've already got
        if objectId:
            self.objectId = objectId

        # FIXME: we should check that the current objectId is valid
        item = self.getPublishedObject().latest

        self.updateMetadata()
        self.manage_delObjects(self.objectIds())
        self.manage_checkoutPaste(item.manage_copyObjects(item.objectIds()))

        # reset print file and associated info, since we have changed
        # (also called on new checkout, though that should be blank start)
        self.setPrintedFile(None)

        # make available the GoogleAnalyticsTrackingCode of the parent
        versionFolder = item.aq_parent
        self.setGoogleAnalyticsTrackingCode(versionFolder.getGoogleAnalyticsTrackingCode())

        # Note the checkout in the properties
        self.logAction('checkout')

    def manage_checkoutPaste(self, cb_copy_data=None, REQUEST=None):
        """Do an 'unsafe' paste suring a chackout"""
        return OrderedBaseFolder.manage_pasteObjects(self, cb_copy_data, REQUEST)

    def setMassUpdate(self, bool):
        """Set whether we're doing a lot of updates.
        Used by addModulesToCourse to silence logAction calls.
        """
        self._massUpdate = bool

    def doingMassUpdate(self):
        """True iff we're in mass update mode; see 'setMassUpdate'.
        Has no direct effect on logAction, just allows other processes to know this state.
        """
        return getattr(self, '_massUpdate', None)

    # FIXME: Use portal_workflow instead of this
    def logAction(self, action, message=''):
        """Log last user action."""
        user = getToolByName(self, 'portal_membership').getAuthenticatedMember()

        # State transition table
        nextState = {'create':'created',
                     'add':'published',
                     'save':'modified',
                     'checkout':'checkedout',
                     'submit':'pending',
                     'publish':'published',
                     'withdraw':'created',
                     'discard':'published'}

        # Do state changes unless the current state is 'created'
        if self.state == 'created' and action not in ['submit','publish']:
            state = self.state
        else:
            state = nextState[action]

        prev_state = self.state
        self.state = state
        self.timestamp = DateTime()
        self.action = action
        self.actor = user.getUserName()
        self.message = message

        self.reindexObject()

        # Deal with the pending catalog for new authors
        if action  == 'submit':
            pending = getToolByName(self,'pending_catalog')
            pending.catalog_object(self)

        if prev_state == 'pending' and action in ['withdraw','publish']:
            pending = getToolByName(self,'pending_catalog')
            pending.uncatalog_object('/'.join(self.getPhysicalPath()))

    def revert(self):
        """Revert to last-published version (or blank)"""

        # Blow away our contents,
        self.manage_delObjects(self.objectIds())

        if self.state == 'created':
            # If it's a new course, re-initialize with original properties
            self.manage_changeProperties(self._defaults)
        else:
            # Otherwise, restore metadata and content
            self.updateMetadata()
            #self.updateContent()

        # reset print file and associated info, since we have changed
        self.setPrintedFile(None)

        self.reindexObject()

    def pdf(self):
        """Download the PDF stored in the print tool.
        Ideally, this method would just be the accessor for that field, but this allows us more
        control over the response, like in setting the content-disposition name. If this could be
        specified in the AT schema, we could drop this method.
        """
        self.REQUEST.RESPONSE.setHeader('Content-Type', 'application/pdf')
        self.REQUEST.RESPONSE.setHeader('Content-Disposition', 'attachment; filename=%s.pdf' % self.objectId)
        self.REQUEST.RESPONSE.setHeader('Cache-Control', 'max-age=84600, s-maxage=31536000, public, must-revalidate')
        return self.getPrintedFile()

    def pdfview(self):
        """Return the PDF stored in the RhaptosPrint tool with no unusual content headers.
        See also 'pdf'.
        """
        self.REQUEST.RESPONSE.setHeader('Content-Type', 'application/pdf')
        self.REQUEST.RESPONSE.setHeader('Cache-Control', 'max-age=84600, s-maxage=31536000, public, must-revalidate')
        return self.getPrintedFile()

    def _pdfPages(self, data=None):
        """Return the number of pages in the PDF, in a simple sort of way.
        See: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/496837
        """
        if data is None: data = str(self.getPrintedFile())
        return len(rxcountpages.findall(data))

    def setPrintedFile(self, value, extension='pdf', **kwargs):
        """
        If file has a value, add new file to RhaptosPrint tool.
        """
        #if it is a new collection (no object id), do nothing or setting in print tool will fail.
        oid = getattr(self, "objectId", None)
        if oid == None:
            return None
        if value is None and extension == 'pdf':
            self.setLastPrinted(None)
            self.setPrintedFilePages(0)
        else:
            if hasattr(value,'read'): #file like object - replace w/ bytes
                value = value.read()
            if extension == 'pdf':
                self.setLastPrinted(DateTime())
                self.setPrintedFilePages(self._pdfPages(str(value)))
            printTool = getToolByName(self,'rhaptos_print')
            printTool.setFile(self.objectId, self.getVersion(), extension, str(value))

        return None

    def getPrintedFile(self, extension='pdf'):
        """Checks the RhaptosPrint tool for status of PDF file.  If PDF generation status == failed,
        return None.  Otherwise, return stored PDF from RhaptosPrintTool.
        """
        objectId = self.objectId
        version = self.version

        #if it is a new collection (no object id), do nothing or setting in print tool will fail.
        if self.objectId == None:
            return None

        printTool = getToolByName(self,'rhaptos_print')
        if printTool.getStatus(objectId, version, extension) != 'failed':
            pdf = printTool.getFile(objectId, version, extension)
            if pdf != None:
                return pdf

        return None

    security.declareProtected(PrintPermission, 'triggerPrint')
    def triggerPrint(self, waitObj=None):
        """Cause the remote printing app to start work on the PDF, but come right back without waiting for it."""
        if self.getProcessStatus() == "locked":
            return "not printing; collection is locked"

        self.setProcessStatus('working')

        portal = self.portal_url.getPortalObject()
        printtool = getToolByName(portal,'rhaptos_print')

        # Check what print style we're set to, create a dependency if alternate
        # depends is a list of other depencies arising from other queue jobs
        # that must have completed and created some result.  Each dependency is
        # described by a tuple. The dependency tuple consists of the key of the
        # job we're dependent on, a type that is used for determining if the
        # dependency is fulfilled, a detail dictionary of any additional
        # information needed to so determine, and an action to perform if the
        # dependecy is not met. This may currently be one of 'fail',
        # 'reenqueue', (possible future: 'enqueuedep' or 'freeze' )
        # The deptype may be 'printtool' for other files stored via printtool,
        # or 'url' for a file available from a url, or 'file' for a directly
        # accessible file. in Either case, the depdetail provides the values
        # needed to determine if the dependecy exists, and is new enough for
        # the current job to use to build the pdf

        
        styles = printtool.getAlternateStyles()
        mystyle = self.getParameters().get('printstyle','')

        depends = []

        if mystyle:
            depkey = 'colcomplete_%s' % self.objectId
            deptype = 'printtool'
            depdetail = {'objectId':self.objectId, 'version':self.version, 'extension':'offline.zip', 'newer':DateTime()}
            depaction = 'reenqueue' 

            depends.append((depkey,deptype,depaction,depdetail))
        
        host = printtool.getHost()
        if host.startswith('http://'):
            host = host[7:]

        makefile = printtool.getMakefile()
        makefiledir = os.path.dirname(makefile)
        makefile = "%s/course_print.mak" % makefiledir

        project_name = portal.Title()
        project_short_name = project_name
        if project_name == 'Connexions':
              project_name = 'The Connexions Project'

        qtool = getToolByName(self, 'queue_tool')
        key = "colprint_%s" % self.objectId
        serverURL = self.REQUEST['SERVER_URL']
        dictRequest = { "id":self.objectId,
                        "version":self.version,
                        "makefile":makefile,
                        "host":host,
                        "serverURL":serverURL,
                        "project_name":project_name,
                        "project_short_name":project_short_name}

        if depends:
            dictRequest['depends'] = depends

        script_location = 'SCRIPTSDIR' in os.environ and os.environ['SCRIPTSDIR'] or '.'
        qtool.add(key, dictRequest, "%s/create_collection_pdf.zctl" % script_location)

        return "printing enqueued"

    def enqueue(self, **kw):
        """Call standard slate of event enquing as of publish."""
        # note ids are non-versioned, to avoid duplication on rapid publish
        # shouldn't this be a view?
        qtool = getToolByName(self, 'queue_tool')
        repos = getToolByName(self, 'content')
        oid = self.objectId
        ver = self.version
        repos = repos.absolute_url()
        status = self.getProcessStatus()

        kw = kw or hasattr(self,'REQUEST') and self.REQUEST.form or {}
        added = []

        rebuildCollectionXml = ( kw.get('collxml') is not None )
        rebuildCompleteZip   = ( kw.get('colcomplete') is not None )
        rebuildCollectionPDF = ( kw.get('colprint') is not None )
        if not rebuildCollectionXml and not rebuildCompleteZip and not rebuildCollectionPDF:
            rebuildCollectionXml = rebuildCompleteZip = rebuildCollectionPDF = True
        script_location = 'SCRIPTSDIR' in os.environ and os.environ['SCRIPTSDIR'] or '.'

        # ...collxml generation
        if rebuildCollectionXml:
            key = "collxml_%s" % self.objectId
            dictRequest = {'id':oid, 'version':ver, 'repository':repos, 'serverURL':self.REQUEST['SERVER_URL']}
            qtool.add(key, dictRequest, "%s/create_collection_xml.zctl" % script_location)
            added.append('collxml')

        # ...complete collxml package generation
        if rebuildCompleteZip:
            if status != 'locked':
                key = "colcomplete_%s" % self.objectId
                dictRequest = {'id':oid, 'version':ver, 'repository':repos, 'serverURL':self.REQUEST['SERVER_URL']}
                qtool.add(key, dictRequest, "%s/create_collection_complete_export_zip.zctl" % script_location)
                added.append('colcomplete')

        # ...pdf and latex generation
        if rebuildCollectionPDF:
            if status != 'locked':
                self.triggerPrint(waitObj=self)
                added.append('colprint')

        return "Enqueued: %s" % added or 'nothing'

    security.declarePrivate('_enqueueOnPublish')
    def _enqueueOnPublish(self):
        self.enqueue(collxml=1, colcomplete=1, colprint=1)

    security.declarePrivate('notifyObjectRevised')
    def notifyObjectRevised(self, origobj):
        """Called from repository when this object is published or republished.
        origobj is the previous revision, if available.
        """
        pubobj = self

        # clear count of between version module publishes
        self.setMinorVersion(0)

        # preserve locked status from previous version, if necessary; otherwise, reset status
        if origobj:
            status = origobj.getProcessStatus()
            if status == 'locked':
                pubobj.setPrintedFile(origobj.getPrintedFile())
                pubobj.setLastPrinted(origobj.getLastPrinted())  # order matters here, since 'setPrintedFile' does a 'setLastPrinted'
            else:
                status = 'blank'
            pubobj.setProcessStatus(status)

        # trigger async print of this collection
        status = pubobj.getProcessStatus()
        if status != 'locked':
            pubobj.setPrintedFile(None)      # don't keep any workspace printings

        # trigger async processing of other resources
        self._enqueueOnPublish()

    security.declarePrivate('notifyContentsRevised')
    def notifyContentsRevised(self, moded_in_publish=None):
        """Called from repository when modules in the object are republished.
        """
        self.incrementMinorVersion()
        # trigger async processing
        self._enqueueOnPublish()


    # FIXME: we should use actual actions for these but since some of
    # them are conditional, it's easier to do this way until we move
    # to CMF-1.4
    def getAboutActions(self):
        return [{'id':'collection_view', 'url':'collection_view', 'name':'View'},
                {'id':'about', 'url':'about', 'name':'About'},
                {'id':'history', 'url':'history', 'name':'History'},
                {'id':'collection_print', 'url':'collection_print', 'name':'Print'}]

    def getObjectActions(self):
        url = self.absolute_url()
        actions = []
        if self.state != 'published':
            actions.append({'id':'publish', 'url':url+'/collection_publish', 'name':'Publish'})

            if self.state != 'created':
                actions.append({'id':'fork', 'url':url+'/confirm_fork', 'name':'Derive Copy'})

            actions.append({'id':'discard', 'url':url+'/confirm_discard', 'name':'Discard'})
        return actions

    def getViewActions(self):
        if self.state != 'published':
            return [{'id':'view', 'url':self.absolute_url()+'/preview', 'name':'Online'},]
        else:
            return [{'id':'view', 'url':self.getPublishedObject().url(), 'name':'Online'},]

    def setProcessStatus(self, value):
        """
        add status to RhaptosPrintTool
        """
        id = getattr(self,"objectId", None)
        if id == None:
            return 

        printTool = getToolByName(self,'rhaptos_print')
        printTool.setStatus(self.objectId, self.getVersion(), 'pdf', value)

    def getProcessStatus(self):
        """
        If self.status has a value, call setProcessStatus() to move status to RhaptosPrintTool and clear self.status field.
        Get status from RhaptosPrintTool
        """
        #if it is a new collection (no object id), do nothing or setting in print tool will fail.      
        id = getattr(self,"objectId", None)
        if id == None:
            return ''

        printTool = getToolByName(self,'rhaptos_print')
        ptStatus = printTool.getStatus(self.objectId, self.version, 'pdf')
        return ptStatus or ''

    security.declarePrivate('addModuleFiles')
    def addModuleFiles(self, content, zipfile):
        """
        recursive call to add module files to the collection zip.
        content argument is either a Colelction or SubCollection.
        """
        collection = self
        collection_name = collection.getTitle()
        collection_id = collection.objectId
        collection_version = collection.id == 'latest' and collection.version or collection.id
        toplevelfolder = "%s_%s_complete" % (collection_id,collection_version)


        for obj in content.listFolderContents():
            if obj.portal_type == 'SubCollection':
                subcollection = obj
                self.addModuleFiles(subcollection, zipfile)

            elif hasattr(obj, 'isModule') and obj.isModule():
                module_ptr = obj
                module = module_ptr.getContent()
                module_id = module.objectId
                module_folder = "%s/%s" % (toplevelfolder,module_id)

                # Handle CNXML version upgrade/metadata extension
                cnxml = module.getDefaultFile()
                if not cnxml.upgrade():
                    cnxml.setMetadata()
                module_file_name = 'index_auto_generated.cnxml'
                file_location = "%s/%s" % (module_folder,module_file_name)
                if type(cnxml.data) == type(u''):
                    cdata = str(cnxml.data.encode('utf-8'))
                else:
                    cdata = str(cnxml.data)
                zipfile.writestr(file_location, cdata)


                    
                module_files = module.objectIds()
                for module_file in module_files:
                    # aping suppressHiddenFiles logic below
                    if module_file[:1] == '.':
                        continue
                    if module_file == 'CVS':
                        continue

                    module_file_name = module_file
                    bytes = str(module.getFile(module_file_name))
                    file_location = "%s/%s" % (module_folder,module_file_name)
                    zipfile.writestr(file_location, bytes)
                    #log("... for module %s in collection %s, writing file %s to zip at %s ..." % (module_id,collection_id,module_file_name,file_location))

    security.declarePublic('create_collxml')
    def create_collxml(self, REQUEST=None, collectionXml=None, versionHistoryXml=None, ancillaryXml=None):
        """
        returns a zipfile with just the collxml inside
        """
        collection = self
        collection_name = collection.getTitle()
        collection_id = collection.objectId
        collection_version = collection.id == 'latest' and collection.version or collection.id
        toplevelfolder = "%s_%s_complete" % (collection_id,collection_version)

        content = StringIO()
        zipfile = ZipFile(content, 'w', ZIP_DEFLATED)

        if REQUEST is not None:
            source_create = self.restrictedTraverse('source_create')
            collectionXml = source_create(self)

        if collectionXml is not None and len(collectionXml) > 0:
            zipfile.writestr(toplevelfolder + '/collection.xml', collectionXml)
        #zipfile.writestr(toplevelfolder + '/version-history.xml', "Hello World.")
        #zipfile.writestr(toplevelfolder + '/ancillary.xml', "Hello World.")

        zipfile.close()
        data = content.getvalue()
        return data

    security.declarePublic('create_complete')
    def create_complete(self, REQUEST=None, collectionXml=None, versionHistoryXml=None, ancillaryXml=None):
        """
        does the heavy lifting for building the collection zip.
        """
        collection = self
        collection_name = collection.getTitle()
        collection_id = collection.objectId
        collection_version = collection.id == 'latest' and collection.version or collection.id
        toplevelfolder = "%s_%s_complete" % (collection_id,collection_version)

        content = StringIO()
        zipfile = ZipFile(content, 'w', ZIP_DEFLATED)
        if REQUEST is not None:
            source_create = self.restrictedTraverse('source_create')
            collectionXml = source_create(self)

        if collectionXml is not None and len(collectionXml) > 0:
            zipfile.writestr(toplevelfolder + '/collection.xml', collectionXml)
        #zipfile.writestr(toplevelfolder + '/version-history.xml', "Hello World.")
        #zipfile.writestr(toplevelfolder + '/ancillary.xml', "Hello World.")

        self.addModuleFiles(collection, zipfile)
        zipfile.close()
        data = content.getvalue()
        return data

    def failIfLocked(self):
        """ This supports the SWORD API amongst other things.
            Check if isLocked via webDav
        """
        if self.wl_isLocked():
            raise ResourceLockedError('This resource is locked via webDAV.')
        return 0

registerType(Collection)
