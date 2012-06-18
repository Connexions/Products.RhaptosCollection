## Script (Python) "addModulesToCourse"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=ids=[],redirect=True
##title= Add pointers to published modules to a course

request = container.REQUEST

if context.portal_membership.isAnonymousUser():
  return

target = context
failed = []
collection = context.nearestCourse()

allIDs = collection.containedModuleIds()

collection.setMassUpdate(1)  # this will stop logAction on PCP creation
for m in ids:
  if m in allIDs:
    failed.append(m)
    continue
  target.invokeFactory(id=m, type_name="PublishedContentPointer")
  module = target[m]
  module.setModuleId(m)
  #module.setVersion('latest')
  # Copy links
  pub = module.getContent()
  for l in pub.getLinks():
    module.addLink(l.target, l.title, l.category, l.strength)
collection.setMassUpdate(0)
collection.logAction('save')

if not redirect:
    return

if failed:
  psm = context.translate("message_two_modules_in_one_course", domain="rhaptos", default="Modules cannot appear twice in a course.")
  request.RESPONSE.redirect('.?portal_status_message='+psm)
else:
  request.RESPONSE.redirect('.')
