from Acquisition import aq_inner

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _

from composer import ComposerBaseView

class DragView(ComposerBaseView):
    """Methods facilitating collection and module location"""

    def drop(self, path, new_parent_path, previous_path=None, next_path=None):
        """Move object to new location"""

        col = self.context
        obj = col.restrictedTraverse(path)
        new_parent = col.restrictedTraverse(new_parent_path)

        old_parent = obj.aq_parent

        # Move to a different container?
        if new_parent != old_parent:
            id = obj.getId()
            cp = old_parent.manage_cutObjects([id])
            new_parent.manage_pasteObjects(cp)
            obj = new_parent._getOb(id)

        # Order within container?
        if previous_path or next_path:
            parent = obj.aq_parent
            obj_pos = parent.getObjectPosition(obj.getId())
            diff = 0
            if previous_path:
                previous = col.restrictedTraverse(previous_path)
                pos = parent.getObjectPosition(previous.getId())
                if obj_pos > pos:
                    diff = 1
                parent.moveObject(obj.getId(), pos + diff)

            elif next_path:
                next = col.restrictedTraverse(next_path)
                pos = parent.getObjectPosition(next.getId())
                if obj_pos < pos:
                    diff = 1
                parent.moveObject(obj.getId(), pos - diff)

        return
