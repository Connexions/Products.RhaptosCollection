"""
Initialize RhaptosCollection Product

Author: Brent Hendricks and J. Cameron Cooper
(C) 2005 Rice University

This software is subject to the provisions of the GNU Lesser General
Public License Version 2.1 (LGPL).  See LICENSE.txt for details.
"""

from Products.Archetypes.public import process_types, listTypes
from Products.CMFCore import utils
from Products.CMFCore.DirectoryView import registerDirectory
import os, os.path

from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot

from config import SKINS_DIR, GLOBALS, PROJECTNAME
from config import ADD_CONTENT_PERMISSION
import types

registerDirectory(SKINS_DIR, GLOBALS)

from AccessControl import allow_module, allow_class

# Allow access to urlparse for parsing courseURL cookies
import urlparse
allow_module('urlparse')

# Allow DisplayLists for subjectwidget
allow_module('Products.Archetypes.utils')

def initialize(context):
    ##Import Types here to register them
    import types.Collection
    import types.SubCollection
    import types.ContentPointer
    import types.PublishedContentPointer

    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)

    utils.ContentInit(
        PROJECTNAME + ' Content',
        content_types      = content_types,
        permission         = ADD_CONTENT_PERMISSION,
        extra_constructors = constructors,
        fti                = ftis,
        ).initialize(context)

import eventHandlers
del eventHandlers
