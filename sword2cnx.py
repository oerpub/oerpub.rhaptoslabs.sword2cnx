"""
Library for interacting with Connexions through its SWORD version 2
API.

Author: Carl Scheffler
Copyright (C) 2011 Katherine Fletcher.

Funding was provided by The Shuttleworth Foundation as part of the OER
Roadmap Project.

If the license this software is distributed under is not suitable for
your purposes, you may contact the copyright holder through
oer-roadmap-discuss@googlegroups.com to discuss different licensing
terms.

This file is part of oerpub.rhaptoslabs.sword2cnx

Sword2Cnx is free software: you can redistribute it and/or modify it
under the terms of the GNU Lesser General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Sword2Cnx is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with Sword1Cnx.  If not, see <http://www.gnu.org/licenses/>.
"""
from __future__ import division
from sword2 import *
from sword2.compatible_libs import etree

class Sword2CnxException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return message

class MetaData(Entry):
    """
    An extension of the sword2.Entry class for Atom entries. This
    class adds a few default namespaces to the entry and allows you to
    specify additional namespaces on instantiation.

    The base namespaces is http://www.w3.org/2005/Atom and the
    remaining default namespaces are

      dcterms = http://purl.org/dc/terms/
      oerdc = http://cnx.org/aboutus/technology/schemas/oerdc
      xsi = http://www.w3.org/2001/XMLSchema-instance

    """

    defaultNamespaces = {
        '': 'http://www.w3.org/2005/Atom',
        'dcterms': 'http://purl.org/dc/terms/',
        'oerdc': 'http://cnx.org/aboutus/technology/schemas/oerdc',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
    }

    def __init__(self, metadata, namespaces = {}):
        """
        Namespaces are passed as key-value pairs in the dictionary, e.g.

          namespaces = {'dcterms': 'http://purl.org/dc/terms/'}

        Any of the default namespaces can be overwritten by supplying
        them in the input dictionary.

        Entries in the metadata can be specified with a namespace
        prefix.

          metadata = {'title': 'Great Expectations',
                      'dcterms:author': 'Charles Dickens'}
        """

        # Combine default and user-specified namespace dictionaries
        allNamespaces = dict(self.defaultNamespaces)
        allNamespaces.update(namespaces)

        # Replace default sword2.Entry bootstrap string
        self.bootstrap = '<?xml version="1.0"?>\n  <entry'
        for prefix, url in allNamespaces.iteritems():
            if prefix == '':
                self.bootstrap += ' xmlns="%s"'%url
            else:
                self.bootstrap += ' xmlns:%s="%s"'%(prefix, url)
        self.bootstrap += '>\n  </entry>'

        # Call parent constructor
        Entry.__init__(self)

        # Register namespaces
        self.add_ns = []
        for prefix, url in allNamespaces.iteritems():
            if prefix == '':
                continue
            etree.register_namespace(prefix, url)
            self.add_ns.append(prefix)
            NS[prefix] = "{%s}%%s"%url

        # Record metadata
        self.add_fields(**metadata)
    
    # Overload add_field method to handle attributes
    def add_field(self, key, value, attributes={}):
        """
        Append a single key-value pair to the metadata, e.g.
        
          e.add_field("myprefix:foo", "value")
        
        You can use MetaData.add_fields method instead for a neater
        interface that does not allow for attributes.

        The optional attributes argument is used to supply key-value
        pairs for the attributes of the new element, e.g.
        
          e.add_field("myprefix:foo", "value",
                      {"otherprefix:attribname": "attribvalue"})

        Note that the atom:author field is handled differently, as it
        requires certain fields from the author. This means of entry
        is not supported for other elements.
        
          e.add_field("author", {'name':".....",
                                 'email':"....",
                                 'uri':"...."} )
        """
        from sword2.compatible_libs import etree

        namespacedAttributes = {}
        for k, v in attributes.iteritems():
            if ":" in k: # XML namespace, eg 'dcterms:title'
                nmsp, tag = k.split(":", 1)
                if nmsp in self.add_ns:
                    namespacedAttributes[NS[nmsp] % tag] = v
                    continue
            namespacedAttributes[k] = v
        attributes = namespacedAttributes

        if key in self.atom_fields:
            # These should be unique!
            old_e = self.entry.find(NS['atom'] % key)
            if old_e == None:
                e = etree.SubElement(self.entry, NS['atom'] % key, attrib=attributes)
                e.text = value
            else:
                old_e.text = value
        elif ":" in key:
            # possible XML namespace, eg 'dcterms:title'
            nmsp, tag = key.split(":", 1)
            if nmsp in self.add_ns:
                e = etree.SubElement(self.entry, NS[nmsp] % tag, attrib=attributes)
                e.text = value
        elif key == "author" and isinstance(value, dict):
            self.add_author(**value)

    # Overload add_fields method to handle list values
    def add_fields(self, **kw):
        """
        Add in multiple elements in one method call, e.g.
        
          e.add_fields(dcterms:title="Origin of the Species",
                       dcterms:contributor="Darwin, Charles")

        If a value is not a string and is iterable, it will result in
        multiple entries. So this

          e.add_fields(dcterms_subject=["cats","dogs"])

        is equivalent to this

          e.add_fields(dcterms:subject="cats")
          e.add_fields(dcterms:subject="dogs")
        """
        for key, value in kw.iteritems():
            if isinstance(value, basestring):
                self.add_field(key, value)
            else:
                try:
                    iterator = iter(value)
                    for value in iterator:
                        self.add_field(key, value)
                except TypeError:
                    raise TypeError, "Cannot interpret type (%s) for key (%s)"%(str(type(value)), key)

def get_workspaces(connection):
    """
    Read available collections from the service document. The service
    document will be loaded from the server if necessary.

    Inputs:
      connection - A sword2.Connection object

    Returns:
      A list of sword2.SDCollection objects
    """
    if connection.sd is None:
        connection.get_service_document()
        if connection.sd is None:
            raise Sword2CnxException, "Could not load service document."
    if len(connection.sd.workspaces) != 1:
        raise Sword2CnxException("This is not a Connexions service document.")
    return connection.sd.workspaces[0][1]
