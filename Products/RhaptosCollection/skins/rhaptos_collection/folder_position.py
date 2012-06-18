## Python Script "folder_position"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=position, id
##title=Move objects in a ordered folder
##

## Rhaptos Note:
## Customized, mostly to get HTTP_REFERER in there
## FIXME: New Plone version is CPT, and we should probably remove this and
##  use FormController tool customization to change where it goes (Plone one
##  always goes to 'folder_contents'). See also cc_reorder.py

from Products.PythonScripts.standard import url_quote

if position.lower()=='up':
    context.moveObjectsUp(id)

if position.lower()=='down':
    context.moveObjectsDown(id)

if position.lower()=='top':
    context.moveObjectsToTop(id)

if position.lower()=='bottom':
    context.moveObjectsToBottom(id)

# order folder by field
# id in this case is the field
if position.lower()=='ordered':
    context.orderObjects(id)

context.plone_utils.reindexOnReorder(context)

msg=context.translate("message_item_position_changed", domain="rhaptos", default="Item's position has changed.")
request = context.REQUEST
response = request.RESPONSE
ref = getattr(request, 'HTTP_REFERER', None)
if ref:
    return response.redirect(ref)
return response.redirect('%s/%s?portal_status_message=%s' % (context.absolute_url(),
                                                             'folder_contents',
                                                             url_quote(msg)) )
