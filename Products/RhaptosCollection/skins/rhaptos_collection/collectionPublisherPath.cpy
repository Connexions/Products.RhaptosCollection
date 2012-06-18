## Script (Python) "collectionPublisherPath"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Determine if user needs to see collection print confirmation page or should go directly to QOOP
parameters = context.getParameters()
specialBuy = ''
#url = ''
try:
    specialBuy = context.buyLink or context.aq_parent.buyLink
except AttributeError:
    pass

#autoBuy = ''
if specialBuy == '' and parameters.has_key('buyLink'):
    specialBuy = parameters['buyLink']
#autoBuy = context.portal_properties.rhaptos_collection_print_config.buyBookURLformat or ''
#printFile = context.getPrintedFile()
#printable = printFile and printFile.get_size()
#autoBuy = printable and autoBuy and autoBuy % context.objectId or None
#zLOG.LOG("collectionPublisherPath", zLOG.INFO, "autoBuy: " + str(autoBuy))
#url = specialBuy or autoBuy
if specialBuy !=  None and len(specialBuy) != 0:
    context.REQUEST.RESPONSE.redirect(specialBuy)
else:
     context.REQUEST.RESPONSE.redirect(context.absolute_url() + "/collection_print_confirmation")
