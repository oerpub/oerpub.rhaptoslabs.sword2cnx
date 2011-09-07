from __future__ import division

PARAMS = {
    'username': raw_input("Enter Connexions username: "),
    'password': raw_input("Enter Connexions password: "),
}

class Connection:
    def __init__(self, url, user_name, user_pass, download_service_document=True):
        self.url = url
        self.userName = user_name
        self.userPass = user_pass

        if download_service_document:
            self.get_service_document()
        else:
            self.sd = None

    def get_service_document(self):
        import urllib2, base64
        req = urllib2.Request(self.url)
        req.add_header('Authorization', 'Basic ' + base64.b64encode(self.userName + ':' + self.userPass))
        conn = urllib2.urlopen(req)
        self.sd = conn.read()
        conn.close()

    def create(self, payload, mimetype):
        import urllib2, base64
        req = urllib2.Request(self.url)
        req.add_header('Authorization', 'Basic ' + base64.b64encode(self.userName + ':' + self.userPass))
        req.add_header('Content-type', mimetype)
        req.add_header('Content-length',  len(payload))
        conn = urllib2.urlopen(req, payload)
        result = conn.read()
        conn.close()
        return result


print 'Retrieving service document...'
conn = Connection("http://cnx.org/sword",
                  user_name=PARAMS['username'],
                  user_pass=PARAMS['password'],
                  download_service_document=True)

def parse_service_document(serviceDoc):
    """
    Read available collections from the service document.
    """
    serviceDocLower = serviceDoc.lower()
    pos = 0
    swordCollections = []
    while True:
        # Get url
        subString = '<collection href="'
        pos0 = serviceDocLower.find(subString, pos)
        if pos0 == -1:
            break
        pos0 += len(subString)
        pos1 = serviceDocLower.find('">', pos0)
        url = serviceDoc[pos0:pos1]
        pos = pos1
        # Get collection entity extent
        posCollectionEnd = serviceDocLower.find('</collection>', pos)
        # Get title
        subString = '<atom:title>'
        pos0 = serviceDocLower.find(subString, pos)
        if (pos0 == -1) or (pos0 > posCollectionEnd):
            break
        pos0 += len(subString)
        pos1 = serviceDocLower.find('</atom:title>', pos0)
        title = serviceDoc[pos0:pos1]
        pos = pos1
        # Check that it accepts zip files
        pos0 = serviceDocLower.find('<accept>application/zip</accept>', pos)
        if (pos0 == -1) or (pos0 > posCollectionEnd):
            break
        # Store
        swordCollections.append({'url': url, 'title': title})

    return swordCollections


swordCollections = parse_service_document(conn.sd)

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
    print ' %i. %s [%s]'%(i+1, swordCollections[i]['title'],
                          swordCollections[i]['url'])
formFields['url'] = swordCollections[int(raw_input())-1]['url']

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
    conn = Connection(formFields['url'],
                      user_name=PARAMS['username'],
                      user_pass=PARAMS['password'],
                      download_service_document=False)
    response = conn.create(payload = zipFile.read(),
                           mimetype = "application/zip")
print 'Response:'
print response
