"""
Library for interacting with servers supporting the SWORD version 1
protocol.
"""
from __future__ import division

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
