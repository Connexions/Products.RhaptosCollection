## Script (Python) "toc_structure"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=collection=None, collapse=True
##title=HTML render of Table of Contents
# calls hopefully-cached Python script htmlContents to do the actual work. this method
# is for providing explicit parameters for the cached method to vary on.
# see 'htmlContents' for param info.

request = context.REQUEST
cookie = request.get('table_of_contents', None)
collection = collection or context
if cookie is None:
    cookielist = None
else:
    cookielist = cookie.split('%2C')

salt = collection.isPublic() and 1 or random.random()  # don't cache on preview

#passthru collection param, or synthesize from last two url components
collection_param = request.get('collection') or collection.isPublic() and '/'.join(collection.url().rstrip('/').split('/')[-2:]) or  'preview'

return context.htmlContents(collection=collection, collectionId=collection.objectId, 
                            minorversion=collection.getMinorVersion(), 
                            collection_param=collection_param, collapse=collapse, 
                            nodes=cookielist, salt=salt)
