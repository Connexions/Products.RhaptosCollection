import types

from Acquisition import aq_inner

from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

class ComposerBaseView(BrowserView):
    """Provide common methods used by the various composer components"""

    header_macros = ZopeTwoPageTemplateFile('macro_wrapper.pt')

    """_macroContent and macroContent are taken and slightly adapted from 
    https://svn.plone.org/svn/plone/plone.app.kss/branches/hedley-macrocontent/plone/app/kss/plonekssview.py
    """
    def _macroContent(self, provider, macro_name, context=None, **kw):
        # Determine context to use for rendering
        if context is None:
            render_context = aq_inner(self.context)
        else:
            render_context = context

        # Build extra context. These variables will be in
        # scope for the macro.        
        extra_context = {'options':{}}
        extra_context.update(kw)
        the_macro = None

        # Determine what type of provider we are dealing with
        if isinstance(provider, types.StringType):
            # Page template or browser view. Traversal required.
            pt_or_view = render_context.restrictedTraverse(provider)
            if provider.startswith('@@'):            
                the_macro = pt_or_view.index.macros[macro_name]
                if not extra_context.has_key('view'):
                    extra_context['view'] = pt_or_view
            else:          
                the_macro = pt_or_view.macros[macro_name]

            # template_id seems to be needed, so add to options
            # if it is not there
            if not extra_context['options'].has_key('template_id'):
                extra_context['options']['template_id'] = provider.split('/')[-1]

        # Adhere to header_macros convention. Setting the_macro here
        # ensures that code calling this method cannot override the_macro.
        extra_context['options']['the_macro'] = the_macro

        # If context is explicitly passed in then make available        
        if context is not None:
            extra_context['context'] = context

        # Bizarrely for the Rhaptos stack we have to make a call to pt_macros!
        wtf = self.header_macros.__of__(render_context).pt_macros()
        content = self.header_macros.__of__(render_context).pt_render(
                    extra_context=extra_context)

        # IE6 has problems with whitespace at the beginning of content
        content = content.strip()

        # Always encoded as utf-8
        content = unicode(content, 'utf-8')
        return content

    def macroContent(self, macropath, **kw):
        'Renders a macro and returns its text'
        path = macropath.split('/')
        if len(path) < 2 or path[-2] != 'macros':
            raise RuntimeError, 'Path must end with macros/name_of_macro (%s)' % (repr(macropath), )
        # needs string, do not tolerate unicode (causes but at traverse)
        jointpath = '/'.join(path[:-2]).encode('ascii')

        # put parameters on the request, by saving the original context
        self.request.form, orig_form = kw, self.request.form
        content = self._macroContent(
                    provider=jointpath, 
                    macro_name=path[-1],                  
                    **kw
                    )
        self.request.form = orig_form

        return content
