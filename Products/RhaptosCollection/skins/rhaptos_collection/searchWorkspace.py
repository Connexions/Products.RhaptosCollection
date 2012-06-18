## Script (Python) "searchWorkspace"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Search for modules in a workspace

from Products.CMFCore.utils import getToolByName

request = container.REQUEST
words = getattr(request, 'words', '').split()
results = []

try:
    ws_path = context.workspacePath()
except AttributeError:
    ws_path = context.absolute_url(1)

catalog = getToolByName(context, 'portal_catalog')
results = catalog(Type='Module',
                  path=ws_path,
                  SearchableText=words,
                  )

results = [r.getObject() for r in results]
return results