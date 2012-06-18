## Script (Python) "authornames"
##title=Return a list of Author full names
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=

if hasattr(context, 'getAuthors'):
    authorlist = context.getAuthors()
else:
    authorlist = context.authors

return [getattr(context.desecured.getMemberById(author),'fullname') for author in authorlist] 
