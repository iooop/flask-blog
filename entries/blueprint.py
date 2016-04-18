import os
from flask import Blueprint, flash, g, render_template, redirect, url_for, request
from helpers import object_list
from models import Entry, Tag
from forms import EntryForm, ImageForm, CommentForm
from flask.ext.login import login_required
from app import app, db
from werkzeug import secure_filename

entries = Blueprint('entries', __name__, template_folder='templates')


@entries.route('/')
def index():
	entries = Entry.query.order_by(Entry.created_timestamp.desc())
	return entry_list('entries/index.html', entries)

@entries.route('/tags/')
def tag_index():
	tags = Tag.query.order_by(Tag.name)
	return object_list('entries/tag_index.html', tags)

@entries.route('/tags/<slug>/')
def tag_detail(slug):
	tag = Tag.query.filter(Tag.slug == slug).first_or_404()
	entries = tag.entries.order_by(Entry.created_timestamp.desc())
	return object_list('entries/tag_detail.html', entries, tag=tag)

@entries.route('/create/', methods=['GET', 'POST'])
@login_required
def create():
	if request.method == 'POST':
		form = EntryForm(request.form)
		if form.validate():
			entry = form.save_entry(Entry(author=g.user))
			db.session.add(entry)
			db.session.commit()
			flash('Entry "%s" created successfully.' % entry.title, 'success')
			return redirect(url_for('entries.detail', slug=entry.slug))
	else:
		form = EntryForm()

	return render_template('entries/create.html', form=form)

@entries.route('/image-upload/', methods=['GET', 'POST'])
@login_required
def image_upload(): 
	if request.method == 'POST': 
		form = ImageForm(request.form) 
		if form.validate(): 
			image_file = request.files['file'] 
			filename = os.path.join(app.config['IMAGES_DIR'], 
									secure_filename(image_file.filename)) 
			image_file.save(filename) 
			flash('Saved %s' % os.path.basename(filename), 'success') 
			return redirect(url_for('entries.index')) 
	else: 
		form = ImageForm() 

	return render_template('entries/image_upload.html', form=form) 

@entries.route('/<slug>/') 
def detail(slug): 
	entry = get_entry_or_404(slug) 
	form = CommentForm(data={'entry_id': entry.id}) 
	return render_template('entries/detail.html', entry=entry, form=form) 

@entries.route('/<slug>/edit/', methods=['GET', 'POST']) 
@login_required
def edit(slug): 
	entry = get_entry_or_404(slug, author=None)
	if request.method == 'POST': 
		form = EntryForm(request.form, obj=entry) 
		if form.validate(): 
			entry = form.save_entry(entry) 
			db.session.add(entry) 
			db.session.commit() 
			flash('Entry "%s" has been saved.' % entry.title, 'success')
			return redirect(url_for('entries.detail', slug=entry.slug)) 
	else: 
		form = EntryForm(obj=entry) 

	return render_template('entries/edit.html', entry=entry, form=form) 

@entries.route('/<slug>/delete/', methods=['GET', 'POST']) 
@login_required
def delete(slug): 
	entry = get_entry_or_404(slug, author=None) 
	if request.method == 'POST': 
		entry.status = Entry.STATUS_DELETED 
		db.session.add(entry) 
		db.session.commit()
		flash('Entry "%s" has been deleted.' % entry.title, 'success')
		return redirect(url_for('entries.index')) 

	return render_template('entries/delete.html', entry=entry) 

	
def entry_list(template, query, **context):
	query = filter_status_by_user(query) 
	
	valid_statuses = (Entry.STATUS_PUBLIC, Entry.STATUS_DRAFT)
	query = query.filter(Entry.status.in_(valid_statuses))
	search = request.args.get('q')
	if search:
			query = query.filter(
								(Entry.body.contains(search)) |
								(Entry.title.contains(search)))
	return object_list(template, query, **context)

def get_entry_or_404(slug, author=None): 
	query = Entry.query.filter(Entry.slug == slug) 
	if author: 
		query = query.filter(Entry.author == author) 
	else: 
		query = filter_status_by_user(query) 
	return query.first_or_404() 

def filter_status_by_user(query): 
    if not g.user.is_authenticated: 
        query = query.filter(Entry.status == Entry.STATUS_PUBLIC) 
    else: 
        # Allow user to view their own drafts. 
        query = query.filter( 
            (Entry.status == Entry.STATUS_PUBLIC) | 
            ((Entry.author == g.user) & 
             (Entry.status != Entry.STATUS_DELETED))) 
    return query 

