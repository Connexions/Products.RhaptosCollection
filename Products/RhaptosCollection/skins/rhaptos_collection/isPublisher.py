## Script (Python) "isPublisher"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title= Returns true if the current user has permission to publish this module
# FIXME: ModuleEditor uses publishBlocked now, which is more clever; use that or a similar facility here

return context.portal_membership.checkPermission('Publish Rhaptos Object', context)
