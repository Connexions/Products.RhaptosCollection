from Acquisition import aq_inner

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _

from composer import ComposerBaseView

class CollectionTitleView(ComposerBaseView):
    """Methods facilitating collection title editing"""

    def __call__(self, *args, **kwargs):
        """Handle possible submission"""

        if not self.request.get('form.submitted'):
            return self.index()
            
        title = self.request.get('title', '').strip()

        if not title or (title == '(Untitled)'):
            self.request.set('title', self.context.Title())
            html = self.macroContent(
                '@@%s/macros/body' % self.__name__, 
                errors={'title':_('Please enter a title')}
            )
            return html

        self.context.edit(title=title)

        # Roll your own API here. JSON would be nice here, and for more complex cases 
        # we should investigate its use.
        return 'close:%s' % self.context.Title()
