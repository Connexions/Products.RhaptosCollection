## Script (Python) "redirectToCollectionPublisher"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Determine link to publisher and redirect user

parameters = context.getParameters()
url = ''
#specialBuy = context.buyLink or context.aq_parent.buyLink or ''
autoBuy = ''
specialBuy = ''
try:
    specialBuy = context.buyLink or context.aq_parent.buyLink
except AttributeError:
    pass

if specialBuy == '' and parameters.has_key('buyLink'):
    specialBuy = parameters['buyLink']

autoBuy = context.portal_properties.rhaptos_collection_print_config.buyBookURLformat or ''
printFile = context.getPrintedFile()
printable = printFile and printFile.get_size()
autoBuy = printable and autoBuy and autoBuy % context.objectId or None
url = specialBuy or autoBuy

context.REQUEST.RESPONSE.redirect(url)

