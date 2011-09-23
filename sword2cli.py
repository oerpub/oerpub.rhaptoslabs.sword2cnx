from __future__ import division

import sys
import sword2cnx

PARAMS = {
    'username': 'user1',
    'password': 'user1',
}

print 'Retrieving service document...'
conn = sword2cnx.Connection("http://50.57.120.10:8080/rhaptos/sword/servicedocument",
                            user_name=PARAMS['username'],
                            user_pass=PARAMS['password'],
                            download_service_document=True)
if conn.sd is None:
    print 'ERROR: No service document found.'
    sys.exit()

swordCollections = sword2cnx.parse_service_document(conn.sd)

formFields = {
    "url":          None,
    "title":        None,
    "abstract":     None,
    "keywords":     None,
    "language":     "en",
    "keepUrl":      True,
    "keepTitle":    False,
    "keepAbstract": False,
    "keepKeywords": True,
}

print 'Deposit location:'
for i in range(len(swordCollections)):
    print ' %i. %s [%s]'%(i+1, swordCollections[i].title,
                          swordCollections[i].href)
formFields['url'] = swordCollections[int(raw_input())-1].href

# -------------------------
sys.exit()
# -------------------------

formFields['title'] = raw_input('Title: ').strip()
formFields['abstract'] = raw_input('Summary: ').strip()
formFields['keywords'] = raw_input('Keywords (comma-separated): ')
formFields['language'] = raw_input('Language code: ').strip()

filenames = []
while True:
    filenames.append(raw_input('Files to upload (empty to stop): '))
    if filenames[-1] == '':
        del filenames[-1]
        break

# Pre-processing before SWORD post
keywordArray = ['<bib:keywords>' + keyword + '</bib:keywords>'
                for keyword in [_.strip() for _ in formFields['keywords'].split(',')] if keyword != '']


# Create and zip METS file
import zipfile, os

zipFilename = os.tmpnam()
zipFile = open(zipFilename, "wb")
zipArchive = zipfile.ZipFile(zipFile, "w")
zipArchive.writestr('mets.xml', """<?xml version="1.0" encoding="utf-8" standalone="no" ?>
<mets ID="sort-mets_mets" OBJID="sword-mets" LABEL="DSpace SWORD Item" PROFILE="DSpace METS SIP Profile 1.0" xmlns="http://www.loc.gov/METS/" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.loc.gov/METS/ http://www.loc.gov/standards/mets/mets.xsd">

  <metsHdr CREATEDATE="2008-09-04T00:00:00">
    <agent ROLE="CUSTODIAN" TYPE="ORGANIZATION">
      <name>Unknown</name>
    </agent>
  </metsHdr>

  <dmdSec ID="sword-mets-dmd-1" GROUPID="sword-mets-dmd-1_group-1">
    <mdWrap LABEL="SWAP Metadata" MDTYPE="OTHER" OTHERMDTYPE="EPDCX" MIMETYPE="text/xml">
      <xmlData>
        <epdcx:descriptionSet xmlns:epdcx="http://purl.org/eprint/epdcx/2006-11-16/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://purl.org/eprint/epdcx/2006-11-16/ http://purl.org/eprint/epdcx/xsd/2006-11-16/epdcx.xsd">
          <epdcx:description epdcx:resourceId="sword-mets-epdcx-1">
            <epdcx:statement epdcx:propertyURI="http://purl.org/dc/elements/1.1/title">
              <epdcx:valueString>""" + formFields['title'] + """</epdcx:valueString>
            </epdcx:statement>
            <epdcx:statement epdcx:propertyURI="http://purl.org/dc/terms/abstract">
              <epdcx:valueString>""" + formFields['abstract'] + """</epdcx:valueString>
            </epdcx:statement>
            <epdcx:statement epdcx:propertyURI="http://purl.org/eprint/terms/isExpressedAs" epdcx:valueRef="sword-mets-expr-1" />
          </epdcx:description>
          <epdcx:description epdcx:resourceId="sword-mets-expr-1">
            <epdcx:statement epdcx:propertyURI="http://purl.org/dc/elements/1.1/type" epdcx:valueURI="http://purl.org/eprint/entityType/Expression" />
            <epdcx:statement epdcx:propertyURI="http://purl.org/dc/elements/1.1/type" epdcx:vesURI="http://purl.org/eprint/terms/Type" epdcx:valueURI="http://purl.org/eprint/entityType/Expression" />
          </epdcx:description>
	  <epdcx:description epdcx:resourceId="sword-mets-expr-1">
	    <epdcx:statement epdcx:propertyURI="http://purl.org/dc/elements/1.1/type" epdcx:valueURI="http://purl.org/eprint/entityType/Expression" />
	    <epdcx:statement epdcx:propertyURI="http://purl.org/dc/elements/1.1/language" epdcx:vesURI="http://purl.org/dc/terms/RFC3066">
	      <epdcx:valueString>""" + formFields['language'] + """</epdcx:valueString>
	    </epdcx:statement>
	    <epdcx:statement epdcx:propertyURI="http://purl.org/dc/elements/1.1/type" epdcx:vesURI="http://purl.org/eprint/terms/Type" epdcx:valueURI="http://purl.org/eprint/entityType/Expression" />
	    <epdcx:statement epdcx:propertyURI="http://purl.org/eprint/terms/bibliographicCitation">
	      <epdcx:valueString>
		<bib:file xmlns:bib="http://bibtexml.sf.net/">
		  <bib:entry>
                    """ +  "".join(keywordArray) + """
		  </bib:entry>
		</bib:file>
	      </epdcx:valueString>
	    </epdcx:statement>
	  </epdcx:description>
	</epdcx:descriptionSet>
      </xmlData>
    </mdWrap>
  </dmdSec>
</mets>
""")

# Zip uploaded files
for filename in filenames:
    zipArchive.write(filename, os.path.basename(filename))
zipArchive.close()

# Send zip file to SWORD interface
print 'Posting new module to Connexions...'
with open(zipFilename, "rb") as zipFile:
    conn = OldConnection(formFields['url'],
                      user_name=PARAMS['username'],
                      user_pass=PARAMS['password'],
                      download_service_document=False)
    response = conn.create(payload = zipFile.read(),
                           mimetype = "application/zip")
print 'Response:'
print response
