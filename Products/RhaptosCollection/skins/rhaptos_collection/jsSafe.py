## Script (Python) "jsSafe"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=uid
##title= Make a Zope id safe for use as a javascript identifier
retval = "js"+uid
retval = retval.replace('_dot_','__dot__')
retval = retval.replace('.','_dot_')
retval = retval.replace('_dash_','__dash__')
retval = retval.replace('-','_dash_')
return retval