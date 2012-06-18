## Script (Python) "getContributors"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=salt=None
##title= Inner method for colContributors

# inner method; call colContributors instead, which automatically decides 'salt'
# 'salt' is a dummy parameter you can pass to the method to create caching uniqueness to a call

d = {}
all_modules = context.containedModules()
all_mids = [o.getId() for o in all_modules]
brains = context.content.catalog(objectId=all_mids)

# In python 2.2 we have nested scopes and can use a list comp. here
for brain in brains:
    for a in brain.authors or []:
        authors =  d.setdefault('authors',{})
        authors[a] = None
        d['authors'] = authors
    for r,persons in (brain.roles or {}).items():
        if r != 'editors':
            for p in persons:
                role = d.setdefault(r,{})
                role[p] = None
                d[r] = role

for role in d.keys():
    d[role] = d[role].keys()

return d
