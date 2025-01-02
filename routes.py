from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, current_user, logout_user, login_required
from app import app, db, bcrypt
from models import User, Post
from forms import LoginForm, PostForm

@app.route('/')
def home():
    posts = Post.query.all()
    return render_template('home.html', posts=posts)

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
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
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
                         next_post=next_post)