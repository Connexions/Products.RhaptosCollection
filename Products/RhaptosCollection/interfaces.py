"""
Zope 3 Component Architecture interface(s) for CollXML.

Author: J. Cameron Cooper (jccooper@rice.edu)
Copyright (C) 2009 Rice University. All rights reserved.

This software is subject to the provisions of the GNU Lesser General
Public License Version 2.1 (LGPL).  See LICENSE.txt for details.
"""

from zope.interface import Interface, Attribute

class ICollection(Interface):
    """Marker interface for objects that are Collections."""
    pass

class ICollectionContained(Interface):
    """Marker interface for objects that can be contained inside a Collection."""
    pass
