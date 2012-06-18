from RestrictedPython.Utilities import same_type
from DateTime import DateTime

def convert(obj):
    """Convert from the old style course composer (RisaCollectionEditor) to the new one (RisaCollection)"""

    parent = obj.aq_parent
    id = obj.getId()
    parent.manage_renameObjects([id], [id+'.old'])

    parent.invokeFactory(id=id, type_name='Collection')
    target = getattr(parent, id)

    # Copy metadata
    target.setTitle(obj.title)
    target.setCreated(obj.created)
    target.setRevised(obj.revised)
    target.setAuthors(obj.authors)
    target.setMaintainers(obj.maintainers)
    target.setLicensors(obj.licensors)
    target.setVersion(obj.version)
    target.setAbstract(obj.abstract)
    target.setKeywords(obj.keywords)
    target.setLicense(obj.license)
    target.setInstitution(obj.institution)
    target.setInstructor(obj.instructor)    
    target.setCode(obj.code)
    target.setHomepage(getattr(obj,'homepage',''))

    target.setState(obj.state)
    
    # Copy parameters
    params = obj.getParameters()
    if params.get('imaginaryi', '') == 'imaginaryi':
        del params['imaginaryi']

    for key, value in params.items():
        # Skip blank parameters (defaults)
        if not value or key.startswith('_') or key.startswith(' '):
            continue
        t = same_type(value, 0) and 'int' or 'string' 
        target.parameters.manage_addProperty(key, value, t)

    # Copy annotations
    if hasattr(obj, 'annotations'):
        target.manage_delObjects('annotations')
        target.manage_clone(obj.annotations, 'annotations')

    # Convert contents
    convertContents(obj, target)

    # Copy links
    for m, links in obj._links.items():
        m = target.getContainedObject(m)
        if not m:
            continue
        for l in links:
            now=DateTime()
            id = 'Link.'+now.strftime('%Y-%m-%d')+'.'+now.strftime('%M%S')
            count = 0
            while id in m.objectIds():
                id = 'Link.'+now.strftime('%Y-%m-%d')+'.'+now.strftime('%M%S')+'.'+str(count)
                count = count + 1

            m.manage_addProduct['RisaRepository'].manage_addRisaLink(id)
            m[id].edit('me', l['url'], l['title'], l['type'], int(l['strength']))

        
        
def convertContents(source, target):
    """Recursively copy contents from source to target container"""

    for id in source.order:
        obj = getattr(source, id)
        if obj.isPrincipiaFolderish:
            target.invokeFactory(id=id, type_name='SubCollection')
            c = target[id]
            c.setTitle(obj.title)
            convertContents(obj, c)
        else:
            target.invokeFactory(id=id, type_name='PublishedContentPointer')
            m = target[id]
            m.setModuleId(id)
            if obj.title != source.content.getRisaObject(id, 'latest').title:
                m.setOptionalTitle(obj.title)
