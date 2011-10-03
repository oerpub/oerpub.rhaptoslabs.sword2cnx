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

class Sword2CnxException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return message

def parse_service_document(serviceDoc):
    """
    Read available collections from the service document.
    """
    if len(serviceDoc.workspaces) != 1:
        raise Sword2CnxException("This is not a Connexions service document.")
    return serviceDoc.workspaces[0][1]

# ----------------------------

def upload_multipart(connection, title, summary, language, keywords, files, unicodeEncoding='utf8'):
    # Create and zip METS file
    import zipfile
    from StringIO import StringIO

    zipFile = StringIO('')
    zipArchive = zipfile.ZipFile(zipFile, "w")
    mets = create_mets(title, summary, language, keywords)
    if isinstance(mets, unicode):
        mets = mets.encode(unicodeEncoding)
    zipArchive.writestr('mets.xml', mets)

    # Zip uploaded files
    for filename in files:
        zipArchive.writestr(filename, files[filename].read())
    zipArchive.close()

    # Send zip file to SWORD interface
    zipFile.seek(0)
    response = connection.create(payload = zipFile.read(),
                                 mimetype = "application/zip")
    """
    with open(zipFilename, "rb") as zipFile:
        response = connection.create(payload = zipFile.read(),
                                     mimetype = "application/zip")
    os.unlink(zipFilename)
    """

    # Clean-up
    return response
