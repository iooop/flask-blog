from flask import render_template,request
from app import app

@app.route('/')
def homepage():
#	o	return 'Home page'
	name = request.args.get('name')
	if not name:
		name = '<unknown>'
	return render_template('homepage.html',name=name)

