"""
Zope 3 Component Architecture view(s) for CollXML.

Author: J. Cameron Cooper (jccooper@rice.edu)
Copyright (C) 2009 Rice University. All rights reserved.

This software is subject to the provisions of the GNU Lesser General
Public License Version 2.1 (LGPL).  See LICENSE.txt for details.
"""

from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView

from Products.RhaptosCollection.config import PARAMETERS_EXPORT, PARAMETER_VALUE_EXPORT

def annotateContents(col, repos, contents):
    for elt in contents:
        container = elt.get('container', None)  # indicates module ref/container
        eltid = elt.get('id', None)  # indicates pub module ref only
        obpath = elt.get('path', None)
        if not container and eltid:
            revdate = col.revised
            elt['reposversion'] = [h.version for h in repos.getHistory(eltid) if h.revised < revdate][0]
            #alternately repos.getRhaptosObject(eltid, 'latest').version

            links = col.restrictedTraverse(obpath).getLinks(sequence=0)
            linkgroups = {}
            for l in links:
                lcat = l.category
                if not linkgroups.has_key(lcat):
                    linkgroups[lcat] = []
                ldata = {'url':l.target,
                         'title':l.title,
                         'strength':l.strength,
                         }
                linkgroups[lcat].append(ldata)
            elt['links'] = linkgroups
        kids = elt.get('children', None)
        if kids:
            annotateContents(col, repos, kids)

class ExportView(BrowserView):
    """View class for the CollXML export, adapting Collection.
    """
    def content_structure(self):
        context = self.context
        repos = getToolByName(context, 'content')
        contents = context.contentsTree(cookielist=[])
        annotateContents(context, repos, contents)
        
        response = self.request.RESPONSE
        response.setHeader('Content-Type', 'application/xml; charset=utf-8')
        return contents
    
    def parameters(self):
        context = self.context
        setparams = context.parameters
        params = {}
        for internal, external in PARAMETERS_EXPORT.items():
            valumap = PARAMETER_VALUE_EXPORT[internal]
            internalvalue = setparams.getProperty(internal, None)
            params[external] = valumap.get(internalvalue, internalvalue)
        
        return params

    def coltype(self):
        context = self.context
        return context.parameters.getProperty('collectionType', None)

class Download(BrowserView):
    """View class for the CollXML template download, setting filename, etc, to trigger download
    instead of view of the XML.
    """
    def download(self):
        context = self.context
        obid = context.objectId or context.getId()
        version = context.version
        if version=='**new**':
            version = 'unpublished'
        if context.isPublic():
            status = ''
        else:
            status="edited_"
        name = "%s_%s_%scollection.xml" % (obid, version, status)

        response = self.request.RESPONSE
        response.setHeader('Content-Type', 'application/xml; charset=utf-8')
        response.setHeader('Content-Disposition', 'attachment; filename=%s' % name)
        response.setHeader('Cache-Control', 'max-age=84600, s-maxage=31536000, public, must-revalidate')
        return self.context.restrictedTraverse('source_create')()

    __call__ = download

class PublishedSource(BrowserView):
    """View class for the CollXML template download, setting filename, etc, to trigger download
    instead of view of the XML.
    """
    def get(self):
        collection = self.context
        collectionId = collection.objectId
        collectionVersion = collection.id == 'latest' and collection.version or collection.id
        ptool = getToolByName(collection,'rhaptos_print')
        data = ptool.getFile(collectionId, collectionVersion, 'xml')
        bIsXmlFileCached = ( data is not None and len(data) > 0 )
        if bIsXmlFileCached:
            name = "%s_%s_collection.xml" % (collectionId, collectionVersion)
            response = self.request.RESPONSE
            response.setHeader('Content-Type', 'application/xml; charset=utf-8')
            response.setHeader('Content-Disposition', 'attachment; filename=%s' % name)
            response.setHeader('Cache-Control', 'max-age=84600, s-maxage=31536000, public, must-revalidate')
            return data
        else:
            return None

    __call__ = get
