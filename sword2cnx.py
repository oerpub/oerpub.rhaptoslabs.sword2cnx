"""
Library for interacting with Connexions through its SWORD version 2
API.
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
