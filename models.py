from google.appengine.ext import ndb


class Note(ndb.Model):
    kindergartenName = ndb.StringProperty()
    kindergartenMenu = ndb.StringProperty()
