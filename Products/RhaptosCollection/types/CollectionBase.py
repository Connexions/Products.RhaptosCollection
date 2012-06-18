from Products.Archetypes.public import OrderedBaseFolder
from Products.Archetypes.interfaces.base import IBaseFolder
from Products.Archetypes.interfaces.orderedfolder import IOrderedFolder

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.CMFCorePermissions import AddPortalContent

from Acquisition import aq_parent, aq_inner, aq_base

from OFS.CopySupport import CopyError, eInvalid, eNoData, eNotFound, eNotSupported
from OFS.CopySupport import _cb_decode, sanity_check
from OFS.CopySupport import Moniker
from App.Dialogs import MessageDialog
import sys
from types import UnicodeType
from Products.PythonScripts.standard import html_quote

import zLOG
def log(msg, severity=zLOG.INFO):
    zLOG.LOG("RhaptosCollection: CollectionBase", severity, msg)
    #pass

_marker = []   # marker object for a recognizable default, where we want to use None as a reasonable value

class CollectionBase(OrderedBaseFolder):
    """Base for Collection types, like 'Collection' and 'SubCollection'"""

    __implements__ = OrderedBaseFolder.__implements__  # we don't want references or exensible metadata tabs

    use_folder_tabs = 0
    
    # fix permissions set by CopySupport.py just like in PloneFolder
    # and, no, I don't pretend to understand why this works (it should only be available to Managers!)
    __ac_permissions__=(
        ('Modify portal content',
         ('manage_cutObjects', 'manage_copyObjects', 'manage_pasteObjects',
          'manage_renameForm', 'manage_renameObject', 'manage_renameObjects',)),
        )
    def resourcename(self, fragmentary=0):
        if not fragmentary:
            return self.UID()
        else:
            return "#" + self.UID()

    def getContainedObject(self, id):
        """Return the contained content pointer corresponding to a particular ID (or None)"""
        for name, obj in self.objectItems():
            if name == id:
                return obj
            if hasattr(obj.aq_base, 'isGroup'):
                child = obj.getContainedObject(id)
                if child:
                    return child

    def containedModules(self):
        """Return a list of the published modules this course contains."""
        modules = []
        for id in self.objectIds(['Collection', 'SubCollection', 'ContentPointer', 'PublishedContentPointer']): #self.order:
            node = getattr(self, id)
            if hasattr(node.aq_base, 'isGroup'):
                modules.extend(node.containedModules())
            elif hasattr(node.aq_base, 'isModule'):
                modules.append(node)
        return modules

    def containedModuleIds(self):
        """Return a list of the published modules this course contains."""
        return [m.getModuleId() for m in self.containedModules()]

    def containedModuleAuthors(self):
        """Return a list of the authors of published modules this course contains."""
	authors=[]
	for m in self.containedModules():
	    authors.extend(m.authors)
        return dict(zip(authors,authors)).keys()

    def children(self):
        return self.contentValues()  # should be something like children = contentValues

    def children_resources(self):
        return [child.resourcename(fragmentary=1) for child in self.children()]

    def panel(self):
        #template = self.restrictedTraverse(path = 'collection_panel')
        #return template.macros[panel]
        return 'collection_panel'

    def get_size(self):
        """ Used for FTP and apparently the ZMI now too """
        return 0
    
    def contentsTree(self, level=0, node_chapter=None, cookielist=_marker, path=''):
        """Generate nested table of contents structure for this collection.
        
        Returns a list of dicts:
          {'container':boolean true for subcollections,
           'id': module id (module ref only),
           'path': path inside the collection to this object (suitable for restrictedTraverse),
           'UID': Plone uid (subcollection only),
           'title': title,
           'url': URL to module (module ref only),
           'level': level in tree, starting at 'level' param (subcollection only),
           'number': chapter number, only on qualifying collections to be appended to title,
           'shown': node is not collapsed, based on 'cookielist' (subcollection only),
           'children': list of these dicts (subcollection only)
           }
        Keys are only available if they have meaning in that context.
        
        Derived from previous htmlContentsTree.
        """
        result = []
        nodes = self.objectValues(['Collection', 'SubCollection', 'ContentPointer', 'PublishedContentPointer'])
        
        if level==0 and not nodes:
            return []
        
        # chapter calculation. only for first level on textbooks (and skip v. small collections)
        numbering = level==0 and len(nodes) > 0 and self.getCollectionType() == 'Textbook'
        chapter = None
        if numbering:
            types = set([x.portal_type for x in nodes])
            if 'SubCollection' not in types:  # collection consists of modules only
                chapter = 0
            elif types==set(['SubCollection']):  # ...subcollections only
                chapter = 0
        
        for node in nodes:
            title = node.Title()
            nodepath = "%s%s/" % (path, node.getId())
            
            if node.portal_type.find('ContentPointer') != -1:
                # Module ref
                if numbering and chapter != None:
                    # if chapter is an int, use it...
                    chapter += 1
                node = {'container':False,
                        'id':node.moduleId,
                        'version':node.getVersion(),
                        'url':node.moduleLocation(),
                        'number':chapter,
                        }
            elif node.portal_type == 'SubCollection':
                # SubCollection
                if numbering and chapter==None:
                    # ...if chapter is None, wait until we get a PCP, then become int.
                    chapter = 0
                if numbering and chapter != None:
                    chapter +=1
                uid = node.UID()
                shown = not cookielist or "js%s" % uid in cookielist and True or False
                node = {'container':True,
                        'UID': uid,
                        'level':level,
                        'number':node_chapter,
                        'shown': shown,
                        'children':node.contentsTree(level+1, chapter, cookielist, nodepath)
                        }
            else:
                raise Exception("Unknown collection contents: %s" % self)
            node['title'] = title
            node['path'] = nodepath
            result.append(node)
        
        return result
        
    #### FIXME we really shouldn't be building HTML this deep in the code - 
    #### this also could use some sort of cache, w/ invalidation on contained content publish 
    def htmlContentsTree(self, level=0, node_chapter=None, cookielist=_marker, collection=None):
        """Generate HTML tree of content titles and urls. Done only as an optimization--all this recursion is
        absurdly slow in template, and slower in restricted code in general.

        The headings go from h4 to h6, based on the level param that increments at each recursion (it starts at 
        three because we only really start rendering contents one level in.)
        
        'cookielist' is list of UIDs of elements to expand; set to None to expand all.
           This really should be done in a template, but we don't have one yet.

        'collection' is the colID/version string to use for the URL collection parameter. 
           If None, will be colId/latest if published, or 'preview' if not.
        """
        result = u''
        nodes = self.objectValues(['Collection', 'SubCollection', 'ContentPointer', 'PublishedContentPointer'])
        if not(collection):
            collection = self.state == 'public' and ('%s/latest' % self.objectId ) or 'preview'

        if level==0 and not nodes:
            return "No contents."

        # chapter calculation. only for first level on textbooks (and skip v. small collections)
        numbering = level==0 and len(nodes) > 0 and self.getCollectionType() == 'Textbook'
        chapter = None
        if numbering:
            types = set([x.portal_type for x in nodes])
            if 'SubCollection' not in types:  # collection consists of modules only
                chapter = 0
            elif types==set(['SubCollection']):  # ...subcollections only
                chapter = 0

        for node in nodes:
            title = node.Title()
            if type(title) != UnicodeType:
                title = title.decode('utf-8')
            if node.portal_type.find('ContentPointer') != -1:
                if numbering and chapter != None:
                    # if chapter is an int, use it...
                    chapter += 1
                    title = "%s. %s" % (chapter, title)
                result += u'<li id="%s"><a href="%s?collection=%s">%s</a></li>\n' % (node.moduleId, 
                                                                       node.moduleLocation(),collection,
                                                                       html_quote(title))
            else:
                if numbering and chapter==None:
                    # ...if chapter is None, wait until we get a PCP, then become int.
                    chapter = 0
                if numbering and chapter != None:
                    chapter +=1
                result += node.htmlContentsTree(level+1, chapter, cookielist, collection)

        if self.portal_type.find('SubCollection') != -1:
            title = self.Title()
            if type(title) != UnicodeType:
                title = title.decode('utf-8')
            if node_chapter != None:
                title = "%s. %s" % (node_chapter, title)
            header = level < 3 and level+3 or 6
            uid = self.UID()
            display = not cookielist or "js%s" % uid in cookielist and 'block' or 'none'
            result = u"""
            <li class="cnx_null_li">
             <h%s class="cnx_chapter_header"
                  onclick="org.archomai.transMenus.toc.ExpandMenuHeader(event);">%s</h%s>
             <ul id="js%s" class="collapsibleMenu" style="display: %s">%s</ul>
            </li>""" % (header, html_quote(title), header, uid, display, result)
        else:
            result = u'<ul id="collapsibleDemo">\n%s</ul>\n' % (result)  # top level

        return result
    #### REFERENCE PASTE SUPPORT ###

    def _transformableType(self, obj):
        # this is a brittle method. any additions to CC will require changes here
        excluded_types = ['ContentPointer','PublishedContentPointer', 'SubCollection']
        permitted_types = ['Module']
        obj_type = getattr(obj, 'portal_type', '')
        return not obj_type in excluded_types and hasattr(obj.aq_base, 'contentValues') or obj_type in permitted_types

    def _getTransformCopy(self, obj, op, id=None, container=None):
        """Returns tuple of transformed object and list of duplicates removed"""
        
        if not container: container = self
        if not id: id = self._get_id(obj.getId())
        otype = getattr(obj, 'portal_type', '')
        retval = None
        dupes = []

        #log("Transform copy of '%s'" % id)

        # Recurse containers
        if otype == 'Module':
            if self._duplicateCheck(obj, op):
                dupes.append(obj.getId())
            else:
                # FIXME: Do this when we re-enable ContentPointers (WMRs)
                #container.invokeFactory('ContentPointer', id)
                container.invokeFactory('PublishedContentPointer', id)
                retval = getattr(container, id)
                #retval.setModule(obj.UID())
                retval.setModuleId(obj.getId())

        elif hasattr(obj.aq_base, 'contentValues') and otype not in ['ContentPointer','PublishedContentPointer']:
            container.invokeFactory('SubCollection', id)
            retval = getattr(container, id)
            retval.setTitle(obj.Title())
            for elt in obj.contentValues():
                r, d = container._getTransformCopy(elt, op, container=retval)
                dupes.extend(d)

        else:
            container._verifyObjectPaste(obj)
            
            if self._duplicateCheck(obj, op):
                dupes.append(obj.getId())
            else:
                obj=obj._getCopy(container)
                obj._setId(id)
                container._setObject(id, obj)
                obj = container._getOb(id)
                retval = obj

        return retval, dupes

    def manage_pasteObjects(self, cb_copy_data=None, REQUEST=None):
        """Paste previously copied objects into the current object,
           making folders into chapters and RhaptosModuleEditors into
           ContentPointers (and not destroying their originals).
           Other objects will be as usual.
           Largely copied from OFS.CopySupport.
           If calling manage_pasteObjects from python code, pass
           the result of a previous call to manage_cutObjects or
           manage_copyObjects as the first argument."""
        cp=None
        if cb_copy_data is not None:
            cp=cb_copy_data
        else:
            if REQUEST and REQUEST.has_key('__cp'):
                cp=REQUEST['__cp']
        if cp is None:
            raise CopyError, eNoData

        try:    cp=_cb_decode(cp)
        except: raise CopyError, eInvalid

        oblist=[]
        op=cp[0]
        app = self.getPhysicalRoot()
        result = []
        duplicates = []

        for mdata in cp[1]:
            m = Moniker.loadMoniker(mdata)
            try: ob = m.bind(app)
            except: raise CopyError, eNotFound
            oblist.append(ob)
            
        for ob in oblist:
            self._verifyObjectPaste(ob)

        if op==0:
            # Copy operation
            for ob in oblist:
                if not ob.cb_isCopyable():
                    raise CopyError, eNotSupported % ob.getId()
                try:    ob._notifyOfCopyTo(self, op=0)
                except: raise CopyError, MessageDialog(
                    title='Copy Error',
                    message=sys.exc_info()[1],
                    action ='manage_main')
                #ob=ob._getCopy(self)
                orig_id=ob.getId()
                id=self._get_id(ob.getId())
                ob, dupes = self._getTransformCopy(ob, op, id, self)  # NEW
                duplicates.extend(dupes)
                if ob:
                    result.append({'id':orig_id, 'new_id':id})
                    #ob._setId(id)
                    #self._setObject(id, ob)
                    #ob = self._getOb(id)
                    ob.manage_afterClone(ob)

            if REQUEST is not None:
                return self.manage_main(self, REQUEST, update_menu=1,
                                        cb_dataValid=1)

        if op==1:
            # Move operation
            for ob in oblist:
                id=ob.getId()
                if not ob.cb_isMoveable():
                    raise CopyError, eNotSupported % id
                try:    ob._notifyOfCopyTo(self, op=1)
                except: raise CopyError, MessageDialog(
                    title='Move Error',
                    message=sys.exc_info()[1],
                    action ='manage_main')
                if not sanity_check(self, ob):
                    raise CopyError, 'This object cannot be pasted into itself'

                ### NEW BELOW ###
                if self._transformableType(ob):
                    # do the "copy" procedure
                    orig_id=ob.getId()
                    id=self._get_id(ob.getId())
                    ob, dupes = self._getTransformCopy(ob, op, id)
                    duplicates.extend(dupes)
                    if ob:
                        result.append({'id':orig_id, 'new_id':id})
                        ob.manage_afterClone(ob)
                else:
                    ### NEW ABOVE (below is ++indented compared to original) ###
                    # try to make ownership explicit so that it gets carried
                    # along to the new location if needed.
                    old = ob
                    orig_id=ob.getId()
                    id=self._get_id(ob.getId())
                    ob, dupes = self._getTransformCopy(ob, op, id)
                    duplicates.extend(dupes)
                    if ob:
                        result.append({'id':orig_id, 'new_id':id})
                        ob.manage_afterClone(ob)

                    aq_parent(aq_inner(old))._delObject(id)

            if REQUEST is not None:
                REQUEST['RESPONSE'].setCookie('__cp', 'deleted',
                                    path='%s' % cookie_path(REQUEST),
                                    expires='Wed, 31-Dec-97 23:59:59 GMT')
                REQUEST['__cp'] = None
                return self.manage_main(self, REQUEST, update_menu=1,
                                        cb_dataValid=0)
            
        if duplicates:
            raise "DuplicateError", duplicates

        return result

    def _verifyObjectPaste(self, object, validate_src=1):
        # Verify whether the current user is allowed to paste the
        # passed object into self.
        if self._transformableType(object):
            return
        OrderedBaseFolder._verifyObjectPaste(self, object)
        if object.portal_type not in [elt.id for elt in self.allowedContentTypes()] and object.meta_type != 'Annotation Server':
            raise 'Unauthorized', "%s not allowed here." % getattr(object,'archetype_name', object.portal_type)

        # ...ain't it stupid that this isn't done by default?


    def _duplicateCheck(self, object, op):
        """Check course for duplicate modules"""

        #zLOG.LOG("CB", zLOG.INFO, "Checking for dupe of " + object.getId())
        m = self.nearestCourse().getContainedObject(object.getId())
        if ((op==0) and m) or ((op==1) and m and m != object):
            #raise "DuplicateError", "Modules cannot appear twice in a course."
            return 1

