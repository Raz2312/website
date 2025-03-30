from flask import  render_template, request, flash , Blueprint
from flask_login import login_required, current_user
from . import db
from .models import User
from firebase_admin.firestore import FieldFilter, firestore
from werkzeug.utils import secure_filename
import os
from flask import redirect, url_for

profile_changes = Blueprint('profile_changes', __name__)

# /////////////////////////////////////////////////////////////////////////////////////////////////

@profile_changes.route('/update_bio', methods=['POST','GET'])
@login_required
def update_bio():
        bio = request.form.get('Bio')  
        user_ref = db.collection('Users').document(current_user.id)
        user_ref.update({"Bio": firestore.DELETE_FIELD})
        user_ref.update({"Bio": bio})
        flash("Bio updated successfully!", category='success')
        return redirect(url_for('pages.profile2', owner_id=current_user.id))

# /////////////////////////////////////////////////////////////////////////////////////////////////
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'website/static/profile_pictures')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@profile_changes.route('/change_profile_picture', methods=['POST','GET'])
@login_required
def change_profile_picture():
        product_picture = request.files.get('profile_picture')
        filename = secure_filename(product_picture.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        product_picture.save(filepath)
        image_path = f'profile_pictures/{filename}'
        user_ref = db.collection('Users').document(current_user.id)
        user_ref.update({"profile_pic": image_path})  
        flash("Profile picture updated successfully!", category='success')
        print(image_path)
        return redirect(url_for('pages.profile2', owner_id=current_user.id))
# /////////////////////////////////////////////////////////////////////////////////////////////////
@profile_changes.route('/delete_user/<user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
        items_ref = db.collection('Items').where('owner_id', '==', user_id).stream()  
        for item in items_ref:
            item.reference.delete()  

        user_ref = db.collection('Users').document(user_id)
        user_ref.delete()
        flash("User and their items deleted successfully!", category='success')
        return redirect(url_for('pages.admin'))