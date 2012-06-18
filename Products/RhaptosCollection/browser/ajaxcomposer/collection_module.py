from Acquisition import aq_inner
from Products.PythonScripts.standard import html_quote, sql_quote

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _

from composer import ComposerBaseView

class CollectionModuleView(ComposerBaseView):
    """Methods facilitating collection module addition"""

    def __call__(self, *args, **kwargs):
        """Handle possible submission"""

        if not self.request.get('form.submitted'):
            return self.index()

        action = self.request.get('form.action')

        if not action:
            # Plain post and reload
            html = self.macroContent(
                    '@@%s/macros/body' % self.__name__, 
                    **self.request.form
                )
            return html

        if action == 'submit':
            # Persist changes. The name addModulesToCourse is a legacy misnomer.
            context = aq_inner(self.context)
            ids = self.request.get('ids', [])
            context.addModulesToCourse(
                ids=ids, 
                redirect=False
            )
            # Result must be parseable by javascript           
            result = '['
            counter = 0
            for id in ids:
                ob = getattr(context, id, None)
                if ob is not None:
                    if counter:
                        result += ','
                    counter += 1
                    line = "{'nodeurl':'%s', 'text': '%s', 'uid':'%s', 'nodeid':'%s', 'version':'%s'}" % \
                        (ob.absolute_url(), ob.Title().replace("'", "\\'"), ob.UID(), ob.getId(), str(ob.version))
                    result += line
            result += ']'
            return 'close:'+result
