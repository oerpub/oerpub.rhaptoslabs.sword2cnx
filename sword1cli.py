"""
Command line client using SWORD version 1 to push content to
Connexions.
"""
from __future__ import division
import sword1cnx
import os

PARAMS = {
    'username': raw_input("Enter Connexions username: "),
    'password': raw_input("Enter Connexions password: "),
}

print 'Retrieving service document...'
conn = sword1cnx.Connection("http://cnx.org/sword",
                            user_name=PARAMS['username'],
                            user_pass=PARAMS['password'],
                            download_service_document=True)

swordCollections = sword1cnx.parse_service_document(conn.sd)

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

# Send zip file to SWORD interface
print 'Posting new module to Connexions...'
conn = sword1cnx.Connection(formFields['url'],
                            user_name=PARAMS['username'],
                            user_pass=PARAMS['password'],
                            download_service_document=False)
response = sword1cnx.upload_multipart(
    conn, formFields['title'], formFields['abstract'], formFields['language'],
    ",".split(formFields['keywords']), [{os.path.basename(filename): open(filename,'rb')} for filename in filenames])

print 'Response:'
print response
