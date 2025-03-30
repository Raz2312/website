from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from google.cloud.firestore_v1.base_query import FieldFilter

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Query Firestore for user by email
        user_query = db.collection('Users').where(filter=FieldFilter('email', '==', email)).stream()
        user_docs = list(user_query)  # Convert to a list
        if user_docs:  # Ensure we have at least one result
            user_data = user_docs[0].to_dict()  # Convert the first document to a dictionary
            user = User(
                id=user_docs[0].id,  # Firestore document ID
                user_name=user_data['user_name'],
                email=user_data['email'],
                password=user_data['password'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                Bio=user_data['Bio'],
                profile_pic=user_data['profile_pic']
            )
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('pages.index'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)


@auth.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


import uuid  

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        user_name = request.form.get('user_name')
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        last_name = request.form.get('LastName', "")
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        profilepic = request.files.get('profile_pic')

        email_query = db.collection('Users').where(filter=FieldFilter('email', '==', email)).get()
        username_query = db.collection('Users').where(filter=FieldFilter('user_name', '==', user_name)).get()

        if email_query:
            flash('Email already exists.', category='error')
        elif username_query:
            flash('User name is already in use.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 1:
            flash('First name must be greater than 1 character.', category='error')
        elif len(last_name) < 1:
            flash('Last name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            unique_id = str(uuid.uuid4())

            new_user = User(
                id=unique_id, 
                email=email,
                user_name=user_name,
                first_name=first_name,
                last_name=last_name,
                password=generate_password_hash(password1, method='pbkdf2:sha256'),
                Bio="", 
                profile_pic='avatar.jpg'
                
            )
            doc_ref = db.collection('Users').document(unique_id)  
            doc_ref.set(new_user.__dict__) 
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('pages.index'))

    return render_template("sign_up.html", user=current_user)

