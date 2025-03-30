import firebase_admin
from firebase_admin import credentials , firestore
from flask import Flask, request, flash, Response, render_template, redirect, url_for
from flask_login import UserMixin


class User(UserMixin):#מחלקת 
    def __init__(
        self,
        id,
        Bio,
        user_name,
        email,
        password,
        first_name,
        last_name,
        profile_pic,
        items=None,
          # New attribute for items
    ):
        self.id = id
        self.user_name = user_name
        self.email = email
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.Bio = Bio
        self.profile_pic = profile_pic
        self.items = items if items is not None else []  # Initialize with empty list if not provided

    def add_item(self, item):
        """Adds an Item to the User's item list."""
        self.items.append(item)

class Item:# מאפיינים של אייטם
    def __init__(self, name, year, condition, price, other, date, owner_id, product_picture, item_id,address):
        self.name = name
        self.year = year
        self.condition = condition
        self.price = price
        self.other = other
        self.date = date
        self.owner_id = owner_id
        self.product_picture = product_picture
        self.item_id = item_id
        self.address = address