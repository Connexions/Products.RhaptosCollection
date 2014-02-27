"""
Configuration of RhaptosCollection Product

Author: J. Cameron Cooper and Brent Hendricks
(C) 2005 Rice University

This software is subject to the provisions of the GNU Lesser General
Public License Version 2.1 (LGPL).  See LICENSE.txt for details.
"""

from Products.CMFCore.CMFCorePermissions import AddPortalContent
from Products.Archetypes.public import DisplayList
from Products.PloneLanguageTool import availablelanguages

ADD_CONTENT_PERMISSION = AddPortalContent
PROJECTNAME = "RhaptosCollection"
SKINS_DIR = 'skins'

GLOBALS = globals()

WORKSPACE_TYPES = ("Workgroup", "Workspace")

LICENSES = DisplayList((
    ('http://creativecommons.org/licenses/by/4.0/', 'Creative Commons Attribution 4.0'),
    ('http://creativecommons.org/licenses/by/3.0/', 'Creative Commons Attribution 3.0'),
    ('http://creativecommons.org/licenses/by/2.0/', 'Creative Commons Attribution 2.0'),
#    ('http://creativecommons.org/licenses/by/1.0', 'Creative Commons Attribution 1.0'),
#    ('http://creativecommons.org/licenses/by-sa/1.0/', 'Creative Commons Attribution-ShareAlike 1.0'),
    ))

PROCESS_MODES = ("blank", "working", "succeeded", "failed", "locked")

#FIXME this language list doesn't respect plone language settings!
langs = list(availablelanguages.getNativeLanguageNames().items())
langs.sort(lambda x, y: cmp(x[1], y[1]))

LANGUAGES = DisplayList(langs)
langs.extend(availablelanguages.getCombinedLanguageNames().items())
langs.sort(lambda x, y: cmp(x[1], y[1]))
LANGS_COMBINED = DisplayList(langs)


sl={}.fromkeys([l[0:2] for l in availablelanguages.combined.keys()]).keys()
langs = [l for l in availablelanguages.languages.keys() if l not in sl]
langs.sort()

LANGS_NOSUB = langs

COLLECTION_SUB_TYPES = ['Course','Manual','Proceedings','Techreport','Report','Textbook','Book','Mastersthesis','Phdthesis']
# This dictionary is keyed on the possible values of the collectionType field.
# The keys are (Full Name, Editing Name, Shortname)
COLLECTION_DISPLAY_NAMES = {
    'Course':('Course','Course','Course'),
    'Manual':('Manual','Manual','Manual'),
    'Proceedings':('Proceedings','Proceedings','Proceedings'),
    'Techreport':('Technical report','Technical report','Report'),
    'Report':('Report','Other report','Report'),
    'Textbook':('Textbook','Textbook','Textbook'),
    'Book':('Book','Other book','Book'),
    'Mastersthesis':("Master's thesis", "Thesis (Master's)", 'Thesis'),
    'Phdthesis':('Ph.D. thesis','Thesis (Ph.D.)','Thesis'),
    }

COLLECTION_EDITING_TYPES = [(c,COLLECTION_DISPLAY_NAMES[c][1]) for c in COLLECTION_SUB_TYPES]
COLLECTION_EDITING_TYPES.insert(0,('','(no subtype)'))

# collection parameters real name vs. exported name
# if not in this list, not exported
PARAMETERS_EXPORT = {
  'printfont':'print-font',
  'printstyle':'print-style',
  'fontsize':'print-font-size',
  'papersize':'print-paper-size',
  'paraspacing':'print-paragraph-spacing',

  'vectornotation':'vector-notation',
  'scalarproductnotation':'scalar-product-notation',
  'curlnotation':'curl-notation',
  'gradnotation':'gradient-notation',

  'andornotation':'and-or-notation',
  'realimaginarynotation':'real-imaginary-notation',
  'conjugatenotation':'conjugate-notation',
  'imaginaryi':'imaginary-i-notation',
  'forallequation':'for-all-equation-layout',
  'meannotation':'mean-notation',
  'remainder':'remainder-notation',
}

# mapping of values of collection parameter to a mapping of its values internal:external
# null values keyed to None; if not provided, use internal
PARAMETER_VALUE_EXPORT = {
  'printfont':{None:'computer-modern', 'times':'times', 'palatino':'palatino'},
'printstyle':{None:'', 'modern-textbook':'modern-textbook'},
  'fontsize':{None:'10pt', '12pt':'12pt'},
  'papersize':{None:'8.5x11', '6x9':'6x9'},
  'paraspacing':{None:'compact', 'loose':'loose'},

  'vectornotation':{None:'bold', 'overbar':'overbar', 'rightarrow':'right-arrow'},
  'scalarproductnotation':{None:'angle-bracket', 'dotnotation':'dot'},
  'curlnotation':{None:'text', 'symbolicnotation':'symbolic'},
  'gradnotation':{None:'text', 'symbolicnotation':'symbolic'},

  'andornotation':{None:'propositional-logic', 'text':'text',
                   'statlogicnotation':'statistics-logic', 'dsplogicnotation':'dsp-logic'},
  'realimaginarynotation':{None:'font', 'text':'text'},
  'conjugatenotation':{None:'bar', 'engineeringnotation':'star'},
  'imaginaryi':{None:'i', 'j':'j'},
  'forallequation':{None: 'symbolic', 0:'symbolic', 1:'text'},
  'meannotation':{None:'bar', 'anglebracket':'angle-bracket'},
  'remainder':{None:'text', 'remainder_anglebrackets':'angle-bracket'},
}
