"""
Zope 3 Component Architecture export package view(s) for Collection XML.

Author: Brian West (bnwest@rice.edu)
Copyright (C) 2009 Rice University. All rights reserved.

This software is subject to the provisions of the GNU Lesser General
Public License Version 2.1 (LGPL).  See LICENSE.txt for details.
"""

from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView

class CompleteZip(BrowserView):
    """View class for the collection xml zip file, which also contains all of the module files as well.
    """
    def get(self):
        collection = self.context
        request = self.request

        collection_id = collection.objectId or context.getId()
        collection_version = collection.id == 'latest' and collection.version or collection.id

        ptool = getToolByName(self,'rhaptos_print')
        data = ptool.getFile(collection_id, collection_version, 'complete.zip')
        bIsZipFileCached = ( data is not None and len(data) > 0 )
        if not bIsZipFileCached:
            data = None

        if data is not None:
            zipfilename = '%s_%s_complete.zip' % (collection_id,collection_version)
            request.RESPONSE.setHeader('Content-Type', 'application/zip')
            request.RESPONSE.setHeader('Content-Disposition', 'attachment; filename=%s' % zipfilename)
            request.RESPONSE.setHeader('Cache-Control', 'max-age=84600, s-maxage=31536000, public, must-revalidate')
        return data

    __call__ = get

class OfflineZip(BrowserView):
    """View class for the collection xml zip file, which also contains all of the module files as well.
    """
    def get(self):
        collection = self.context
        request = self.request

        collection_id = collection.objectId or context.getId()
        collection_version = collection.id == 'latest' and collection.version or collection.id

        ptool = getToolByName(self,'rhaptos_print')
        data = ptool.getFile(collection_id, collection_version, 'offline.zip')
        bIsZipFileCached = ( data is not None and len(data) > 0 )
        if not bIsZipFileCached:
            data = None

        if data is not None:
            zipfilename = '%s_%s_offline.zip' % (collection_id,collection_version)
            request.RESPONSE.setHeader('Content-Type', 'application/zip')
            request.RESPONSE.setHeader('Content-Disposition', 'attachment; filename=%s' % zipfilename)
            request.RESPONSE.setHeader('Cache-Control', 'max-age=84600, s-maxage=31536000, public, must-revalidate')
        return data

    __call__ = get

class EpubZip(BrowserView):
    """View class for the collection xml zip file, which also contains all of the module files as well.
    """
    def get(self):
        collection = self.context
        request = self.request

        collection_id = collection.objectId or context.getId()
        collection_version = collection.id == 'latest' and collection.version or collection.id

        ptool = getToolByName(self,'rhaptos_print')
        data = ptool.getFile(collection_id, collection_version, 'epub')
        bIsZipFileCached = ( data is not None and len(data) > 0 )
        if not bIsZipFileCached:
            data = None

        if data is not None:
            zipfilename = '%s_%s.epub' % (collection_id,collection_version)
            request.RESPONSE.setHeader('Content-Type', 'application/epub+zip')
            request.RESPONSE.setHeader('Content-Disposition', 'attachment; filename=%s' % zipfilename)
            request.RESPONSE.setHeader('Cache-Control', 'max-age=84600, s-maxage=31536000, public, must-revalidate')
        return data

    __call__ = get

class LatexFromPrint(BrowserView):
    """View class for the latex files generated in PDF generation aka Print.
    """
    def get(self):
        collection = self.context
        request = self.request

        collection_id = collection.objectId or context.getId()
        collection_version = collection.id == 'latest' and collection.version or collection.id

        ptool = getToolByName(self,'rhaptos_print')
        data = ptool.getFile(collection_id, collection_version, 'latex.zip')
        bIsZipFileCached = ( data is not None and len(data) > 0 )
        if not bIsZipFileCached:
            data = None

        if data is not None:
            zipfilename = '%s_%s_latex.zip' % (collection_id,collection_version)
            request.RESPONSE.setHeader('Content-Type', 'application/zip')
            request.RESPONSE.setHeader('Content-Disposition', 'attachment; filename=%s' % zipfilename)
            request.RESPONSE.setHeader('Cache-Control', 'max-age=84600, s-maxage=31536000, public, must-revalidate')
        return data

    __call__ = get

