## Script (Python) "editCollectionLinks"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=links=[], delete=[]
##title= Edit module links

for l in links:
    context[l.id].edit(context.absolute_url(), l.target, l.title, l.category, l.strength)

if delete:
    context.manage_delObjects(delete)

psm = context.translate("message_links_updated", domain="rhaptos", default="Links updated.")
return state.set(portal_status_message=psm)    




