## Script (Python) "current_collection"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Get current collection context
##

# historical note: extracted from getCourseParameters

from urlparse import urlparse
request = context.REQUEST

from Products.CMFCore.utils import getToolByName
utool = getToolByName(context, 'portal_url')

collection = None
colpath = None
if request.has_key('collection') and request.collection != 'preview':
    # Parameter tells us the collection
    colpath = request.collection
    colsplit = colpath.split('/')
    if len(colsplit)==1:
        # no version ... no problem ... make it latest
        colsplit = colsplit + ['latest']

    colpath = "content/%s" % '/'.join(colsplit) # we have a structure like "col10000/1.1"
    # set cookie so we stay this way...
    portal = utool.getPortalObject()
    cookie_context = "/%s" % portal.content.virtual_url_path()
    request.RESPONSE.setCookie('courseURL', "/%s" % colpath, path = cookie_context)

elif request.has_key('courseURL'):
    # Cookie tells us the collection
    (scheme, netloc, path, params, query, fragment) = urlparse(request['courseURL'])
    colpath = path
    portal_name = utool.getPortalObject().virtual_url_path()
    if portal_name is not None and len(portal_name) > 0:
        # with    virtual host, colpath is '/content/...'
        # without virtual host, colpath is '/plone/content/...'
        # here we remove the portal name, so that colpath is the same, regardless of virtual host
        portalstart = '/' + portal_name
        i = path.find(portalstart)
        if i == 0:
            colpath = path[len(portalstart):]
    colpath = colpath[1:]


if colpath:
    try:
        # FIXME: restricted traverse will work for local collections.
        # We could expand this to handle remote repositories as well
        colpath = str(colpath) # in case it's a unicode string, which getRhaptosObject doesn't like
        collection = context.portal_url.getPortalObject().restrictedTraverse(colpath)
    except (KeyError, AttributeError):
        # No such collection, return None
        pass

return collection
