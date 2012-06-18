RhaptosCollection

  This Zope Product is part of the Rhaptos system
  (http://software.cnx.rice.edu)

  RhaptosCollection is a content object that provides editing and
  display for collections of module.  It uses RhaptosRepository for
  version control.

  A Collection does not acually contain modules, but rather contains
  pointers to modules already published.  These may point at a
  specific version of published content or at the magic 'latest'
  object that represents the most recently revised content.  In this
  way a published collection can continue to point at the latest
  version of a module without the collection itself needing to be
  updated.

  In addition to a tree-structured sequence of modules and
  subcollections, collections provide support for making
  customizations including:

    - annotations using the W3C's Annotea protocol

    - custom mathematical notation for modules written in content
      MathML

    - customized links overriding module-level links from LinkMapTool

    - an alternative stylesheet for modules viewed in the the context
      of a course (no UI yet)

Future plans

  - UI for alternative style selection

  - Display "contained" modules at the URL under the course object
    instead of setting a cookie and pointing to the published module
    URL.  This will allow people to link to and bookmark a module in a
    course.

  - Allow unpublished modules in courses

  - Drag-and-drop reordering

  - Implement a diff plugin for CMFDiffTool (thereby enabling
    patching)

  