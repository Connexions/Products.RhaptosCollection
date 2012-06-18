import re
from random import randint

from Acquisition import aq_inner
from Products.PythonScripts.standard import html_quote

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.validation.validators.BaseValidators import protocols

from Products.LinkMapTool.LinkMapTool import ExtendedLink

from composer import ComposerBaseView

class FeaturedLinksView(ComposerBaseView):
    """Methods facilitating featured links editing"""

    def published_module_url(self):
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        content = portal.content
        id = self.context.getId()
        return content[id].absolute_url() + '/' + self.context.version

    @property
    def random_id(self):
        return 'el-%s' % randint(10000, 10000000)

    def __call__(self, *args, **kwargs):
        """Handle possible submission"""
        
        if not self.request.get('form.submitted'):
            return self.index()

        context = aq_inner(self.context)
        action = self.request.get('form.action')

        id = self.request.get('id', '')

        if action in ('create', 'edit'):

            # Form variables
            title = self.request.get('title', '').strip()
            category = self.request.category
            strength = self.request.strength
            url = self.request.get('url', '').strip()
            connexions_id = self.request.get('connexions_id', '').strip()
            if action == 'create':
                urlorid = self.request.urlorid
                version = self.request.get('version', '').strip() or 'latest'
            if action == 'edit':
                urlorid = 'url'

            # Validate the form
            errors = {}
    
            if not title:
                errors['title'] = _("Please enter a title")

            if urlorid == 'url':
                if not url:
                    errors['url'] = _("Please enter an URL")
                else:
                    # Validate url
                    m = re.match(r'(%s)s?://[^\s\r\n]+' % '|'.join(protocols), url)
                    if m is None:
                        errors['url'] = _("Please enter a valid URL")
                target = url

            elif urlorid == 'id':
                if not connexions_id:
                    errors['connexions_id'] = _("Please enter a Connexions ID")
                else:
                    # Does target exist?
                    try:
                        target = context.content.getRhaptosObject(connexions_id, version).url()
                    except KeyError:
                        errors['connexions_id'] = _("Please enter a valid Connexions ID and optional version")

            if errors:
                if action == 'create':
                    html = self.macroContent(
                        '@@%s/macros/newlink' % self.__name__, 
                        errors=errors
                    )
                if action == 'edit':
                    html = self.macroContent(
                        '@@%s/macros/editlink' % self.__name__, 
                        errors=errors,
                        **self.request.form
                    )
                return html

        # Generate the response HTML snippet (new strength icon, title, link)
        if action == 'edit':
            # Construct a temporary ExtendedLink so the macro can be rendered
            link = ExtendedLink('dummy', context.absolute_url(), target, 
                category, int(strength), title
            )
            html = self.macroContent(
                    '@@%s/macros/editlink_label' % self.__name__, 
                    link=link
            )

        # Change the data on the server
        title = self.request.title.strip()
        category = self.request.category
        strength = self.request.strength
        url = self.request.url.strip()

        if action == 'remove':
            html = ''
            context.manage_delObjects([id])

        elif action == 'create':
            link = context.addLink(url, title, category, int(strength))
            html = self.macroContent(
                    '@@%s/macros/editlink_row' % self.__name__,
                    link=link,
                    target=target,
                    marker_class='create'
            )

        elif action == 'edit':
            link = context._getOb(id)
            link.edit(context.absolute_url(), target=url, title=title, 
                category=category, strength=int(strength)
            )

        return 'close:'+html
