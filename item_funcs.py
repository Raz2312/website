from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from . import db
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from firebase_admin import firestore
import uuid
from .models import User
from google.cloud.firestore_v1.base_query import FieldFilter
from .models import Item

item_funcs = Blueprint('item_funcs', __name__)

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'website/static/uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# /////////////////////////////////////////////////////////////////////////////////////////////////

@item_funcs.route('/create', methods=['GET', 'POST'])# פעולה מסופיה אייטם חדש למשתמש
@login_required
def create():
    if request.method == 'POST':
        name = request.form.get('name')
        year = request.form.get('year')
        condition = request.form.get('condition')
        price = request.form.get('price')
        other = request.form.get('other')
        product_picture = request.files.get('product_picture')
        address = request.form.get('address') 

        # Debugging: Print the received values
        print(f"Name: {name}, Year: {year}, Condition: {condition}, Price: {price}, Other: {other}, Address: {address}")

        try:
            year = int(year)
            price = float(price)
        except ValueError:
            flash('Year and Price must be valid numbers.', category='error')
            return render_template("create.html", user=current_user)

        if len(name) < 3:
            flash('Item name must be greater than 3 characters.', category='error')
        elif year <= 0:
            flash('Year must be a positive number.', category='error')
        elif len(condition) < 2 :
            flash('Condition must be greater than 3 characters.', category='error')
        elif price <= 0:
            flash('Price must be a positive number.', category='error')
        else:
            image_path = None
            if product_picture:
                filename = secure_filename(product_picture.filename)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                product_picture.save(filepath)
                image_path = f'uploads/{filename}'  

            # Generate a unique item_id
            unique_id = str(uuid.uuid4())

            item_data = {
                "name": name,
                "year": int(year),
                "condition": condition,
                "price": float(price),
                "other": other,
                "date": firestore.SERVER_TIMESTAMP,
                "owner_id": str(current_user.id),  
                "product_picture": image_path,
                "item_id": unique_id,
                "address": address
            }
            # Add to main Items collection using unique_id as document ID
            doc_ref = db.collection('Items').document(unique_id)
            doc_ref.set(item_data)
            
            # Add to user's Items subcollection with the same ID
            user_ref = db.collection('Users').document(str(current_user.id))
            user_ref.collection('Items').document(unique_id).set(item_data)  # Use document() instead of add()
            flash('Item added successfully!', category='success')
            return redirect(url_for('item_funcs.show_items'))

    return render_template("create.html", user=current_user)
# /////////////////////////////////////////////////////////////////////////////////////////////////

@item_funcs.route('/delete/<item_id>' , methods = ['POST'])
def delete(item_id):
    find_item = db.collection('Items').where(filter=FieldFilter('item_id', '==', item_id)).stream()
    
    for item in find_item:
        item.reference.delete()  
        user_ref = db.collection('Users').document(str(current_user.id))
        user_ref.collection('Items').document(item.id).delete()
        flash('Item deleted successfully!', category='success')
        

    return redirect(url_for('pages.profile2', owner_id=current_user.id))
# /////////////////////////////////////////////////////////////////////////////////////////////////

@item_funcs.route('/admin/delete/<item_id>' , methods = ['POST'])
@login_required
def admin_delete(item_id):
    find_item = db.collection('Items').where(filter=FieldFilter('item_id', '==', item_id)).stream()
    
    for item in find_item:
        item.reference.delete()  
        item_data = item.to_dict()  # Retrieve the document data as a dictionary
        user_id = item_data.get('owner_id')  # Access owner_id from the dictionary
        # Optionally, delete from all users' collections if needed
        user_ref = db.collection('Users').document(str(user_id))  # Corrected to user_id
        user_ref.collection('Items').document(item.id).delete()
        flash('Item deleted successfully!', category='success')
        
    return redirect(url_for('pages.admin', owner_id=current_user.id))

# /////////////////////////////////////////////////////////////////////////////////////////////////

@item_funcs.route('/public')# פעולה המציגה את כל האייטמים 
def show_items():
    items = show_items()
    return render_template('public.html', items=items, user=current_user)

# /////////////////////////////////////////////////////////////////////////////////////////////////
