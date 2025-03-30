from flask import Flask, request, flash, render_template, redirect, url_for , jsonify
from flask_login import LoginManager, login_user, login_required, current_user
import firebase_admin
from firebase_admin import credentials, firestore 
from ebaysdk.finding import Connection as Finding
from ebaysdk.exception import ConnectionError
import json
import os
import datetime
import sys
from datetime import datetime, timedelta
import googlemaps

# Replace with your actual API key
API_KEY = "AIzaSyAtcWj6Uog3a16LgoF9NeXe_A951igbzsc"

cred = credentials.Certificate(r"c:\Users\RAZ\Downloads\website-firebase-2f02a-firebase-adminsdk-1gcvh-31adc67afb.json")
firebase_admin.initialize_app(cred)
db = firestore.client()



class User:#מאיפיינים של משתמש
    def __init__(self, id, user_name, email, password, first_name, last_name, profile_pic, Bio):
        self.id = id
        self.user_name = user_name
        self.email = email
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.Bio = Bio
        self.profile_pic = profile_pic
        self.items = []

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

class Item:# מאפיינים של אייטם
    def __init__(self, name, year, condition, price, other, date, owner_id, product_picture, item_id):
        self.name = name
        self.year = year
        self.condition = condition
        self.price = price
        self.other = other
        self.date = date
        self.owner_id = owner_id
        self.product_picture = product_picture
        self.item_id = item_id


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'

    from .auth import auth
    from .profile_changes import profile_changes
    from .pages import pages
    from .item_funcs import item_funcs


    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(profile_changes, url_prefix='/')
    app.register_blueprint(pages, url_prefix='/')
    app.register_blueprint(item_funcs, url_prefix='/')
    

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        user_ref = db.collection('Users').document(user_id)
        user_data = user_ref.get()

        if user_data.exists:
            user_info = user_data.to_dict()

            user = User(
                id=user_id,
                user_name=user_info.get('user_name', 'Unknown'),
                email=user_info.get('email', 'Unknown'),
                password=user_info.get('password', ''),
                first_name=user_info.get('first_name', ''),
                last_name=user_info.get('last_name', ''),
                profile_pic=user_info.get('profile_pic', None),
                Bio=user_info.get('Bio', 'Unknown')
            )

            items_ref = user_ref.collection('Items').stream()
            user.items = [
                Item(
                    name=item.to_dict().get('name'),
                    year=item.to_dict().get('year'),
                    condition=item.to_dict().get('condition'),
                    price=item.to_dict().get('price'),
                    other=item.to_dict().get('other'),
                    date=item.to_dict().get('date'),
                    owner_id=user_id,
                    product_picture=item.to_dict().get('product_picture'),
                    item_id=item.to_dict().get('item_id')
                )
                for item in items_ref
            ]

            return user
        return None

    @app.route('/Myprofile', methods=['GET', 'POST'])
    @login_required
    def profile():
        user_ref = db.collection('Users').document(current_user.id)
        user_data = user_ref.get()
        if user_data.exists:
            user = user_data.to_dict()
            return render_template("Myprofile.html", user=current_user)
        flash("User not found!", category='error')
        return redirect(url_for('auth.login'))
    
    gmaps = googlemaps.Client(key='AIzaSyAtcWj6Uog3a16LgoF9NeXe_A951igbzsc')

    @app.route('/autocomplete', methods=['GET'])
    def autocomplete_address():
        input_text = request.args.get('input')
        print(f"Input received: {input_text}")  # Debugging line
        if not input_text:
            return jsonify({'predictions': []})
        try:
            autocomplete_result = gmaps.places_autocomplete(input_text)
            predictions = autocomplete_result
            print(f"Predictions: {predictions}")  # Debugging line
            return jsonify({'predictions': predictions})
        except Exception as e:
            print(f"Error: {str(e)}")  # Debugging line
            return jsonify({'error': str(e)}), 500

    @app.route('/profile/<user_id>', methods=['GET', 'POST'])
    @login_required
    def profilefinder(user_id):
        user_ref = db.collection('Users').document(user_id)
        user_data = user_ref.get()

        if user_data.exists:
            user_info = user_data.to_dict()
            user = User(
                id=user_id,
                user_name=user_info.get('user_name'),
                email=user_info.get('email'),
                password=user_info.get('password'),
                first_name=user_info.get('first_name'),
                last_name=user_info.get('last_name'),
                profile_pic=user_info.get('profile_pic'),
                Bio=user_info.get('Bio')
            )
            return render_template("Profile.html", user=user)
        else:
            flash("User not found!", category='error')
            return redirect(url_for('views.index'))
    


    @app.route('/api/locations', methods=['GET'])
    def get_locations():
        try:
            items_ref = db.collection('Items').stream()
            locations = [{'address': item.to_dict().get('address')} for item in items_ref if item.to_dict().get('address')]
            return jsonify(locations)
        except Exception as e:
            print(f"Error fetching locations: {e}")
            return jsonify({'error': 'Failed to fetch locations'}), 500

    @app.errorhandler(404)  
    def page_not_found(e):
        return render_template('error.html', error=404, message="Page not found", user=current_user), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('error.html', error=500, message="Internal server error", user=current_user), 500
    return app
