## Python Script "cc_reorder"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=position, id
##title=Move objects in a ordered folder, for Collection Composer
##

# dispatch to folder_position, with update to collection parent

# assume we have col, since this should only be called by CC
col = context.nearestCourse()
col.logAction('save')

return context.folder_position(position, id)