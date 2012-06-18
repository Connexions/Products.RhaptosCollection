"""
Widget for RhaptosCollection Product

Author: J. Cameron Cooper
(C) 2005 Rice University

This software is subject to the provisions of the GNU Lesser General
Public License Version 2.1 (LGPL).  See LICENSE.txt for details.
"""

from Products.Archetypes.public import StringWidget, SelectionWidget, CalendarWidget, MultiSelectionWidget
from Products.Archetypes.public import TextAreaWidget
from Products.Archetypes.Widget import TypesWidget
from Products.Archetypes.utils import capitalize
from Products.MasterSelectWidget.MasterSelectWidget import MasterSelectWidget

## CNX Note: version widget's process_form may need to be upgraded, but
##    I haven't bothered since we don't use it now

class CompactStringWidget(StringWidget):
    _properties = StringWidget._properties.copy()
    _properties.update({
        'macro' : "compactstring",
        })

class URLWidget(StringWidget):
    _properties = StringWidget._properties.copy()
    _properties.update({
        'macro' : "urlwidget",
        })

class CompactSelectionWidget(SelectionWidget):
    _properties = SelectionWidget._properties.copy()
    _properties.update({
        'macro' : "compactselection",
        })

class CompactDateTimeWidget(CalendarWidget):
    _properties = CalendarWidget._properties.copy()
    _properties.update({
        'macro' : "compactdatetime",
        })

class SubjectWidget(MultiSelectionWidget):
    _properties = MultiSelectionWidget._properties.copy()
    _properties.update({
        'macro' : "subjectwidget",
        })

class LanguageWidget(MasterSelectWidget):
    _properties = MasterSelectWidget._properties.copy()
    _properties.update({
        'macro' : "languageselection",
        })

class CollectionTypeWidget(CompactSelectionWidget):
    _properties = CompactSelectionWidget._properties.copy()
    _properties.update({
        'macro' : "coltypeselection",
        })

class VersionWidget(TypesWidget):
    _properties = TypesWidget._properties.copy()
    _properties.update({
        'macro' : "versionwidget",
        })

    def process_form(self, instance, field, form, empty_marker=None):
        fieldname = field.getName()
        val = form.get(fieldname, empty_marker)
        if val is empty_marker: return empty_marker

        kwargs = {}

        if form.has_key('specific'):
            kwargs['specific'] = form['specific']

        return val, kwargs

class CNXMLWidget(TextAreaWidget):
    _properties = TextAreaWidget._properties.copy()
    _properties.update({
        'macro' : "cnxmlwidget",
        })

try:
  from Products.Archetypes.Registry import registerWidget

  registerWidget(CompactStringWidget,
                 title='CompactString',
                 description='Like StringWidget, but the view widget is on a single line.',
                 used_for=('Products.Archetypes.Field.StringField',)
                 )

  registerWidget(URLWidget,
                 title='URL',
                 description='Like StringWidget, but the view widget is on a single line and is wrapped in a link.',
                 used_for=('Products.Archetypes.Field.StringField',)
                 )

  registerWidget(CompactSelectionWidget,
                 title='CompactSelection',
                 description='Like SelectionWidget, but the view is on a single line.',
                 used_for=('Products.Archetypes.Field.StringField',
                           'Products.Archetypes.Field.LinesField',)
                 )

  registerWidget(CompactDateTimeWidget,
                 title='CompactDateTime',
                 description='Like CalendarWidget, but the view is on a single line.',
                 used_for=('Products.Archetypes.Field.DateTimeField',)
                 )

  registerWidget(SubjectWidget,
                 title='Subject',
                 description='Like MultiSelectionWidget, but has a radio button for an empty selection. Currently specific to subjects.',
                 used_for=('Products.Archetypes.Field.LinesField',)
                 )

  registerWidget(LanguageWidget,
                 title='Language',
                 description='Like MasterSelectWidget, but has a couple tweaks specific to languages.',
                 used_for=('Products.Archetypes.Field.StringField',)
                 )

  registerWidget(CollectionTypeWidget,
                 title='CollectionType',
                 description='Like CompactSelectionWidget, but has a couple tweaks specific to CollectionType.',
                 used_for=('Products.Archetypes.Field.StringField',)
                 )

  registerWidget(VersionWidget,
                 title='Version',
                 description='Used with a VersionField, can display any of a number of widgets.',
                 used_for=('Products.Archetypes.Field.VersionField',)
                 )

  registerWidget(CNXMLWidget,
                 title='CNXML',
                 description='Used as a TextAreaWidget, but able to take additional validation errors.',
                 used_for=('Products.Archetypes.Field.TextField',)
                 )
except ImportError:
  pass # this is expected for Archetypes pre-1.2
