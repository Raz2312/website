from flask import render_template, request, flash, Blueprint, redirect, url_for
from flask_login import login_required, current_user
from . import db
from .models import User, Item
from firebase_admin.firestore import FieldFilter

pages = Blueprint('pages', __name__)
# /////////////////////////////////////////////////////////////////////////////////////////////////

@pages.route('/item/<item_id>/<owner_id>')
def BigItem(item_id, owner_id):
    item_ref = db.collection('Items').document(item_id)
    user_ref = db.collection('Users').document(owner_id)
    user_data = user_ref.get()
    item_data = item_ref.get()
    if item_data.exists:
        data = item_data.to_dict()
        item = Item(
            name=data['name'],
            year=data['year'],
            condition=data['condition'],
            price=data['price'],
            other=data['other'],
            date=data['date'],
            owner_id=data['owner_id'],
            product_picture=data['product_picture'],
            item_id=item_id,
            address=data['address']
        )
        if user_data.exists:
            user_data = user_data.to_dict()
            user = User(
                id=owner_id,
                user_name=user_data['user_name'],
                email=user_data['email'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                password=user_data['password'],
                Bio=user_data['Bio'],
                profile_pic=user_data['profile_pic']
            )
        
        return render_template('BigItem.html', user=user, item=item)
    else:
        flash('Item not found', category='error')
             
    
    return redirect(url_for('pages.show_items'))

# /////////////////////////////////////////////////////////////////////////////////////////////////
def show_items():
    items = []
    items = []
    users_ref = db.collection('Users')
    for user_doc in users_ref.stream():
        owner_id = user_doc.id
        items_collection = user_doc.reference.collection('Items').stream()
        for doc in items_collection:
            item_data = doc.to_dict()
            item_data['id'] = doc.id
            item_data['owner_id'] = owner_id  
            items.append(item_data)
    
    return items
def show_users():
    users = []
    users_ref = db.collection('Users').stream()
    for user in users_ref:
        user_data = user.to_dict()
        user_data['id'] = user.id
        users.append(user_data)
    return users
# /////////////////////////////////////////////////////////////////////////////////////////////////


# /////////////////////////////////////////////////////////////////////////////////////////////////

@pages.route('/index', methods=['GET', 'POST'])
def index():
    return render_template("index.html", user=current_user)

# /////////////////////////////////////////////////////////////////////////////////////////////////

@pages.route('/profile2/<owner_id>', methods=['GET'])
def profile2(owner_id):
    return render_template('Myprofile.html', user_id=owner_id,user = current_user)

# /////////////////////////////////////////////////////////////////////////////////////////////////

@pages.route('/admin', methods=['GET', 'POST'])
def admin():
    if (current_user.is_authenticated == False) or (current_user.user_name != 'admin'):
        return redirect(url_for('pages.index'))
    
    users = show_users()
    items = []
    users_ref = db.collection('Users')
    for user_doc in users_ref.stream():
        owner_id = user_doc.id
        items_collection = user_doc.reference.collection('Items').stream()
        for doc in items_collection:
            item_data = doc.to_dict()
            item_data['id'] = doc.id
            item_data['owner_id'] = owner_id  
            items.append(item_data) # Call the show_items function to retrieve items

    return render_template('admin.html', items=items, user=current_user, users = users)

# /////////////////////////////////////////////////////////////////////////////////////////////////

@pages.route('/public')# פעולה המציגה את כל האייטמים 
@login_required
def show_items():
    items = []
    users_ref = db.collection('Users')
    for user_doc in users_ref.stream():
        owner_id = user_doc.id
        items_collection = user_doc.reference.collection('Items').stream()
        for doc in items_collection:
            item_data = doc.to_dict()
            item_data['id'] = doc.id
            item_data['owner_id'] = owner_id  
            items.append(item_data)
    
    return render_template('public.html', items=items, user=current_user)
# /////////////////////////////////////////////////////////////////////////////////////////////////
@pages.route("/map")
@login_required
def Map():
    items = show_items()
    users = show_users()
    return  render_template('map.html',user = current_user,items=items,users=users)