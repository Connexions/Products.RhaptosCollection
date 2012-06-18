from Acquisition import aq_inner

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _

from composer import ComposerBaseView

class ModuleTitleView(ComposerBaseView):
    """Methods facilitating module title editing"""

    def original_title(self):
        """ Title accessor is overridden in BaseContentPointer making access 
            to original title difficult.
        """
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        content = portal.content
        id = self.context.getId()
        return content[id].latest.Title()

    def published_module_url(self):
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        content = portal.content
        id = self.context.getId()
        return content[id].absolute_url() + '/' + self.context.version

    def published_module_version_history_url(self):
        return self.published_module_url() + '/content_info#cnx_history_header'

    def __call__(self, *args, **kwargs):
        """Handle possible submission"""

        if not self.request.get('form.submitted'):
            return self.index()
            
        optionalTitle = self.request.optionalTitle.strip()
        version = self.request.version
        specific = self.request.specific

        self.context.edit(
            optionalTitle=optionalTitle,
            version=(version == 'latest') and 'latest' or specific
        )

        return 'close:%s' % self.context.Title()
