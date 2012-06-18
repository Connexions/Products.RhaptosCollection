## Script (Python) "addWorkspaceModulesToCourse"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=modules=[]
##title= Add pointers to modules to a course

## ABANDONED, along with unpublished content pointers!

request = container.REQUEST

if context.portal_membership.isAnonymousUser():
  return

if modules:
  target = context

  for m in modules:
    target.invokeFactory(id=m, type_name="ContentPointer")
    module = target[m]
    module.setModule(m)

request.RESPONSE.redirect('.')
