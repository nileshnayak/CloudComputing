import os
import urllib
import webapp2
import logging
import cgi


from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import ndb
from google.appengine.api import users

DEFAULT_USER_NAME = "k.sripradha@gmail.com"

def user_key(user_name=DEFAULT_USER_NAME):
    """Constructs a Datastore key for a user entity with username."""
    return ndb.Key('User', user_name)

class EachUser(ndb.Model):
    """Models an individual user entry with blob key"""
    author = ndb.UserProperty()
    blobkey = ndb.BlobKeyProperty(required=False)

class MainHandler(webapp2.RequestHandler):
  def get(self):
    upload_url = blobstore.create_upload_url('/upload')
    self.response.out.write("""<html><link rel="stylesheet" href="/stylesheets/common.css" type="text/css" media="screen">
    <script src="/stylesheets/min.js"></script>
  
    <script>
	

function displayInline(contentUrl) {
  var iframe =
      '<iframe src="' + contentUrl + '" class="inlined-content"></iframe>';
  $('#inlined_content').html(iframe);
}

$(document).ready(function() {
 

  $('[data-action=delete]').click(function() {
    return confirm('Are you sure?');
  });

  $('#display_inline').click(function() {
    var url = $(this).data('content-uri');
	var fileName = $('#file_search').find(":selected").val();
	uri=url+fileName;
    displayInline(uri);
  });

  
});</script><body><div class='main'><h2> Cloud Music Box</h2></div>""")
    self.response.out.write('<center><form action="%s" method="POST" enctype="multipart/form-data">' % upload_url)
    self.response.out.write("""Upload File:<input type="file" name="file"><input type="submit" name="submit" class="myButton" value="Submit"> </form>""")
    load_url = blobstore.create_upload_url('/list')
    #self.response.out.write('<form action="%s" method="POST" enctype="multipart/form-data">' % load_url)
    #self.response.out.write("""Load File:<input type="submit"
        #name="submit" class="myButton" value="Submit"> </form>""")
    
    #blob_obj = blobstore.BlobInfo.all()
    qry = EachUser.query(EachUser.author == users.get_current_user())
    
    self.response.out.write('<br/><br/><table><tr><th>File Name</th><th>Play</th></tr>')
    for q in qry:
      blob_obj = blobstore.BlobInfo.get(q.blobkey)
      self.response.write('<tr><td>%s :</td>'  %blob_obj.filename)
      self.response.write("""<td><audio controls><source src="/serve/%s" type="audio/mpeg"></audio></td></tr>""" %q.blobkey)
    self.response.out.write('</table>')
    #self.response.out.write('<input type="button" id="try" value="list" onclick=/>')
    self.response.out.write("""
   <div id="inlined_content">
	
    </div><div id="alert"><!--<img src="/images/dogs-listening.jpg"/>--></center>""")
    self.response.out.write('</body></html>')
    

class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
  def post(self):
    #try:
    upload_files = self.get_uploads('file')  # 'file' is file upload field in the form
    blob_info = upload_files[0]
    user_name = users.get_current_user();
    user = user_name.nickname()

    eachuser = EachUser(parent=user_key(user))

    logging.info(user_name)
    eachuser.blobkey = blob_info.key()
    eachuser.author = user_name
    eachuser.put()
    self.redirect('/')
	
 
class Load(blobstore_handlers.BlobstoreUploadHandler):
  def post(self):
    src = self.request.get_all("file_search")
    #self.response.out.write('%s' %src[0])
    play = src[0]
    self.redirect('/serve/%s' %play)
class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
  def get(self, resource):
    resource = str(urllib.unquote(resource))
    blob_info = blobstore.BlobInfo.get(resource)
    self.send_blob(blob_info)


app = webapp2.WSGIApplication([('/', MainHandler),
                               ('/upload', UploadHandler),
							   ('/list', Load),
                               ('/serve/([^/]+)?',ServeHandler)],
                              debug=True)
