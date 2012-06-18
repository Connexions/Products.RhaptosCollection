## Script (Python) "colContributors"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Return a list of userids of people who are authors on contained content

# calls hopefully-cached Python script getContributors to do the actual work.
# wraps that method to provide "salt" to make non-public calls have unique cache signatures


salt = context.isPublic() and 1 or random.random()  # don't cache on preview

return context.getContributors(salt=salt)
