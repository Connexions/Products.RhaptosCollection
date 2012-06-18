## Script (Python) "htmlContents"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=collection, collectionId, minorversion, collection_param, collapse=True, nodes=[], salt=None
##title= Return a nested tree HTML representation of the contents
# This method renders HTML structure for the table of contents of a collection. This is intended
# to be cached, so it should have all state information be context or a parameter.
# Params:
# 'collection' is the collection object to render the table of contents for.
# 'collapse' is whether or not to pre-collapse the tree based on Transmenus cookie value. Default True,
#    to avoid flicker and use render the table based on the cookie values. Set to False to keep
#    everything expanded, helpful for non-JS contexts.
# 'nodes' is a list of nodes by UID to expand. Extracted from the cookie, most likely. Use None if
#    no cookie detected, so all are expanded (no JS indicated); a list otherwise (empty list means
#    all collapsed.)
# 'salt' is a dummy parameter you can pass to the method to create caching uniqueness to a call

if not collapse:
    return collection.htmlContentsTree(cookielist=[], collection = collection_param)

return collection.htmlContentsTree(cookielist=nodes, collection = collection_param)
