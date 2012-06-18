## Script (Python) "addCollectionLink"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=newLink
##title= Display differences from the published module

# If they didn't specify a target URL, assemble it from the moduleid and version
if newLink.target:
    target = newLink.target
else:
    # If they didn't specify a URL, assemble it from the ID and version
    version = newLink.version or 'latest'
    try:
        target = context.content.getRhaptosObject(newLink.objectId, version).url()
    except KeyError:
        psm = context.translate("message_invalid_id_or_version", domain="rhaptos", default="Invalid ID or version")
        return state.set(status='failure', portal_status_message=psm)

context.addLink(target, newLink.title, newLink.category, newLink.strength)

psm = context.translate("message_link_added", domain="rhaptos", default="Link added.")
return state.set(portal_status_message=psm, newLink=None)

