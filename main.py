import os
import jinja2
import webapp2
from google.appengine.ext import db
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape= True)

class Handler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)

	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))

class BlogData(db.Model):
	subject = db.StringProperty(required = True)
	content = db.TextProperty(required = True)
	date = db.DateTimeProperty(auto_now_add =True)
	
class BlogPage(Handler):
	def render_data(self):
		blogdata = db.GqlQuery("SELECT * FROM BlogData ORDER BY date DESC limit 10")
		self.render("blog.html", blogdata = blogdata)
	def get(self):
		self.render_data()



class NewPostHandler(Handler):
	def get(self):
		self.render("newpost.html")
	def post(self):
		subject = self.request.get('subject')
		content = self.request.get('content')
		error_data = False
		params = dict(subject = subject, content = content)
		if len(subject) == 0 and len(content) == 0:
			params['errorsubject'] = "Please, add subject!"
			params['errorcontent'] = "Please, add content!"
			error_data = True
		elif len(content) == 0:
			params['errorcontent'] = "Please, add content!"
			error_data = True
		elif len(subject) == 0:
			params['errorsubject'] = "Please, add subject!"
			error_data = True

		if error_data:
			self.render("newpost.html", **params)
		else:
			b = BlogData(subject = subject, content = content)
			b.put()
			self.redirect('/%s' %str(b.key().id()))

class PremHandler(Handler):
	def get(self, id):
		blogs = BlogData.get_by_id(int(id))
		date = blogs.date
		subject = blogs.subject
		content = blogs.content
		params = dict(subject=subject, date=date, content=content, link='/')
		self.render("premlink.html", **params)



app = webapp2.WSGIApplication([('/', BlogPage), ('/newpost', NewPostHandler),('/(\d+)', PremHandler)], debug = True)