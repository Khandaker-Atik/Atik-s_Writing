from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import login_user, current_user, logout_user, login_required
from app import app, db, bcrypt
from models import User, Post
from forms import LoginForm, PostForm
from datetime import datetime

# Define the last edited time
last_edited_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@app.route('/')
def home():
    posts = Post.query.all()
    return render_template('home.html', posts=posts, last_edited_time=last_edited_time)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        # Replace newlines with <br> tags before saving
        content = form.content.data.replace('\n', '<br>')
        post = Post(title=form.title.data, content=content, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('post.html', form=form)

@app.route('/post/delete/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        flash('You do not have permission to delete this post', 'danger')
        return redirect(url_for('home'))
    db.session.delete(post)
    db.session.commit()
    flash('The post has been deleted', 'success')
    return redirect(url_for('home'))

@app.route("/post/<int:post_id>")
def view_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    # Get total number of posts and current post number
    all_posts = Post.query.order_by(Post.date_posted.desc()).all()
    post_number = all_posts.index(post) + 1
    
    # Get previous and next posts
    prev_post = None
    next_post = None
    
    for i, p in enumerate(all_posts):
        if p.id == post_id:
            if i > 0:
                prev_post = all_posts[i-1]
            if i < len(all_posts)-1:
                next_post = all_posts[i+1]
            break
    
    return render_template('view_post.html', 
                         post=post, 
                         post_number=post_number,
                         prev_post=prev_post, 
                         next_post=next_post,
                         last_edited_time=last_edited_time)

@app.route('/post/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    # Check if the current user is the author of the post
    if post.author != current_user:
        flash('You do not have permission to edit this post', 'danger')
        return redirect(url_for('home'))
    
    form = PostForm()
    if form.validate_on_submit():
        # Update the existing post, replacing newlines with <br> tags
        post.title = form.title.data
        post.content = form.content.data.replace('\n', '<br>')
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('view_post', post_id=post.id))
    
    # Pre-populate the form with the current post data
    form.title.data = post.title
    form.content.data = post.content
    
    return render_template('post.html', form=form, post=post)
