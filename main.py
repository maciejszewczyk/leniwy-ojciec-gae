#!/usr/bin/env python

import webapp2
import os
import jinja2
from iprzedszkole import *
from models import Note
from google.appengine.ext import ndb
from google.appengine.api import memcache
import logging

jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
expirationTime = 600

class MainHandler(webapp2.RequestHandler):
    def get(self):
        logging.debug("Sprawdzam czy dane sa w memcache")
        data = memcache.get('jadlospis')
        if data is None:
            logging.debug("Danych nie ma w memcache, sprawdzam czy dane sa w NDB")
            q = Note.get_by_id('jadlospis')
            if q is None:
                logging.debug("Danych nie ma w NDB")
                data = 'Brak danych w bazie'
            else:
                logging.debug("Dane sa w NDB")
                data = q.kindergartenMenu
                logging.debug("Dodaje dane do memcache")
                memcache.add(key='jadlospis', value=data, time=expirationTime)
        else:
            logging.debug("Dane sa w memcache")

        template_context = {
            'body': data
        }
        template = jinja_env.get_template('templates/main.html')
        self.response.out.write(template.render(template_context))


class CronUpdate(webapp2.RequestHandler):
    def post(self):
        self.abort(405, headers=[('Allow', 'GET')])

    def get(self):
        if 'X-AppEngine-Cron' not in self.request.headers:
            self.error(403)
        przedszkole = iPrzedszkole('<nazwa przedszkola>', '<uzytkownik>', '<haslo>')
        menu = przedszkole.jadlospis()
        if menu is None:
            menu = "Weekend :)"
        note = Note(id='jadlospis')
        note.kindergartenMenu = menu
        note.put()
        memcache.set(key='jadlospis', value=note.kindergartenMenu, time=expirationTime)


app = webapp2.WSGIApplication([
    ('/', MainHandler), ('/update', CronUpdate),
], debug=False)