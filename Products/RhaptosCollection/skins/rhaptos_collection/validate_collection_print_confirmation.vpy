## Script (Python) "validate_collection_publish"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=agree=None
##title=Validate user has viewed PDF before ordering printed copy

if not agree:
  lerr = context.translate("message_confirm_viewing_to_proceed", domain="rhaptos", default="You must agree that you have viewed the book and want to purchase a copy to proceed.")
  errormsg = context.translate("message_check_box_to_agree", domain="rhaptos", default="Check this box if you have viewed the book and want to purchase a copy.")
  state.setError('agree', errormsg)
  
if state.getErrors():
    msg = context.translate("message_please_correct_errors", domain="rhaptos", default="Please correct the indicated errors.")
    return state.set(status='failure', portal_status_message=msg)
else:
    return state.set()