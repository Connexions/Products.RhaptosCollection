from Acquisition import aq_inner
from Products.PythonScripts.standard import html_quote

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _

from composer import ComposerBaseView

class CollectionSubcollectionView(ComposerBaseView):
    """Methods facilitating add of subsollection to a (sub)collection"""

    def __call__(self, *args, **kwargs):
        """Handle possible submission"""

        if not self.request.get('form.submitted'):
            return self.index()
            
        titles = [t.strip() for t in self.request.get('titles', '').split('\n') if t.strip()]

        if not titles:
            html = self.macroContent(
                '@@%s/macros/body' % self.__name__, 
                errors={'titles':_('Please enter one or more subcollection titles')}
            )
            return html

        # Create subcollections
        context = aq_inner(self.context)
        created = []
        for title in titles:        
            id = context.invokeFactory(
                'SubCollection', 
                context.generateUniqueId('subcollection'), 
                title=title
            )
            created.append(context._getOb(id))

        # Result must be parseable by javascript           
        result = '['
        counter = 0
        for ob in created:
            if counter:
                result += ','
            counter += 1
            line = "{'nodeurl':'%s', 'text': '%s', 'nodeid':'%s', 'version':'%s', 'children':[]}" % \
                        (ob.absolute_url(), ob.Title().replace("'", "\\'"), ob.getId(), str(ob.version))
            result += line
        result += ']'
        return 'close:'+result
