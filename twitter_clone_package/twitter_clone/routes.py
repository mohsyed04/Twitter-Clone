import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from twitter_clone import app, db, bcrypt
from twitter_clone.forms import RegistrationForm, LoginForm, TweetForm
from twitter_clone.models import User, Tweet, Followers
from flask_login import login_user, current_user, logout_user, login_required

'''
SELECT tweet FROM Tweet WHERE uid
IN (SELECT following FROM Followers WHERE id=current_user.uid);
'''
@app.route("/")
@app.route("/home")
def home():
    if current_user.is_authenticated:
        following_list = [r[0] for r in Followers.query.filter_by(user_id=current_user.user_id).values('following')]
        tweets = db.session.query(Tweet).filter(Tweet.user_id.in_(following_list))
        return render_template('home.html', tweets = tweets, following_list=following_list)
    else:
        return redirect(url_for('register'))


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash('You need to logout first before creating a new account', 'danger')
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Thanks for registering', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Email and/or password is incorrect', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/tweet/<int:tweet_id>")
def tweet(tweet_id):
    tweet = Tweet.query.get_or_404(tweet_id)
    return render_template('tweet.html', tweet=tweet)

@app.route("/tweet/new", methods=['GET', 'POST'])
@login_required
def new_tweet():
    form = TweetForm()
    if form.validate_on_submit():
        tweet = Tweet(tweet=form.text.data, author=current_user)
        db.session.add(tweet)
        db.session.commit()
        flash('Tweeted!', 'success')
        return redirect(url_for('home'))
    return render_template('create_tweet.html', form=form, legend='New Tweet')


@app.route("/tweet/<int:tweet_id>/update", methods=['GET', 'POST'])
@login_required
def update_tweet(tweet_id):
    tweet = Tweet.query.get_or_404(tweet_id)
    if post.author != current_user:
        abort(403)
    form = TweetForm()
    if form.validate_on_submit():
        tweet.tweet = form.text.data #tweet.text makes more sense
        tweet.tweet = form.text.data
        db.session.commit()
        flash('Tweet updated!', 'success')
        return redirect(url_for('tweet', tweet_id=tweet.id))
    elif request.method == 'GET':
        form.text.data = tweet.tweet
    return render_template('create_tweet.html',
                           form=form, legend='Update Tweet')


@app.route("/tweet/<int:tweet_id>/delete", methods=['POST'])
@login_required
def delete_tweet(tweet_id):
    tweet = Tweet.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(tweet)
    db.session.commit()
    flash('Your tweet has been deleted!', 'success')
    return redirect(url_for('home'))


@app.route("/explore", methods=["GET", "POST"])
@login_required
def explore():
    persons = User.query.all()
    return render_template('explore.html', persons=persons)

@app.route("/profile/<int:profile_id>", methods=['GET', 'POST'])
@login_required
def profile(profile_id):
    delete = False
    tweets = Tweet.query.filter_by(user_id=profile_id)
    exists = bool(Followers.query.filter_by(user_id=current_user.user_id, following=profile_id).first())
    return render_template('profile.html', tweets=tweets, delete = delete, following=exists)

@app.route("/follow/<int:follow_id>", methods=['GET', 'POST'])
@login_required
def follow(follow_id):
    
    if(current_user.user_id != follow_id):
        exists = bool(Followers.query.filter_by(user_id=current_user.user_id, following=follow_id).first())
        if(exists == True):
            flash('followed!','success')
        else:
            record = Followers(user_id=current_user.user_id, following=follow_id)
            db.session.add(record)
            db.session.commit()
            flash('followed!','success')

        return redirect(url_for('profile', profile_id=follow_id, following=exists))
    
    else:
        flash('Action prohibited. Sign In from a different account and try again.', 'danger')
        return redirect(url_for('profile', profile_id=follow_id))


@app.route("/unfollow/<int:unfollow_id>", methods=['GET', 'POST'])
@login_required
def unfollow(unfollow_id):
    if(current_user.user_id != unfollow_id):
        Followers.query.filter_by(user_id=current_user.user_id, following=unfollow_id).delete()
        db.session.commit()
        flash('Stopped following!','success')

        return redirect(url_for('profile', profile_id=unfollow_id, following=False))
    
    else:
        flash('Action prohibited. Sign In from a different account and try again.', 'danger')
        return redirect(url_for('profile', profile_id=follow_id))


@app.route("/delete_account", methods=['GET', 'POST'])
@login_required
def delete_account():
    User.query.filter_by(user_id=current_user.user_id).delete()
    Tweet.query.filter_by(user_id=current_user.user_id).delete()
    db.session.commit()
    return redirect(url_for('register'))