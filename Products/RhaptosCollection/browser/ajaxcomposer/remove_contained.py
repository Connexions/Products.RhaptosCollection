from Acquisition import aq_inner

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _

from composer import ComposerBaseView

class RemoveContainedView(ComposerBaseView):
    """Remove contained objects"""

    def __call__(self, *args, **kwargs):
        """Handle possible submission"""

        if not self.request.get('form.submitted'):
            return self.index()

        context = aq_inner(self.context)
        parent = context.aq_parent
        parent.manage_delObjects([context.getId()])

        return 'close:%s' % context.Title()

    @property
    def number_of_subcollection_descendants(self):            
        pc = getToolByName(self.context, 'portal_catalog')
        brains = pc(
            portal_type='SubCollection',
            path='/'.join(self.context.getPhysicalPath())
        )
        return len(brains)-1

    @property
    def number_of_module_descendants(self):            
        pc = getToolByName(self.context, 'portal_catalog')
        brains = pc(
            portal_type='PublishedContentPointer',
            path='/'.join(self.context.getPhysicalPath())
        )
        return len(brains)
