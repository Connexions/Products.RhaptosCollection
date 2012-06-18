## Script (Python) "getCourseParameters"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

request = context.REQUEST

options = {}
course = None

if hasattr(context, 'getParameters'):
    # If the collection is the one we're looking at apply the options
    options.update(context.getParameters())
else:
    course = context.current_collection()

if course:
    options['course'] = course

    module = course.getContainedObject(context.objectId)
    if module:
        # notify favorites lens we read this module in context, if Lensmaker available
        getattr(context, 'favorites_notify_read', lambda *args: None)(course.objectId, context.objectId)

        options['module'] = module
        options.update(course.getParameters())
    
        # the following is made obsolete by pathBasedView...
        if hasattr(course, 'style'):
            options['style'] = course.style
        if hasattr(course, 'customHeader'):
            options['customHeader'] = course.customHeader

return options

