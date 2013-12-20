import os
import urllib
import webapp2
import logging

from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import mail

class CronTask(webapp2.RequestHandler):
  def get(self):
    try:
        subject = "cron jobs checking"
        sender_address = "k.sripradha@gmail.com"
        body ="You have recieved this mail as a result of cron jobs "
        user_address = "k.sripradha@gmail.com"
        logging.info('all parameters ready for mailing')
        mail.send_mail(sender_address, user_address, subject, body)
        logging.info('mail sent! ')
    except:
        logging.error('Not able to send mail! sorry:-(')

app = webapp2.WSGIApplication([('/crontask',CronTask)],
                              debug=True)