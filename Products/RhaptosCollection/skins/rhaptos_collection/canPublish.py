## Script (Python) "canPublish"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title= Returns true if the current user has permission to publish this module
# FIXME: ModuleEditor uses publishBlocked now, which is more clever; use that or a similar facility here
from AccessControl import getSecurityManager

obj = context.getPublishedObject()
if obj:
    # Check maintainership of currently published object
    return context.portal_membership.checkPermission('Edit Rhaptos Object', obj)
else:
    # Only allow local maintainers or global maintainers to publish new object
    cur_user = getSecurityManager().getUser().getUserName()
    return cur_user in context.maintainers or context.portal_membership.checkPermission('Edit Rhaptos Object',context)
