import webapp2
from google.appengine.api import users
from google.appengine.ext import ndb
import jinja2
import os
import logging
import json
import csv

JINJA_ENVIRONMENT = jinja2.Environment(
	loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
	extensions=['jinja2.ext.autoescape'],
	autoescape=True)

class thesisentry(ndb.Model):
	THESIS_YEAR = ndb.StringProperty()
	THESIS_TITLE = ndb.StringProperty(indexed=True)
	THESIS_ABSTRACT = ndb.TextProperty()
	THESIS_ADVISER = ndb.KeyProperty(kind='Faculty',indexed=True)
	THESIS_SECTION = ndb.StringProperty()
	THESIS_DEPARTMENT = ndb.KeyProperty(kind='Department',indexed=True)
	PROPONENT = ndb.KeyProperty(kind='Student', repeated=True)
	THESIS_RELATED = ndb.StringProperty(repeated=True)

	THESIS_AUTHOR = ndb.KeyProperty(indexed=True)
	Date = ndb.DateTimeProperty(auto_now_add=True)

	@classmethod
	def get_by_name(model, name):
		try:
			student = model.query(model.THESIS_TITLE == name)
			return student.get()
		except Exception:
			return None

class User(ndb.Model):
	email = ndb.StringProperty(indexed=True)
	first_name = ndb.StringProperty()
	last_name = ndb.StringProperty()
	phone_number = ndb.IntegerProperty()
	is_admin = ndb.BooleanProperty()
	date_created = ndb.DateTimeProperty(auto_now_add=True)

class Faculty(ndb.Model):
	faculty_title = ndb.StringProperty(indexed=True)
	faculty_fname = ndb.StringProperty(indexed=True)
	faculty_sname = ndb.StringProperty(indexed=True)
	faculty_full = ndb.StringProperty(indexed=True)
	faculty_email = ndb.StringProperty(indexed=True)
	faculty_phone = ndb.StringProperty(indexed=True)
	faculty_bday = ndb.StringProperty(indexed=True)
	faculty_department = ndb.KeyProperty(kind='Department', indexed=True)
	date_created = ndb.DateTimeProperty(auto_now_add=True)

	@classmethod
	def get_by_name(model, name):
		try:
			adviser = model.query(model.faculty_full == name)
			return adviser.get()
		except Exception:
			return None

	@classmethod
	def get_by_keyname(model, key):
		try:
			return model.get_by_id(key)
		except Exception:
			return None

class Student(ndb.Model):
	first_name = ndb.StringProperty(indexed=True)
	last_name = ndb.StringProperty(indexed=True)
	full_name = ndb.StringProperty(indexed=True)
	e_mail = ndb.StringProperty(indexed=True)
	contact = ndb.StringProperty(indexed=True)
	student_num = ndb.StringProperty(indexed=True)
	student_grad = ndb.IntegerProperty(indexed=True)
	b_day = ndb.StringProperty(indexed=True)
	student_dept = ndb.KeyProperty(kind='Department', indexed=True)
	student_name_portions = ndb.StringProperty(repeated=True)
	date_created = ndb.DateTimeProperty(auto_now_add=True)

	@classmethod
	def get_by_name(model, name):
		try:
			student = model.query(model.full_name == name)
			return student.get()
		except Exception:
			return None

class University(ndb.Model):
	univ_name = ndb.StringProperty(indexed=True)
	univ_init = ndb.StringProperty(indexed=True)
	univ_add = ndb.StringProperty(indexed=True)
	date_created = ndb.DateTimeProperty(auto_now_add=True)

class Department(ndb.Model):
	dept_college = ndb.KeyProperty(kind='College', indexed=True)
	dept_name = ndb.StringProperty(indexed=True)
	dept_chair = ndb.KeyProperty(kind='Faculty',indexed=True)
	date_created = ndb.DateTimeProperty(auto_now_add=True)

	@classmethod
	def get_by_name(model, name):
		try:
			department = model.query(model.dept_name == name)
			return department.get()
		except Exception:
			return None

class College(ndb.Model):
	college_univ = ndb.KeyProperty(kind='University',indexed=True)
	college_name = ndb.StringProperty(indexed=True)
	college_depts = ndb.KeyProperty(repeated=True)
	date_created = ndb.DateTimeProperty(auto_now_add=True)
						
class MainPageHandler(webapp2.RequestHandler):
	def get(self):
		loggedin_user = users.get_current_user()
		if loggedin_user:
			user_key = ndb.Key('User', loggedin_user.user_id())
			user = user_key.get()
			if user:
				if user.is_admin:
					link_text = 'Logout'
					links = {}
					links['Faculty'] = {'List':'/faculty/list','Create Entry':'/faculty/create'}
					links['Students'] = {'List':'/student/list','Create Entry':'/student/create'}
					links['Department'] = {'List':'/department/list','Create Entry':'/department/create'}
					links['Universities'] = {'List':'/university/list','Create Entry':'/university/create'}
					links['Colleges'] = {'List':'/college/list','Create Entry':'/college/create'}
					links['Theses'] = {'List':'/thesis/list/all','Create Entry':'/thesis/create'}
					template_values = {
						'links':links,
						'search_url':'/search',
						'logout_url': users.create_logout_url('/'),
						'user': user.first_name
					}
					template = JINJA_ENVIRONMENT.get_template('/pages/main.html')
					self.response.write(template.render(template_values))
				else:
					link_text = 'Logout'
					links = {}
					links['Faculty'] = {'List':'/faculty/list'}
					links['Students'] = {'List':'/student/list'}
					links['Universities'] = {'List':'/university/list'}
					links['Colleges'] = {'List':'/college/list'}
					links['Departments'] = {'List':'/department/list'}
					links['Theses'] = {'List':'/thesis/list/all'}
					template_values = {
						'links':links,
						'search_url':'/search',
						'logout_url': users.create_logout_url('/'),
						'user': user.first_name
					}
					template = JINJA_ENVIRONMENT.get_template('/pages/main.html')
					self.response.write(template.render(template_values))
			else:
				self.redirect('/register')

		else:
			login_url = users.create_login_url('/login')
			template_values = {
				'login_url':login_url,
				'reg_url':'/register'
			}
			template = JINJA_ENVIRONMENT.get_template('/pages/login.html')
			self.response.write(template.render(template_values))

class APIHandler(webapp2.RequestHandler):
	def get(self):
		loggedin_user = users.get_current_user()
		if loggedin_user:
			user_key = ndb.Key('User', loggedin_user.user_id())
			user = user_key.get()
			if user:
				thesisdet = thesisentry.query().order(-thesisentry.Date).fetch()
				thesis_list = []
				for thesis in thesisdet:
					# user = User.query(User.key == thesis.THESIS_AUTHOR)
					e = []
					# for u in user:
					# 	e.append({
					# 		'first_name':u.first_name,
					# 		'last_name':u.last_name
					# 	})

					departmentlist = Department.query(Department.key == thesis.THESIS_DEPARTMENT)
					d = []
					for de in departmentlist:
						college = de.dept_college.get()
						university = college.college_univ.get()
						d.append({
							'name':de.dept_name,
							'college': college.college_name,
							'university': university.univ_name,
							'university_id':university.key.id()
							})

					facultylist = Faculty.query(Faculty.key == thesis.THESIS_ADVISER)
					f = []
					for fa in facultylist:
						f.append({
							'name':fa.faculty_full,
							'faculty_id':fa.key.id()
							})


					thesis_list.append({
						'id' : thesis.key.id(),
						'year': thesis.THESIS_YEAR,
						'title': thesis.THESIS_TITLE,
						'abstract': thesis.THESIS_ABSTRACT,
						'adviser': f,
						'section': thesis.THESIS_SECTION,
						'department': d,
						'thesis_id': thesis.key.id()
					})


				response = {
					'result' : 'OK',
					'thesis_data' : thesis_list
				}
				self.response.headers['Content-Type'] = 'application.json'
				self.response.out.write(json.dumps(response))

			else:
				self.redirect('/register')

		else:
			login_url = users.create_login_url('/login')
			template_values = {
				'login_url':login_url,
				'reg_url':'/register'
			}
			template = JINJA_ENVIRONMENT.get_template('/pages/login.html')
			self.response.write(template.render(template_values))		

	def post(self):
		thesis = thesisentry()
		user = User()
		faculty = Faculty()

		loggedin_user = users.get_current_user()
		user_key = ndb.Key('User', loggedin_user.user_id())

		PROPONENTs = []
		i = 0
		while self.request.get('PROPONENT_' + str(i)) is not None and self.request.get('PROPONENT_' + str(i)) != '':
			PROPONENT_temp = Student.query(Student.full_name == self.request.get('PROPONENT_' + str(i)))
			if PROPONENT_temp.count():
				PROPONENT_temp = PROPONENT_temp.get()
				PROPONENTs.append(PROPONENT_temp.key)
			else:
				PROPONENT_temp = Faculty.query(Faculty.faculty_full == self.request.get('PROPONENT_' + str(i)))
				if PROPONENT_temp.count():
					PROPONENT_temp = PROPONENT_temp.get()
					PROPONENTs.append(PROPONENT_temp.key)
				else:
					PROPONENTs.append(None)
			i += 1

		logging.info(PROPONENTs)

		THESIS_ADVISER_temp = Faculty.query(Faculty.faculty_full == self.request.get('THESIS_ADVISER'))
		THESIS_ADVISER_temp = THESIS_ADVISER_temp.get()
		THESIS_ADVISER_key = THESIS_ADVISER_temp.key

		THESIS_DEPARTMENT_temp = Department.query(Department.dept_name == self.request.get('THESIS_DEPARTMENT'))
		THESIS_DEPARTMENT_temp = THESIS_DEPARTMENT_temp.get()
		THESIS_DEPARTMENT_key = THESIS_DEPARTMENT_temp.key

		thesis.THESIS_AUTHOR = user_key
		thesis.THESIS_YEAR = self.request.get('THESIS_YEAR')
		thesis.THESIS_TITLE = self.request.get('THESIS_TITLE')
		thesis.THESIS_ABSTRACT = self.request.get('THESIS_ABSTRACT')
		thesis.THESIS_ADVISER = ndb.Key('Faculty', THESIS_ADVISER_key.id())
		thesis.THESIS_SECTION = self.request.get('THESIS_SECTION')
		thesis.PROPONENT = PROPONENTs
		thesis.THESIS_DEPARTMENT = ndb.Key('Department', THESIS_DEPARTMENT_key.id())

		tags = []

		for t in thesis.THESIS_TITLE.split():
			if len(t) >= 3 and t not in tags:
				tags.append(t)

		thesis.THESIS_RELATED = tags

		thesis.put()

		self.response.headers['Content-Type'] = 'application/json'
		response = {
			'result': 'OK',
			'data': {
				'id' : thesis.key.urlsafe(),
				'year': thesis.THESIS_YEAR,
				'title': thesis.THESIS_TITLE,
				'abstract': thesis.THESIS_ABSTRACT,
				'section': thesis.THESIS_SECTION,
				'author': user_key.get().first_name + ' ' + user_key.get().last_name
			}
		}
		self.response.out.write(json.dumps(response))

class LoginHandler(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user:
			user_key = ndb.Key('User', user.user_id())
			user_info = user_key.get()
			if user_info:
				self.redirect('/home')
			else:
				self.redirect('/register')

class RegistrationHandler(webapp2.RequestHandler):
	def get(self):
		loggedin_user = users.get_current_user()
		if loggedin_user:
			user_key = ndb.Key('User', loggedin_user.user_id())
			user = user_key.get()
			check = Faculty.query(Faculty.faculty_email == loggedin_user.email())
			check = check.get()
			logging.info(check)
			if check is not None:
				user = User(is_admin=True,first_name=check.faculty_fname,last_name=check.faculty_sname,email=check.faculty_email,id=loggedin_user.user_id())
				user.put()
				self.redirect('/home')
			if user:
				self.redirect('/home')
			else:
				template_data = {
					'email':loggedin_user.email()
				}
				template = JINJA_ENVIRONMENT.get_template('/pages/register.html')
				self.response.write(template.render(template_data))
		else:
			self.redirect(users.create_login_url('/register'))

	def post(self):
		user = User(id=users.get_current_user().user_id())
		user.phone_number = int(self.request.get('phone_number'))
		user.email = self.request.get('email')
		user.first_name = self.request.get('first_name')
		user.last_name = self.request.get('last_name')
		user.is_admin = False

		user.put()
		self.response.headers['Content-Type'] = 'application/json'
		response = {
			'result':'OK',
			'data':{
				'first_name':user.first_name,
				'last_name':user.last_name,
				'phone_number':user.phone_number,
				'id':users.get_current_user().user_id()
			}
		}
		self.response.out.write(json.dumps(response))

class ThesisPageHandler(webapp2.RequestHandler):
	def get(self):
		loggedin_user = users.get_current_user()
		if loggedin_user:
			user_key = ndb.Key('User', loggedin_user.user_id())
			user = user_key.get()
			if user:
				if user.is_admin:
					logout_url = users.create_logout_url('/')
					link_text = 'Logout'
					template_values = {
						'logout_url':logout_url,
						'user':user.first_name
					}
					template = JINJA_ENVIRONMENT.get_template('/pages/thesis.html')
					self.response.write(template.render(template_values))
				else:
					self.redirect('/home')

			else:
				self.redirect('/register')

		else:
			login_url = users.create_login_url('/login')
			template_values = {
				'login_url':login_url,
				'reg_url':'/register'
			}
			template = JINJA_ENVIRONMENT.get_template('/pages/login.html')
			self.response.write(template.render(template_values))

class FacultyHandler(webapp2.RequestHandler):
	def get(self):
		loggedin_user = users.get_current_user()
		if loggedin_user:
			user_key = ndb.Key('User', loggedin_user.user_id())
			user = user_key.get()
			if user:
				if user.is_admin:
					link_text = 'Logout'
					links = {}
					links['Faculty'] = {'List':'/faculty/list','Create Entry':'/faculty/create'}
					links['Students'] = {'List':'/student/list','Create Entry':'/student/create'}
					links['Department'] = {'List':'/department/list','Create Entry':'/department/create'}
					links['Universities'] = {'List':'/university/list','Create Entry':'/university/create'}
					links['Colleges'] = {'List':'/college/list','Create Entry':'/college/create'}
					links['Theses'] = {'List':'/thesis/list/all','Create Entry':'/thesis/create'}
					template_values = {
						'links':links,
						'search_url':'/search',
						'logout_url': users.create_logout_url('/'),
						'user': user.first_name
					}
					template = JINJA_ENVIRONMENT.get_template('/pages/faculty.html')
					self.response.write(template.render(template_values))
				else:
					self.redirect('/')
			else:
				self.redirect('/register')

		else:
			login_url = users.create_login_url('/login')
			template_values = {
				'login_url':login_url,
				'reg_url':'/register'
			}
			template = JINJA_ENVIRONMENT.get_template('/pages/login.html')
			self.response.write(template.render(template_values))

	def post(self):
		faculty = Faculty()

		faculty_department_temp = Department.query(Department.dept_name == self.request.get('faculty_department'))
		faculty_department_temp = faculty_department_temp.get()
		faculty_department_key = faculty_department_temp.key

		faculty.faculty_title = self.request.get('faculty_title')
		faculty.faculty_fname = self.request.get('faculty_fname')
		faculty.faculty_sname = self.request.get('faculty_sname')
		faculty_full = faculty.faculty_fname + ' ' + faculty.faculty_sname
		faculty.faculty_full = faculty_full
		faculty.faculty_email = self.request.get('faculty_email')
		faculty.faculty_phone = self.request.get('faculty_phone')
		faculty.faculty_department = ndb.Key('Department', faculty_department_key.id())
		faculty.faculty_bday = self.request.get('faculty_bday')
		faculty.key = ndb.Key(Faculty, faculty_full.strip().replace(' ', '').replace('.','').replace(',','').lower())
		faculty.put()

		self.response.headers['Content-Type'] = 'application/json'
		response = {
			'result':'OK',
			'data':{
				'title':faculty.faculty_title,
				'first_name':faculty.faculty_fname,
				'last_name':faculty.faculty_sname,
				'full_name':faculty.faculty_full,
				'email':faculty.faculty_email,
				'phone':faculty.faculty_phone,
				'bday':faculty.faculty_bday
			}
		}
		self.response.out.write(json.dumps(response))

class StudentHandler(webapp2.RequestHandler):
	def get(self):
		loggedin_user = users.get_current_user()
		if loggedin_user:
			user_key = ndb.Key('User', loggedin_user.user_id())
			user = user_key.get()
			if user:
				if user.is_admin:
					logout_url = users.create_logout_url('/')
					link_text = 'Logout'
					links = {}
					links['Faculty'] = {'List':'/faculty/list','Create Entry':'/faculty/create'}
					links['Students'] = {'List':'/student/list','Create Entry':'/student/create'}
					links['Department'] = {'List':'/department/list','Create Entry':'/department/create'}
					links['Universities'] = {'List':'/university/list','Create Entry':'/university/create'}
					links['Colleges'] = {'List':'/college/list','Create Entry':'/college/create'}
					links['Theses'] = {'List':'/thesis/list/all','Create Entry':'/thesis/create'}
					template_values = {
						'links':links,
						'logout_url':logout_url,
						'user':user.first_name
					}
					template = JINJA_ENVIRONMENT.get_template('/pages/student.html')
					self.response.write(template.render(template_values))
				else:
					self.redirect('/home')
			else:
				self.redirect('/register')

	def post(self):
		student = Student()

		student_dept_temp = Department.query(Department.dept_name == self.request.get('student_dept'))
		student_dept_temp = student_dept_temp.get()
		student_dept_key = student_dept_temp.key

		student.first_name = self.request.get('first_name')
		student.last_name = self.request.get('last_name')
		student.full_name = student.first_name + ' ' + student.last_name
		student.contact = self.request.get('contact')
		student.e_mail = self.request.get('e_mail')
		student.student_num = self.request.get('student_num')
		student.student_grad = int(self.request.get('student_grad'))
		student.student_dept = ndb.Key('Department', student_dept_key.id())
		student.b_day = self.request.get('b_day')

		portions = []
		for s in student.full_name.split():
			if len(s) > 1 and s not in portions:
				portions.append(s)
		student.student_name_portions = portions
		student.key = ndb.Key(Student, student.full_name.strip().replace(' ', '').replace('.','').replace(',','').lower())
		student.put()

		self.response.headers['Content-Type'] = 'application/json'
		response = {
			'result':'OK',
			'data':{
				'first_name':student.first_name,
				'last_name':student.last_name,
				'full_name':student.full_name,
				'phone':student.contact,
				'email':student.e_mail,
				'student_num':student.student_num,
				'year_graduated':student.student_grad
			}
		}
		self.response.out.write(json.dumps(response))

class UniversityHandler(webapp2.RequestHandler):
	def get(self):
		loggedin_user = users.get_current_user()
		if loggedin_user:
			user_key = ndb.Key('User', loggedin_user.user_id())
			user = user_key.get()
			if user:
				if user.is_admin:
					link_text = 'Logout'
					links = {}
					links['Faculty'] = {'List':'/faculty/list','Create Entry':'/faculty/create'}
					links['Students'] = {'List':'/student/list','Create Entry':'/student/create'}
					links['Department'] = {'List':'/department/list','Create Entry':'/department/create'}
					links['Universities'] = {'List':'/university/list','Create Entry':'/university/create'}
					links['Colleges'] = {'List':'/college/list','Create Entry':'/college/create'}
					links['Theses'] = {'List':'/thesis/list/all','Create Entry':'/thesis/create'}
					template_values = {
						'links':links,
						'search_url':'/search',
						'logout_url': users.create_logout_url('/'),
						'user': user.first_name
					}
					template = JINJA_ENVIRONMENT.get_template('/pages/university.html')
					self.response.write(template.render(template_values))
				else:
					self.redirect('/')
			else:
				self.redirect('/register')

	def post(self):
		university = University()

		university.univ_name = self.request.get('univ_name')
		university.univ_init = self.request.get('univ_init')
		university.univ_add = self.request.get('univ_add')
		university.key = ndb.Key(University, university.univ_init.strip().replace(' ', '').replace('.','').replace(',','').lower())
		university.put()

		self.response.headers['Content-Type'] = 'application/json'
		response = {
			'result':'OK',
			'data':{
				'univ_name': university.univ_name,
				'univ_init': university.univ_init,
				'univ_add': university.univ_add
			}
		}

		self.response.out.write(json.dumps(response))

class CollegeHandler(webapp2.RequestHandler):
	def get(self):
		loggedin_user = users.get_current_user()
		if loggedin_user:
			user_key = ndb.Key('User', loggedin_user.user_id())
			user = user_key.get()
			if user:
				if user.is_admin:
					link_text = 'Logout'
					links = {}
					links['Faculty'] = {'List':'/faculty/list','Create Entry':'/faculty/create'}
					links['Students'] = {'List':'/student/list','Create Entry':'/student/create'}
					links['Department'] = {'List':'/department/list','Create Entry':'/department/create'}
					links['Universities'] = {'List':'/university/list','Create Entry':'/university/create'}
					links['Colleges'] = {'List':'/college/list','Create Entry':'/college/create'}
					links['Theses'] = {'List':'/thesis/list/all','Create Entry':'/thesis/create'}
					template_values = {
						'links':links,
						'search_url':'/search',
						'logout_url': users.create_logout_url('/'),
						'user': user.first_name
					}
					template = JINJA_ENVIRONMENT.get_template('/pages/college.html')
					self.response.write(template.render(template_values))
				else:
					self.redirect('/')
			else:
				self.redirect('/register')

	def post(self):
		college = College()
		
		college_univ_temp = University.query(University.univ_name == self.request.get('college_univ'))
		college_univ_temp = college_univ_temp.get()
		college_univ_key = college_univ_temp.key

		college.college_univ = ndb.Key('University', college_univ_key.id())
		college.college_name = self.request.get('college_name')
		college.key = ndb.Key(College, college.college_name.strip().replace(' ', '').replace('.','').replace(',','').lower())
		college.put()

		self.response.headers['Content-Type'] = 'application/json'
		response = {
			'result':'OK',
			'data':{
				'college_name': college.college_name
			}
		}
		self.response.out.write(json.dumps(response))

class DepartmentHandler(webapp2.RequestHandler):
	def get(self):
		loggedin_user = users.get_current_user()
		if loggedin_user:
			user_key = ndb.Key('User', loggedin_user.user_id())
			user = user_key.get()
			if user:
				if user.is_admin:
					link_text = 'Logout'
					links = {}
					links['Faculty'] = {'List':'/faculty/list','Create Entry':'/faculty/create'}
					links['Students'] = {'List':'/student/list','Create Entry':'/student/create'}
					links['Department'] = {'List':'/department/list','Create Entry':'/department/create'}
					links['Universities'] = {'List':'/university/list','Create Entry':'/university/create'}
					links['Colleges'] = {'List':'/college/list','Create Entry':'/college/create'}
					links['Theses'] = {'List':'/thesis/list/all','Create Entry':'/thesis/create'}
					template_values = {
						'links':links,
						'search_url':'/search',
						'logout_url': users.create_logout_url('/'),
						'user': user.first_name
					}
					template = JINJA_ENVIRONMENT.get_template('/pages/department.html')
					self.response.write(template.render(template_values))
				else:
					self.redirect('/')
			else:
				self.redirect('/register')

	def post(self):
		department = Department()

		dept_college_temp = College.query(College.college_name == self.request.get('dept_college'))
		dept_college_temp = dept_college_temp.get()
		dept_college_key = dept_college_temp.key

		dept_chair_temp = Faculty.query(Faculty.faculty_full == self.request.get('dept_chair'))
		dept_chair_temp = dept_chair_temp.get()
		dept_chair_key = dept_chair_temp.key
		
		department.dept_college = ndb.Key('College', dept_college_key.id())
		department.dept_name = self.request.get('dept_name')
		department.dept_chair = ndb.Key('Faculty', dept_chair_key.id())

		department.key = ndb.Key(Department, department.dept_name.strip().replace(' ', '').replace('.','').replace(',','').lower())
		department.put()

		college = College.query(College.key == department.dept_college)
		c = college.get()
		logging.info(c)
		collegelist = []
		collegelist = c.college_depts
		logging.info(collegelist)
		collegelist.append(department.key)
		c.college_depts = collegelist
		c.put()

		self.response.headers['Content-Type'] = 'application/json'
		response = {
			'result':'OK',
			'data':{
				'dept_name': department.dept_name
			}
		}
		self.response.out.write(json.dumps(response))

class DataImportHandler(webapp2.RequestHandler):
	def get(self):
		script_path = os.path.abspath(__file__) # i.e. /path/to/dir/foobar.py
		script_dir = os.path.split(script_path)[0] #i.e. /path/to/dir/
		rel_path = "data/data.csv"
		abs_file_path = os.path.join(script_dir, rel_path)
		filepath = open(abs_file_path)
		file = csv.reader(filepath)
		j = 0
		for f in file:
			thesis = thesisentry()
			thesis.THESIS_YEAR = f[3]
			thesis.THESIS_TITLE = f[4]
			thesis.THESIS_ABSTRACT = f[5]
			thesis.THESIS_SECTION = f[6]

			dept_name = f[2]
			THESIS_DEPARTMENT = Department.get_by_name(dept_name)
			if THESIS_DEPARTMENT is None:
				THESIS_DEPARTMENT = Department(key=ndb.Key(Department, dept_name.strip().replace(' ', '').replace('.','').replace(',','').lower()), dept_name=dept_name)
				THESIS_DEPARTMENT.put()
			thesis.THESIS_DEPARTMENT = THESIS_DEPARTMENT.key

			if len(f[7]) == 0:
				f[7] = 'is empty'
			adviser_keyname = f[7].strip().replace(' ', '').replace('.','').replace(',','').lower()
			adviser_name = f[7]
			THESIS_ADVISER = Faculty.get_by_keyname(adviser_keyname)

			if THESIS_ADVISER is None:
				name = f[7].split()
				logging.info(name)
				THESIS_ADVISER = Faculty(key=ndb.Key(Faculty, adviser_keyname), faculty_full=f[7], faculty_department=thesis.THESIS_DEPARTMENT, faculty_fname=name[0], faculty_sname=name[1])
				THESIS_ADVISER.put()
			thesis.THESIS_ADVISER = THESIS_ADVISER.key
				
			proponent = []
			for i in range(8, 12):
				if len(f[i]) is not 0:
					proponent.append(f[i])
			proponent_list = []
			for p in proponent:
				PROPONENT = Student.get_by_name(p)
				if PROPONENT is None:
					portions = []
					for s in p.split():
						if len(s) > 1 and s not in portions:
							portions.append(s.lower())
					PROPONENT = Student(key=ndb.Key(Student, p.strip().replace(' ','').replace('.','').replace(',','').lower()), full_name=p, student_name_portions=portions)
					PROPONENT.put()
				proponent_list.append(PROPONENT.key)
			thesis.PROPONENT = proponent_list

			tags = []
			for t in thesis.THESIS_TITLE.split():
				if len(t) >= 3 and t not in tags:
					tags.append(t.lower())
				thesis.THESIS_RELATED = tags
			thesis.put()
			j += 1
			logging.info(j)
		filepath.close()
		self.redirect('/')

class SetupHandler(webapp2.RequestHandler):
	def get(self):
		fname = 'Pedrito '
		sname = 'Tenerife,Jr.'
		title = 'Engr. '
		fullname = (fname + sname).strip().replace(' ','').replace('.','').replace(',','').lower()
		chairperson = Faculty(key=ndb.Key(Faculty, fullname), faculty_fname=fname, faculty_sname=sname, faculty_title=title, faculty_full=title + fname + sname, faculty_email='bert.chd@gmail.com')
		chairperson.put()
		logging.info(chairperson.key.id())

		f = 'Gino '
		s = 'Tria'
		title = 'Engr. '
		fullname = (f + s).strip().replace(' ','').replace('.','').replace(',','').lower()
		faculty = Faculty(key=ndb.Key(Faculty, fullname), faculty_fname=f, faculty_sname=s, faculty_title=title, faculty_full=title + f + s, faculty_email='gino_tr14@gmail.com')
		faculty.put()
		logging.info(faculty.key.id())

		university = University(key=ndb.Key(University, 'pup'), univ_name='Polytechnic University of the Philippines',univ_add='Sta. Mesa, Manila',univ_init='PUP')
		university.put()

		college = College(key=ndb.Key(College, 'engineering'), college_name='Engineering', college_univ=university.key)
		college.put()

		department = Department(key=ndb.Key(Department, 'coe'), dept_name='COE', dept_college=college.key, dept_chair=chairperson.key)
		department.put()

		dept = []
		dept.append(department.key)
		college.college_depts = dept
		college.put()

		chairperson.faculty_department = department.key
		chairperson.put()
		faculty.faculty_department = department.key
		faculty.put()
		self.redirect('/data/import')

class FacultyListHandler(webapp2.RequestHandler):
	def get(self):
		loggedin_user = users.get_current_user()
		if loggedin_user:
			user_key = ndb.Key('User', loggedin_user.user_id())
			user = user_key.get()
			if user:
				if user.is_admin:
					link_text = 'Logout'
					links = {}
					links['Faculty'] = {'List':'/faculty/list','Create Entry':'/faculty/create'}
					links['Students'] = {'List':'/student/list','Create Entry':'/student/create'}
					links['Department'] = {'List':'/department/list','Create Entry':'/department/create'}
					links['Universities'] = {'List':'/university/list','Create Entry':'/university/create'}
					links['Colleges'] = {'List':'/college/list','Create Entry':'/college/create'}
					links['Theses'] = {'List':'/thesis/list/all','Create Entry':'/thesis/create'}
					template_values = {
						'links':links,
						'search_url':'/search',
						'logout_url': users.create_logout_url('/'),
						'user': user.first_name
					}
					template = JINJA_ENVIRONMENT.get_template('/pages/facultylist.html')
					self.response.write(template.render(template_values))
				else:
					link_text = 'Logout'
					links = {}
					links['Faculty'] = {'List':'/faculty/list'}
					links['Students'] = {'List':'/student/list'}
					links['Universities'] = {'List':'/university/list'}
					links['Colleges'] = {'List':'/college/list'}
					links['Departments'] = {'List':'/department/list'}
					links['Theses'] = {'List':'/thesis/list/all'}
					template_values = {
						'links':links,
						'search_url':'/search',
						'logout_url': users.create_logout_url('/'),
						'user': user.first_name
					}
					template = JINJA_ENVIRONMENT.get_template('/pages/facultylist.html')
					self.response.write(template.render(template_values))


			else:
				self.redirect('/register')
		else:
			login_url = users.create_login_url('/login')
			template_values = {
				'login_url':login_url,
				'reg_url':'/register'
			}
			template = JINJA_ENVIRONMENT.get_template('/pages/login.html')
			self.response.write(template.render(template_values))

	def post(self):
		faculty = Faculty()

		faculty_department_temp = Department.query(Department.dept_name == self.request.get('faculty_department'))
		faculty_department_temp = faculty_department_temp.get()
		faculty_department_key = faculty_department_temp.key

		faculty.faculty_title = self.request.get('faculty_title')
		faculty.faculty_fname = self.request.get('faculty_fname')
		faculty.faculty_sname = self.request.get('faculty_sname')
		faculty_full = faculty.faculty_fname + ' ' + faculty.faculty_sname
		faculty.faculty_full = faculty_full
		faculty.faculty_email = self.request.get('faculty_email')
		faculty.faculty_phone = self.request.get('faculty_phone')
		faculty.faculty_department = ndb.Key('Department', faculty_department_key.id())
		faculty.faculty_bday = self.request.get('faculty_bday')
		faculty.key = ndb.Key(Faculty, faculty_full.strip().replace(' ', '').replace('.','').replace(',','').lower())
		faculty.put()

		self.response.headers['Content-Type'] = 'application/json'
		response = {
			'result':'OK',
			'data':{
				'title':faculty.faculty_title,
				'first_name':faculty.faculty_fname,
				'last_name':faculty.faculty_sname,
				'full_name':faculty.faculty_full,
				'email':faculty.faculty_email,
				'phone':faculty.faculty_phone,
				'bday':faculty.faculty_bday
			}
		}
		self.response.out.write(json.dumps(response))

class FacultyAPIHandler(webapp2.RequestHandler):
	def get(self):
		loggedin_user = users.get_current_user()
		if loggedin_user:
			user_key = ndb.Key('User', loggedin_user.user_id())
			user = user_key.get()
			if user:
				facultylist = Faculty.query().order(Faculty.date_created).fetch()
				logging.info(facultylist)
				for f in facultylist:
					department = Department.query(Department.key == f.faculty_department)
					department = department.get()
				faculty = []
				for f in facultylist:
					faculty.append({
						'id':f.key.id(),
						'title':f.faculty_title,
						'first_name':f.faculty_fname,
						'last_name':f.faculty_sname,
						'full_name':f.faculty_full,
						'email':f.faculty_email,
						'phone':f.faculty_phone,
						'department':department.dept_name
						})
				response = {
					'result' : 'OK',
					'faculty_data': faculty
				}
				self.response.headers['Content-Type'] = 'application.json'
				self.response.out.write(json.dumps(response))
	
class ThesisCreateAPI(webapp2.RequestHandler):
	def get(self):
		loggedin_user = users.get_current_user()
		if loggedin_user:
			user_key = ndb.Key('User', loggedin_user.user_id())
			user = user_key.get()
			if user:
				facultylist = Faculty.query().order(Faculty.date_created).fetch()
				faculty = []
				for f in facultylist:
					faculty.append({
						'title':f.faculty_title,
						'first_name':f.faculty_fname,
						'last_name':f.faculty_sname,
						'full_name':f.faculty_full,
						'email':f.faculty_email,
						'phone':f.faculty_phone
						})

				studentlist = Student.query().order(Student.date_created).fetch()
				student = []
				for s in studentlist:
					student.append({
						'first_name':s.first_name,
						'last_name':s.last_name,
						'full_name':s.full_name,
						'phone':s.contact,
						'email':s.e_mail,
						'student_num':s.student_num,
						'year_graduated':s.student_grad
						})

				departmentlist = Department.query().order(Department.date_created).fetch()
				department = []
				for d in departmentlist:
					col = College.query(College.key == d.dept_college)
					c = []
					for co in col:
						c.append({
							'name':co.college_name
							})
					department.append({
						'college':c,
						'name':d.dept_name
						})	

				response = {
					'result' : 'OK',
					'faculty_data': faculty,
					'student_data': student,
					'department_data':department
				}
				self.response.headers['Content-Type'] = 'application.json'
				self.response.out.write(json.dumps(response))

class StudentsAPIHandler(webapp2.RequestHandler):
	def get(self):
		loggedin_user = users.get_current_user()
		if loggedin_user:
			user_key = ndb.Key('User', loggedin_user.user_id())
			user = user_key.get()
			if user:
				studentlist = Student.query().order(Student.date_created).fetch()
				student = []
				for s in studentlist:
					student.append({
						'id': s.key.id(),
						'first_name':s.first_name,
						'last_name':s.last_name,
						'full_name':s.full_name,
						'phone':s.contact,
						'email':s.e_mail,
						'student_num':s.student_num,
						'year_graduated':s.student_grad,
						'birthday':s.b_day
						})
				response = {
					'result' : 'OK',
					'data': student
				}
				self.response.headers['Content-Type'] = 'application.json'
				self.response.out.write(json.dumps(response))

class StudentListHandler(webapp2.RequestHandler):
	def get(self):
		loggedin_user = users.get_current_user()
		if loggedin_user:
			user_key = ndb.Key('User', loggedin_user.user_id())
			user = user_key.get()
			if user:
				if user.is_admin:
					link_text = 'Logout'
					links = {}
					links['Faculty'] = {'List':'/faculty/list','Create Entry':'/faculty/create'}
					links['Students'] = {'List':'/student/list','Create Entry':'/student/create'}
					links['Department'] = {'List':'/department/list','Create Entry':'/department/create'}
					links['Universities'] = {'List':'/university/list','Create Entry':'/university/create'}
					links['Colleges'] = {'List':'/college/list','Create Entry':'/college/create'}
					links['Theses'] = {'List':'/thesis/list/all','Create Entry':'/thesis/create'}
					template_values = {
						'links':links,
						'search_url':'/search',
						'logout_url': users.create_logout_url('/'),
						'user': user.first_name
					}
					template = JINJA_ENVIRONMENT.get_template('/pages/studentlist.html')
					self.response.write(template.render(template_values))
				else:
					link_text = 'Logout'
					links = {}
					links['Faculty'] = {'List':'/faculty/list'}
					links['Students'] = {'List':'/student/list'}
					links['Universities'] = {'List':'/university/list'}
					links['Colleges'] = {'List':'/college/list'}
					links['Departments'] = {'List':'/department/list'}
					links['Theses'] = {'List':'/thesis/list/all'}
					template_values = {
						'links':links,
						'search_url':'/search',
						'logout_url': users.create_logout_url('/'),
						'user': user.first_name
					}
					template = JINJA_ENVIRONMENT.get_template('/pages/studentlist.html')
					self.response.write(template.render(template_values))

			else:
				self.redirect('/register')
		else:
			login_url = users.create_login_url('/login')
			template_values = {
				'login_url':login_url,
				'reg_url':'/register'
			}
			template = JINJA_ENVIRONMENT.get_template('/pages/login.html')
			self.response.write(template.render(template_values))

class UniversityAPIHandler(webapp2.RequestHandler):
	def get(self):
		loggedin_user = users.get_current_user()
		if loggedin_user:
			user_key = ndb.Key('User', loggedin_user.user_id())
			user = user_key.get()
			if user:
				universitylist = University.query().order(University.date_created).fetch()
				university = []
				for u in universitylist:
					university.append({
						'id': u.key.id(),
						'univ_name': u.univ_name,
						'univ_init': u.univ_init,
						'univ_add': u.univ_add

						})
				response = {
					'result' : 'OK',
					'data': university
				}
				self.response.headers['Content-Type'] = 'application.json'
				self.response.out.write(json.dumps(response))

class UniversityListHandler(webapp2.RequestHandler):
	def get(self):
		loggedin_user = users.get_current_user()
		if loggedin_user:
			user_key = ndb.Key('User', loggedin_user.user_id())
			user = user_key.get()
			if user:
				if user.is_admin:
					link_text = 'Logout'
					links = {}
					links['Faculty'] = {'List':'/faculty/list','Create Entry':'/faculty/create'}
					links['Students'] = {'List':'/student/list','Create Entry':'/student/create'}
					links['Department'] = {'List':'/department/list','Create Entry':'/department/create'}
					links['Universities'] = {'List':'/university/list','Create Entry':'/university/create'}
					links['Colleges'] = {'List':'/college/list','Create Entry':'/college/create'}
					links['Theses'] = {'List':'/thesis/list/all','Create Entry':'/thesis/create'}
					template_values = {
						'links':links,
						'search_url':'/search',
						'logout_url': users.create_logout_url('/'),
						'user': user.first_name
					}
					template = JINJA_ENVIRONMENT.get_template('/pages/universitylist.html')
					self.response.write(template.render(template_values))
				else:
					link_text = 'Logout'
					links = {}
					links['Faculty'] = {'List':'/faculty/list'}
					links['Students'] = {'List':'/student/list'}
					links['Universities'] = {'List':'/university/list'}
					links['Colleges'] = {'List':'/college/list'}
					links['Departments'] = {'List':'/department/list'}
					links['Theses'] = {'List':'/thesis/list/all'}
					template_values = {
						'links':links,
						'search_url':'/search',
						'logout_url': users.create_logout_url('/'),
						'user': user.first_name
					}
					template = JINJA_ENVIRONMENT.get_template('/pages/universitylist.html')
					self.response.write(template.render(template_values))

			else:
				self.redirect('/register')
		else:
			login_url = users.create_login_url('/login')
			template_values = {
				'login_url':login_url,
				'reg_url':'/register'
			}
			template = JINJA_ENVIRONMENT.get_template('/pages/login.html')
			self.response.write(template.render(template_values))

class CollegeAPIHandler(webapp2.RequestHandler):
	def get(self):
		loggedin_user = users.get_current_user()
		if loggedin_user:
			user_key = ndb.Key('User', loggedin_user.user_id())
			user = user_key.get()
			if user:
				collegelist = College.query().order(College.date_created).fetch()
				college = []
				for c in collegelist:
					un = University.query(University.key == c.college_univ)
					un = un.get()

					college.append({
						'id' : c.key.id(),
						'college_name': c.college_name,
						'college_univ': un.univ_name
						})
				response = {
					'result' : 'OK',
					'data': college
				}
				self.response.headers['Content-Type'] = 'application.json'
				self.response.out.write(json.dumps(response))

class CollegeListHandler(webapp2.RequestHandler):
	def get(self):
		loggedin_user = users.get_current_user()
		if loggedin_user:
			user_key = ndb.Key('User', loggedin_user.user_id())
			user = user_key.get()
			if user:
				if user.is_admin:
					link_text = 'Logout'
					links = {}
					links['Faculty'] = {'List':'/faculty/list','Create Entry':'/faculty/create'}
					links['Students'] = {'List':'/student/list','Create Entry':'/student/create'}
					links['Department'] = {'List':'/department/list','Create Entry':'/department/create'}
					links['Universities'] = {'List':'/university/list','Create Entry':'/university/create'}
					links['Colleges'] = {'List':'/college/list','Create Entry':'/college/create'}
					links['Theses'] = {'List':'/thesis/list/all','Create Entry':'/thesis/create'}
					template_values = {
						'links':links,
						'search_url':'/search',
						'logout_url': users.create_logout_url('/'),
						'user': user.first_name
					}
					template = JINJA_ENVIRONMENT.get_template('/pages/collegelist.html')
					self.response.write(template.render(template_values))
				else:
					link_text = 'Logout'
					links = {}
					links['Faculty'] = {'List':'/faculty/list'}
					links['Students'] = {'List':'/student/list'}
					links['Universities'] = {'List':'/university/list'}
					links['Colleges'] = {'List':'/college/list'}
					links['Departments'] = {'List':'/department/list'}
					links['Theses'] = {'List':'/thesis/list/all'}
					template_values = {
						'links':links,
						'search_url':'/search',
						'logout_url': users.create_logout_url('/'),
						'user': user.first_name
					}
					template = JINJA_ENVIRONMENT.get_template('/pages/collegelist.html')
					self.response.write(template.render(template_values))
			else:
				self.redirect('/register')
		else:
			login_url = users.create_login_url('/login')
			template_values = {
				'login_url':login_url,
				'reg_url':'/register'
			}
			template = JINJA_ENVIRONMENT.get_template('/pages/login.html')
			self.response.write(template.render(template_values))

class DepartmentAPIHandler(webapp2.RequestHandler):
	def get(self):
		loggedin_user = users.get_current_user()
		if loggedin_user:
			user_key = ndb.Key('User', loggedin_user.user_id())
			user = user_key.get()
			if user:
				departmentlist = Department.query().order(Department.date_created).fetch()
				dept = []
				for d in departmentlist:
					c = College.query(College.key == d.dept_college)
					c = c.get()
					logging.info(c)
					u = University.query(University.key == c.college_univ)
					u = u.get()

					f = Faculty.query(Faculty.key == d.dept_chair)
					f = f.get()

					dept.append({
						'id':d.key.id(),
						'department_university':u.univ_name,
						'dept_name': d.dept_name,
						'dept_college': c.college_name,
						'dept_chair': f.faculty_full
						})
				response = {
					'result' : 'OK',
					'data': dept
				}
				self.response.headers['Content-Type'] = 'application.json'
				self.response.out.write(json.dumps(response))

class DepartmentListHandler(webapp2.RequestHandler):
	def get(self):
		loggedin_user = users.get_current_user()
		if loggedin_user:
			user_key = ndb.Key('User', loggedin_user.user_id())
			user = user_key.get()
			if user:
				if user.is_admin:
					link_text = 'Logout'
					links = {}
					links['Faculty'] = {'List':'/faculty/list','Create Entry':'/faculty/create'}
					links['Students'] = {'List':'/student/list','Create Entry':'/student/create'}
					links['Department'] = {'List':'/department/list','Create Entry':'/department/create'}
					links['Universities'] = {'List':'/university/list','Create Entry':'/university/create'}
					links['Colleges'] = {'List':'/college/list','Create Entry':'/college/create'}
					links['Theses'] = {'List':'/thesis/list/all','Create Entry':'/thesis/create'}
					template_values = {
						'links':links,
						'search_url':'/search',
						'logout_url': users.create_logout_url('/'),
						'user': user.first_name
					}
					template = JINJA_ENVIRONMENT.get_template('/pages/departmentlist.html')
					self.response.write(template.render(template_values))
				else:
					link_text = 'Logout'
					links = {}
					links['Faculty'] = {'List':'/faculty/list'}
					links['Students'] = {'List':'/student/list'}
					links['Universities'] = {'List':'/university/list'}
					links['Colleges'] = {'List':'/college/list'}
					links['Departments'] = {'List':'/department/list'}
					links['Theses'] = {'List':'/thesis/list/all'}
					template_values = {
						'links':links,
						'search_url':'/search',
						'logout_url': users.create_logout_url('/'),
						'user': user.first_name
					}
					template = JINJA_ENVIRONMENT.get_template('/pages/departmentlist.html')
					self.response.write(template.render(template_values))
			else:
				self.redirect('/register')
		else:
			login_url = users.create_login_url('/login')
			template_values = {
				'login_url':login_url,
				'reg_url':'/register'
			}
			template = JINJA_ENVIRONMENT.get_template('/pages/login.html')
			self.response.write(template.render(template_values))

class FacultyDeleteHandler(webapp2.RequestHandler):
	def post(self, id):
		faculty = Faculty.get_by_id(id)
		faculty.key.delete()
		self.response.headers['Content-Type'] = 'application/json'
		response = {
			'result':'OK'
		}
		self.response.out.write(json.dumps(response))

class FacultyEditHandler(webapp2.RequestHandler):
	def get(self, id):
		loggedin_user = users.get_current_user()
		if loggedin_user:
			user_key = ndb.Key('User', loggedin_user.user_id())
			user = user_key.get()
			if user:
				if user.is_admin:
					logout_url = users.create_logout_url('/')
					link_text = 'Logout'
					faculty = Faculty.get_by_id(id)
					department = None
					if faculty.faculty_department is not None:
						department = Department.query(Department.key == faculty.faculty_department)
						department = department.get()
						department = department.dept_name

					links = {}
					links['Faculty'] = {'List':'/faculty/list','Create Entry':'/faculty/create'}
					links['Students'] = {'List':'/student/list','Create Entry':'/student/create'}
					links['Department'] = {'List':'/department/list','Create Entry':'/department/create'}
					links['Universities'] = {'List':'/university/list','Create Entry':'/university/create'}
					links['Colleges'] = {'List':'/college/list','Create Entry':'/college/create'}
					links['Theses'] = {'List':'/thesis/list/all','Create Entry':'/thesis/create'}
					data = {
						'links':links,
						'item' : faculty,
						'dept' : department,
						'logout_url':logout_url,
						'user':user.first_name
					}
					template = JINJA_ENVIRONMENT.get_template('/pages/facultyedit.html')
					self.response.write(template.render(data))
				else:
					self.redirect('/')

			else:
				self.redirect('/register')
		else:
			login_url = users.create_login_url('/login')
			template_values = {
				'login_url':login_url,
				'reg_url':'/register'
			}
			template = JINJA_ENVIRONMENT.get_template('/pages/login.html')
			self.response.write(template.render(template_values))

	def post(self, id):
		faculty = Faculty()

		faculty_department_temp = Department.query(Department.dept_name == self.request.get('faculty_department'))
		faculty_department_temp = faculty_department_temp.get()
		faculty_department_key = faculty_department_temp.key

		faculty.faculty_title = self.request.get('faculty_title')
		faculty.faculty_fname = self.request.get('faculty_fname')
		faculty.faculty_sname = self.request.get('faculty_sname')
		faculty_full = faculty.faculty_fname + ' ' + faculty.faculty_sname
		faculty.faculty_full = faculty_full
		faculty.faculty_email = self.request.get('faculty_email')
		faculty.faculty_phone = self.request.get('faculty_phone')
		faculty.faculty_department = ndb.Key('Department', faculty_department_key.id())
		faculty.faculty_bday = self.request.get('faculty_bday')
		faculty.key = ndb.Key(Faculty, id)
		faculty.put()

		self.response.headers['Content-Type'] = 'application/json'
		response = {
			'result':'OK',
			'data':{
				'title':faculty.faculty_title,
				'first_name':faculty.faculty_fname,
				'last_name':faculty.faculty_sname,
				'full_name':faculty.faculty_full,
				'email':faculty.faculty_email,
				'phone':faculty.faculty_phone,
				'bday':faculty.faculty_bday
			}
		}
		self.response.out.write(json.dumps(response))

class StudentDeleteHandler(webapp2.RequestHandler):
	def post(self, id):
		student = Student.get_by_id(id)
		student.key.delete()
		self.response.headers['Content-Type'] = 'application/json'
		response = {
			'result':'OK'
		}
		self.response.out.write(json.dumps(response))

class StudentEdithandler(webapp2.RequestHandler):
	def get(self, id):
		loggedin_user = users.get_current_user()
		if loggedin_user:
			user_key = ndb.Key('User', loggedin_user.user_id())
			user = user_key.get()
			if user:
				if user.is_admin:
					logout_url = users.create_logout_url('/')
					link_text = 'Logout'
					student = Student.get_by_id(id)
					department = None

					if student.student_dept is not None:
						department = Department.query(Department.key == student.student_dept)
						department = department.get()
						department = department.dept_name
					data = {
						'item' : student,
						'id':id,
						'dept' : department,
						'logout_url':logout_url,
						'user':user.first_name
					}
					template = JINJA_ENVIRONMENT.get_template('/pages/studentedit.html')
					self.response.write(template.render(data))
				else:
					self.redirect('/')

			else:
				self.redirect('/register')
		else:
			login_url = users.create_login_url('/login')
			template_values = {
				'login_url':login_url,
				'reg_url':'/register'
			}
			template = JINJA_ENVIRONMENT.get_template('/pages/login.html')
			self.response.write(template.render(template_values))

	def post(self, id):
		student = Student()

		student_dept_temp = Department.query(Department.dept_name == self.request.get('student_dept'))
		student_dept_temp = student_dept_temp.get()
		student_dept_key = student_dept_temp.key

		student.first_name = self.request.get('first_name')
		student.last_name = self.request.get('last_name')
		student.full_name = student.first_name + ' ' + student.last_name
		student.contact = self.request.get('contact')
		student.e_mail = self.request.get('e_mail')
		student.student_num = self.request.get('student_num')
		student.student_grad = int(self.request.get('student_grad'))
		student.student_dept = ndb.Key('Department', student_dept_key.id())
		student.b_day = self.request.get('b_day')
		student.key = ndb.Key(Student, id)
		student.put()

		self.response.headers['Content-Type'] = 'application/json'
		response = {
			'result':'OK',
			'data':{
				'first_name':student.first_name,
				'last_name':student.last_name,
				'full_name':student.full_name,
				'phone':student.contact,
				'email':student.e_mail,
				'student_num':student.student_num,
				'year_graduated':student.student_grad
			}
		}
		self.response.out.write(json.dumps(response))

class UniversityDeleteHandler(webapp2.RequestHandler):
	def post(self, id):
		university = University.get_by_id(id)
		university.key.delete()
		self.response.headers['Content-Type'] = 'application/json'
		response = {
			'result':'OK'
		}
		self.response.out.write(json.dumps(response))

class UniversityEditHandler(webapp2.RequestHandler):
	def get(self, id):
		loggedin_user = users.get_current_user()
		if loggedin_user:
			user_key = ndb.Key('User', loggedin_user.user_id())
			user = user_key.get()
			if user:
				if user.is_admin:
					logout_url = users.create_logout_url('/')
					link_text = 'Logout'
					university = University.get_by_id(id)

					links = {}
					links['Faculty'] = {'List':'/faculty/list','Create Entry':'/faculty/create'}
					links['Students'] = {'List':'/student/list','Create Entry':'/student/create'}
					links['Department'] = {'List':'/department/list','Create Entry':'/department/create'}
					links['Universities'] = {'List':'/university/list','Create Entry':'/university/create'}
					links['Colleges'] = {'List':'/college/list','Create Entry':'/college/create'}
					links['Theses'] = {'List':'/thesis/list/all','Create Entry':'/thesis/create'}
					template_values = {
						'links':links,
						'search_url':'/search',
						'logout_url': users.create_logout_url('/'),
						'user': user.first_name
					}


					data = {
						'links':links,
						'item' : university,
						'logout_url':logout_url,
						'user':user.first_name
					}
					template = JINJA_ENVIRONMENT.get_template('/pages/universityedit.html')
					self.response.write(template.render(data))
				else:
					self.redirect('/')

			else:
				self.redirect('/register')
		else:
			login_url = users.create_login_url('/login')
			template_values = {
				'login_url':login_url,
				'reg_url':'/register'
			}
			template = JINJA_ENVIRONMENT.get_template('/pages/login.html')
			self.response.write(template.render(template_values))

	def post(self, id):
		university = University()

		university.univ_name = self.request.get('univ_name')
		university.univ_init = self.request.get('univ_init')
		university.univ_add = self.request.get('univ_add')
		university.key = ndb.Key(University, id)
		university.put()

		self.response.headers['Content-Type'] = 'application/json'
		response = {
			'result':'OK',
			'data':{
				'univ_name': university.univ_name,
				'univ_init': university.univ_init,
				'univ_add': university.univ_add
			}
		}

		self.response.out.write(json.dumps(response))

class CollegeDeleteHandler(webapp2.RequestHandler):
	def post(self, id):
		college = College.get_by_id(id)
		college.key.delete()
		self.response.headers['Content-Type'] = 'application/json'
		response = {
			'result':'OK'
		}
		self.response.out.write(json.dumps(response))

class CollegeEditHandler(webapp2.RequestHandler):
	def get(self, id):
		loggedin_user = users.get_current_user()
		if loggedin_user:
			user_key = ndb.Key('User', loggedin_user.user_id())
			user = user_key.get()
			if user:
				if user.is_admin:
					logout_url = users.create_logout_url('/')
					link_text = 'Logout'
					college = College.get_by_id(id)

					depts = []
					for c in college.college_depts:
						department = Department.query(Department.key == c)
						logging.info(department)
						if department is not None:
							department = department.get()
							depts.append(department.dept_name)

					university = University.query(University.key == college.college_univ)
					university = university.get()

					links = {}
					links['Faculty'] = {'List':'/faculty/list','Create Entry':'/faculty/create'}
					links['Students'] = {'List':'/student/list','Create Entry':'/student/create'}
					links['Department'] = {'List':'/department/list','Create Entry':'/department/create'}
					links['Universities'] = {'List':'/university/list','Create Entry':'/university/create'}
					links['Colleges'] = {'List':'/college/list','Create Entry':'/college/create'}
					links['Theses'] = {'List':'/thesis/list/all','Create Entry':'/thesis/create'}
					template_values = {
						'links':links,
						'search_url':'/search',
						'logout_url': users.create_logout_url('/'),
						'user': user.first_name
					}


					data = {
						'links':links,
						'item' : college,
						'univ' : university.univ_name,
						'dept' : depts,
						'logout_url':logout_url,
						'user':user.first_name
					}

					for i in range(0, len(depts)):
						data['college_dept_' + str(i)] = depts[i]

					logging.info(data)

					template = JINJA_ENVIRONMENT.get_template('/pages/collegeedit.html')
					self.response.write(template.render(data))
				else:
					self.redirect('/')

			else:
				self.redirect('/register')
		else:
			login_url = users.create_login_url('/login')
			template_values = {
				'login_url':login_url,
				'reg_url':'/register'
			}
			template = JINJA_ENVIRONMENT.get_template('/pages/login.html')
			self.response.write(template.render(template_values))

	def post(self, id):
		college = College()
		
		college_univ_temp = University.query(University.univ_name == self.request.get('college_univ'))
		college_univ_temp = college_univ_temp.get()
		college_univ_key = college_univ_temp.key

		department = college.college_depts

		dept_temp = []
		i = 0
		if self.request.get('college_department_' + str(i)) is not None and self.request.get('college_department_' + str(i)) != '':
			while self.request.get('college_department_' + str(i)) is not None and self.request.get('college_department_' + str(i)) != '':
				college_dept_temp = Department.query(Department.dept_name == self.request.get('college_department_' + str(i)))
				college_dept_temp = college_dept_temp.get()
				if college_dept_temp.key not in department:
					department.append(college_dept_temp.key)
				i += 1
			college.college_depts = department
		else:
			college.college_depts = []

		college.college_univ = ndb.Key('University', college_univ_key.id())
		college.college_name = self.request.get('college_name')
		college.key = ndb.Key(College, id)
		college.put()

		self.response.headers['Content-Type'] = 'application/json'
		response = {
			'result':'OK',
			'data':{
				'college_name': college.college_name
			}
		}
		self.response.out.write(json.dumps(response))

class DepartmentDeleteHandler(webapp2.RequestHandler):
	def post(self, id):
		department = Department.get_by_id(id)
		dept = []
		dept.append(department.key)
		logging.info(dept)
		college = College.query(College.college_depts.IN(dept))
		college = college.get()
		logging.info(college)
		depts = []
		depts = college.college_depts
		depts.remove(department.key)
		college.college_depts = depts
		college.key = college.key
		college.put()
		department.key.delete()
		self.response.headers['Content-Type'] = 'application/json'
		response = {
			'result':'OK'
		}
		self.response.out.write(json.dumps(response))

class DepartmentEditHandler(webapp2.RequestHandler):
	def get(self, id):
		loggedin_user = users.get_current_user()
		if loggedin_user:
			user_key = ndb.Key('User', loggedin_user.user_id())
			user = user_key.get()
			if user:
				if user.is_admin:
					logout_url = users.create_logout_url('/')
					link_text = 'Logout'
					department = Department.get_by_id(id)

					if department.dept_college is not None:
						college = College.query(College.key == department.dept_college)
						college = college.get()
						college = college.college_name

					if department.dept_chair is not None:
						chairperson = Faculty.query(Faculty.key == department.dept_chair)
						chairperson = chairperson.get()
						chairperson = chairperson.faculty_full

					link_text = 'Logout'
					links = {}
					links['Faculty'] = {'List':'/faculty/list','Create Entry':'/faculty/create'}
					links['Students'] = {'List':'/student/list','Create Entry':'/student/create'}
					links['Department'] = {'List':'/department/list','Create Entry':'/department/create'}
					links['Universities'] = {'List':'/university/list','Create Entry':'/university/create'}
					links['Colleges'] = {'List':'/college/list','Create Entry':'/college/create'}
					links['Theses'] = {'List':'/thesis/list/all','Create Entry':'/thesis/create'}

					data = {
						'links':links,
						'item' : department,
						'college' : college,
						'chairperson':chairperson,
						'logout_url':logout_url,
						'user':user.first_name
					}

					logging.info(data)

					template = JINJA_ENVIRONMENT.get_template('/pages/departmentedit.html')
					self.response.write(template.render(data))
				else:
					self.redirect('/')

			else:
				self.redirect('/register')
		else:
			login_url = users.create_login_url('/login')
			template_values = {
				'login_url':login_url,
				'reg_url':'/register'
			}
			template = JINJA_ENVIRONMENT.get_template('/pages/login.html')
			self.response.write(template.render(template_values))

	def post(self, id):
		department = Department()

		dept_college_temp = College.query(College.college_name == self.request.get('dept_college'))
		dept_college_temp = dept_college_temp.get()
		dept_college_key = dept_college_temp.key

		dept_chair_temp = Faculty.query(Faculty.faculty_full == self.request.get('dept_chair'))
		dept_chair_temp = dept_chair_temp.get()
		dept_chair_key = dept_chair_temp.key
		
		department.dept_college = ndb.Key('College', dept_college_key.id())
		department.dept_name = self.request.get('dept_name')
		department.dept_chair = ndb.Key('Faculty', dept_chair_key.id())

		department.key = ndb.Key(Department, id)
		department.put()

		college = College.query(College.key == department.dept_college)
		c = college.get()
		logging.info(c)
		collegelist = []
		collegelist = c.college_depts
		logging.info(collegelist)
		collegelist.append(department.key)
		c.college_depts = collegelist
		c.put()

		self.response.headers['Content-Type'] = 'application/json'
		response = {
			'result':'OK',
			'data':{
				'dept_name': department.dept_name
			}
		}
		self.response.out.write(json.dumps(response))



class ThesisDeleteHandler(webapp2.RequestHandler):
	def post(self, id):
		thesis = thesisentry.get_by_id(int(id))
		thesis.key.delete()
		self.response.headers['Content-Type'] = 'application/json'
		response = {
			'result':'OK'
		}
		self.response.out.write(json.dumps(response))

class ThesisEditHandler(webapp2.RequestHandler):
	def get(self, id):
		loggedin_user = users.get_current_user()
		if loggedin_user:
			user_key = ndb.Key('User', loggedin_user.user_id())
			user = user_key.get()
			if user:
				if user.is_admin:
					logout_url = users.create_logout_url('/')
					link_text = 'Logout'

					thesis = thesisentry.get_by_id(int(id))
					adviser = Faculty.get_by_id(thesis.THESIS_ADVISER.id())
					adviser = adviser.faculty_full
					proponents = []

					for t in thesis.PROPONENT:
						p = Student.get_by_id(t.id())
						proponents.append(p.full_name)

					department = Department.get_by_id(thesis.THESIS_DEPARTMENT.id())
					department = department.dept_name

					template_values = {
						'id': id,
						'proponents':proponents,
						'adviser':adviser,
						'department':department,
						'thesis':thesis,
						'logout_url':logout_url,
						'user':user.first_name
					}
					template = JINJA_ENVIRONMENT.get_template('/pages/thesisedit.html')
					self.response.write(template.render(template_values))
				else:
					self.redirect('/')

			else:
				self.redirect('/register')
		else:
			login_url = users.create_login_url('/login')
			template_values = {
				'login_url':login_url,
				'reg_url':'/register'
			}
			template = JINJA_ENVIRONMENT.get_template('/pages/login.html')
			self.response.write(template.render(template_values))

	def post(self, id):
		thesis = thesisentry()
		user = User()
		faculty = Faculty()

		loggedin_user = users.get_current_user()
		user_key = ndb.Key('User', loggedin_user.user_id())

		PROPONENTs = []
		i = 0
		while self.request.get('PROPONENT_' + str(i)) is not None and self.request.get('PROPONENT_' + str(i)) != '':
			PROPONENT_temp = Student.query(Student.full_name == self.request.get('PROPONENT_' + str(i)))
			if PROPONENT_temp.count():
				PROPONENT_temp = PROPONENT_temp.get()
				PROPONENTs.append(PROPONENT_temp.key)
			else:
				PROPONENT_temp = Faculty.query(Faculty.faculty_full == self.request.get('PROPONENT_' + str(i)))
				if PROPONENT_temp.count():
					PROPONENT_temp = PROPONENT_temp.get()
					PROPONENTs.append(PROPONENT_temp.key)
				else:
					PROPONENTs.append(None)
			i += 1

		logging.info(PROPONENTs)

		THESIS_ADVISER_temp = Faculty.query(Faculty.faculty_full == self.request.get('THESIS_ADVISER'))
		THESIS_ADVISER_temp = THESIS_ADVISER_temp.get()
		THESIS_ADVISER_key = THESIS_ADVISER_temp.key

		THESIS_DEPARTMENT_temp = Department.query(Department.dept_name == self.request.get('THESIS_DEPARTMENT'))
		THESIS_DEPARTMENT_temp = THESIS_DEPARTMENT_temp.get()
		THESIS_DEPARTMENT_key = THESIS_DEPARTMENT_temp.key

		thesis.THESIS_AUTHOR = user_key
		thesis.THESIS_YEAR = self.request.get('THESIS_YEAR')
		thesis.THESIS_TITLE = self.request.get('THESIS_TITLE')
		thesis.THESIS_ABSTRACT = self.request.get('THESIS_ABSTRACT')
		thesis.THESIS_ADVISER = ndb.Key('Faculty', THESIS_ADVISER_key.id())
		thesis.THESIS_SECTION = self.request.get('THESIS_SECTION')
		thesis.PROPONENT = PROPONENTs
		thesis.THESIS_DEPARTMENT = ndb.Key('Department', THESIS_DEPARTMENT_key.id())
		thesis.key = ndb.Key(thesisentry, int(id))
		tags = []

		for t in thesis.THESIS_TITLE.split():
			if len(t) >= 3 and t not in tags:
				tags.append(t)

		thesis.THESIS_RELATED = tags

		thesis.put()

		self.response.headers['Content-Type'] = 'application/json'
		response = {
			'result': 'OK',
			'data': {
				'id' : thesis.key.urlsafe(),
				'year': thesis.THESIS_YEAR,
				'title': thesis.THESIS_TITLE,
				'abstract': thesis.THESIS_ABSTRACT,
				'section': thesis.THESIS_SECTION,
				'author': user_key.get() + ' ' + user_key.get().last_name
			}
		}
		self.response.out.write(json.dumps(response))

class ThesisListAll(webapp2.RequestHandler):
	def get(self):
		loggedin_user = users.get_current_user()
		if loggedin_user:
			user_key = ndb.Key('User', loggedin_user.user_id())
			user = user_key.get()
			if user:
				logout_url = users.create_logout_url('/')
				link_text = 'Logout'
				template_values = {
					'logout_url':logout_url,
					'user':user.first_name
				}
				template = JINJA_ENVIRONMENT.get_template('/pages/thesislist.html')
				self.response.write(template.render(template_values))

			else:
				self.redirect('/register')
		else:
			login_url = users.create_login_url('/login')
			template_values = {
				'login_url':login_url,
				'reg_url':'/register'
			}
			template = JINJA_ENVIRONMENT.get_template('/pages/login.html')
			self.response.write(template.render(template_values))

class ThesisListFilter(webapp2.RequestHandler):
	def get(self, value):
		loggedin_user = users.get_current_user()
		if loggedin_user:
			user_key = ndb.Key('User', loggedin_user.user_id())
			user = user_key.get()
			if user:

				logging.info(value)
				thesisdet = thesisentry.query(thesisentry.THESIS_YEAR == value).fetch()
				selected = value
				if len(thesisdet) == 0:
					faculty = Faculty.get_by_id(value)
					logging.info(faculty)
					if faculty is not None and len(thesisentry.query(thesisentry.THESIS_ADVISER == faculty.key).fetch()) != 0:
						thesisdet = thesisentry.query(thesisentry.THESIS_ADVISER == faculty.key).fetch()
						selected = faculty.faculty_full
					else:
						university = University.get_by_id(value)
						college = College.query(College.college_univ == university.key)
						college = college.get()
						department = Department.query(Department.dept_college == college.key)
						department = department.get()
						thesisdet = thesisentry.query(thesisentry.THESIS_DEPARTMENT == department.key).fetch()
						selected = university.univ_name

				logout_url = users.create_logout_url('/')
				link_text = 'Logout'
				template_values = {
					'thesis': thesisdet,
					'selected': selected,
					'logout_url':logout_url,
					'user':user.first_name
				}
				template = JINJA_ENVIRONMENT.get_template('/pages/thesislistfiltered.html')
				self.response.write(template.render(template_values))

			else:
				self.redirect('/register')
		else:
			login_url = users.create_login_url('/login')
			template_values = {
				'login_url':login_url,
				'reg_url':'/register'
			}
			template = JINJA_ENVIRONMENT.get_template('/pages/login.html')
			self.response.write(template.render(template_values))

class ThesisDetailsHandler(webapp2.RequestHandler):
	def get(self, id):
		loggedin_user = users.get_current_user()
		if loggedin_user:
			user_key = ndb.Key('User', loggedin_user.user_id())
			user = user_key.get()
			if user:
				if user.is_admin:
					logout_url = users.create_logout_url('/')
					link_text = 'Logout'

					thesis = thesisentry.get_by_id(int(id))
					adviser = Faculty.get_by_id(thesis.THESIS_ADVISER.id())
					adviser = adviser.faculty_full
					proponents = []

					for t in thesis.PROPONENT:
						p = Student.get_by_id(t.id())
						proponents.append(p.full_name)

					tags = thesis.THESIS_RELATED
					t = thesisentry.query(thesisentry.THESIS_RELATED.IN(tags)).fetch()
					edit_link = {}
					edit_link['Edit Thesis Entry'] = '/thesis/' + id + '/edit'
					template_values = {
						'edit_link':edit_link,
						'related':t,
						'proponents':proponents,
						'adviser':adviser,
						'thesis':thesis,
						'logout_url':logout_url,
						'user':user.first_name
					}
					template = JINJA_ENVIRONMENT.get_template('/pages/thesisdetail.html')
					self.response.write(template.render(template_values))
				else:
					logout_url = users.create_logout_url('/')
					link_text = 'Logout'

					thesis = thesisentry.get_by_id(int(id))
					adviser = Faculty.get_by_id(thesis.THESIS_ADVISER.id())
					adviser = adviser.faculty_full
					proponents = []

					for t in thesis.PROPONENT:
						p = Student.get_by_id(t.id())
						proponents.append(p.full_name)

					tags = thesis.THESIS_RELATED
					t = thesisentry.query(thesisentry.THESIS_RELATED.IN(tags)).fetch()
					edit_link = {}
					edit_link[''] = '#'
					template_values = {
						'edit_link':edit_link,
						'related':t,
						'proponents':proponents,
						'adviser':adviser,
						'thesis':thesis,
						'logout_url':logout_url,
						'user':user.first_name
					}
					template = JINJA_ENVIRONMENT.get_template('/pages/thesisdetail.html')
					self.response.write(template.render(template_values))

			else:
				self.redirect('/register')
		else:
			login_url = users.create_login_url('/login')
			template_values = {
				'login_url':login_url,
				'reg_url':'/register'
			}
			template = JINJA_ENVIRONMENT.get_template('/pages/login.html')
			self.response.write(template.render(template_values))

class SearchHandler(webapp2.RequestHandler):
	def get(self):
		loggedin_user = users.get_current_user()
		if loggedin_user:
			user_key = ndb.Key('User', loggedin_user.user_id())
			user = user_key.get()
			if user:
				if user.is_admin:
					link_text = 'Logout'
					links = {}
					links['Faculty'] = {'List':'/faculty/list','Create Entry':'/faculty/create'}
					links['Students'] = {'List':'/student/list','Create Entry':'/student/create'}
					links['Department'] = {'List':'/department/list','Create Entry':'/department/create'}
					links['Universities'] = {'List':'/university/list','Create Entry':'/university/create'}
					links['Colleges'] = {'List':'/college/list','Create Entry':'/college/create'}
					links['Theses'] = {'List':'/thesis/list/all','Create Entry':'/thesis/create'}
					template_values = {
						'links':links,
						'search_url':'/search',
						'logout_url': users.create_logout_url('/'),
						'user': user.first_name
					}
					template = JINJA_ENVIRONMENT.get_template('/pages/search.html')
					self.response.write(template.render(template_values))
				else:
					link_text = 'Logout'
					links = {}
					links['Faculty'] = {'List':'/faculty/list'}
					links['Students'] = {'List':'/student/list'}
					links['Universities'] = {'List':'/university/list'}
					links['Colleges'] = {'List':'/college/list'}
					links['Departments'] = {'List':'/department/list'}
					links['Theses'] = {'List':'/thesis/list/all'}
					template_values = {
						'links':links,
						'search_url':'/search',
						'logout_url': users.create_logout_url('/'),
						'user': user.first_name
					}
					template = JINJA_ENVIRONMENT.get_template('/pages/search.html')
					self.response.write(template.render(template_values))
			else:
				self.redirect('/register')
		else:
			login_url = users.create_login_url('/login')
			template_values = {
				'login_url':login_url,
				'reg_url':'/register'
			}
			template = JINJA_ENVIRONMENT.get_template('/pages/login.html')
			self.response.write(template.render(template_values))

	def post(self):
		keyword = []
		search_results = {}
		keyword = (self.request.get('search_keyword')).lower().split()
		logging.info(keyword)
		results = thesisentry.query(thesisentry.THESIS_RELATED.IN(keyword)).fetch()
		logging.info(len(results))
		if len(results) == 0:
			stud_res = Student.query(Student.student_name_portions.IN(keyword)).fetch()
			keys = []
			if len(stud_res) != 0:
				for s in stud_res:
					keys.append(s.key)
				results = thesisentry.query(thesisentry.PROPONENT.IN(keys)).fetch()
				for r in results:
					search_results[r.THESIS_TITLE] = r.key.id()
				self.response.headers['Content-Type'] = 'application.json'
				response = {
					'result':'OK',
					'data': search_results
				}
				self.response.out.write(json.dumps(response))
			else:
				self.response.headers['Content-Type'] = 'application.json'
				response = {
					'result':'OK'
				}
				self.response.out.write(json.dumps(response))
		else:
			for r in results:
				search_results[r.THESIS_TITLE] = r.key.id()
			self.response.headers['Content-Type'] = 'application.json'
			response = {
				'result':'OK',
				'data': search_results
			}
			self.response.out.write(json.dumps(response))

app = webapp2.WSGIApplication([
	('/api/thesis', APIHandler),
	('/register', RegistrationHandler),
	('/login', LoginHandler),
	('/home', MainPageHandler),
	('/thesis/create', ThesisPageHandler),
	('/faculty/create', FacultyHandler),
	('/student/create', StudentHandler),
	('/university/create', UniversityHandler),
	('/college/create', CollegeHandler),
	('/department/create', DepartmentHandler),
	('/data/import', DataImportHandler),
	('/setup', SetupHandler),
	('/faculty/list', FacultyListHandler),
	('/faculty/api', FacultyAPIHandler),
	('/thesis/create/api', ThesisCreateAPI),
	('/student/api', StudentsAPIHandler),
	('/student/list', StudentListHandler),
	('/university/api', UniversityAPIHandler),
	('/university/list', UniversityListHandler),
	('/college/api', CollegeAPIHandler),
	('/college/list', CollegeListHandler),
	('/department/api', DepartmentAPIHandler),
	('/department/list', DepartmentListHandler),
	('/faculty/(.*)/delete', FacultyDeleteHandler),
	('/faculty/(.*)', FacultyEditHandler),
	('/student/(.*)/delete', StudentDeleteHandler),
	('/student/(.*)', StudentEdithandler),
	('/university/(.*)/delete', UniversityDeleteHandler),
	('/university/(.*)', UniversityEditHandler),
	('/college/(.*)/delete', CollegeDeleteHandler),
	('/college/(.*)', CollegeEditHandler),
	('/department/(.*)/delete', DepartmentDeleteHandler),
	('/department/(.*)', DepartmentEditHandler),
	('/thesis/(.*)/delete', ThesisDeleteHandler),
	('/thesis/(.*)/edit', ThesisEditHandler),
	('/thesis/list/all', ThesisListAll),
	('/thesis/list/(.*)', ThesisListFilter),
	('/thesis/(.*)', ThesisDetailsHandler),
	('/search', SearchHandler),
	('/', MainPageHandler)
], debug=True)
