## Script (Python) "updateParameters"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title= Set parameters from form data

formdata = context.REQUEST.form

# Handle to propertysheet
p = context.parameters

# Delete old parameters, except the collectionType
ids = p.propertyIds()
if 'collectionType' in ids:
    ids.remove('collectionType')
p.manage_delProperties(ids)

# No reason to include the submit button as a parameter
if formdata.has_key('submit'):
    del formdata['submit']

for key, value in formdata.items():
    # Skip blank parameters (defaults)
    if not value:
        continue

    t = same_type(value, 0) and 'int' or 'string' 
    p.manage_addProperty(key, value, t)

context.logAction('save')

psm=context.translate("message_collection_parameters_updated", domain="rhaptos", default="Parameters updated.")
context.REQUEST.RESPONSE.redirect('collection_parameters?portal_status_message='+psm)
