from flask import Flask, render_template, redirect, url_for, flash, request, session,jsonify
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from forms import RegistrationForm, LoginForm, PropertyForm
from bson.objectid import ObjectId
from config import Config

app = Flask(__name__)
app.config.from_object(Config) 
mongo_client = PyMongo(app, uri=app.config['MONGODB_URI'])
db = mongo_client.cx[app.config['MONGO_DBNAME']]
mongo = PyMongo(app)
bcrypt = Bcrypt(app)

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', title='Home')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = {
            "first_name": form.first_name.data,
            "last_name": form.last_name.data,
            "email": form.email.data,
            "password": hashed_password,
            "phone_number": form.phone_number.data,
            "role": "" 
        }
        mongo.db.users.insert_one(user)
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = mongo.db.users.find_one({"email": form.email.data})
        if user and bcrypt.check_password_hash(user['password'], form.password.data):
            session['user_id'] = str(user['_id'])
            flash('You have been logged in!', 'success')
            return redirect(url_for('choose_role'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/choose_role', methods=['GET', 'POST'])
def choose_role():
    user_id = session.get('user_id')
    if user_id:
        if request.method == 'POST':
            role = request.form.get('role')
            if role in ['buyer', 'seller']:
                user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
                if user:
                    mongo.db.users.update_one({'_id': ObjectId(user_id)}, {'$set': {'role': role}})
                    flash(f'You are now a {role}!', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    flash('User not found.', 'danger')
        return render_template('choose_role.html', title='Choose Role')
    else:
        flash('Please login to choose your role.', 'warning')
        return redirect(url_for('login'))



@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        user_id = ObjectId(session['user_id'])
        user = mongo.db.users.find_one({"_id": user_id})
        if user:
            role = user.get('role')
            print('role: %s' % role)
            if role:
                if role == 'buyer':
                    session['user_id'] = str(user['_id'])
                    return redirect(url_for('buyer_dashboard'))
                elif role == 'seller':
                    session['user_id'] = str(user['_id'])
                    return redirect(url_for('seller_dashboard'))
    return redirect(url_for('login'))

@app.route('/seller_dashboard')
def seller_dashboard():
    # Checking if the user is logged in
    if 'user_id' in session:
        print("USer loggedIN:")
        user_id = ObjectId(session['user_id'])
        user = mongo.db.users.find_one({'_id': user_id})
        first_name = user.get('first_name')
        last_name = user.get('last_name')
        # Checking if the user exists and has the "seller" role
        if user and user.get('role') == 'seller':
            properties = mongo.db.properties.find()  
            return render_template('seller_dashboard.html', title='Seller Dashboard',first_name=first_name, last_name=last_name,properties=properties)
    
    # If the user is not logged in or does not have the "seller" role, redirecting the user to the login page
    return redirect(url_for('login'))
from flask import request

@app.route('/buyer_dashboard')
def buyer_dashboard():
    filter_place = request.args.get('place')
    filter_area = request.args.get('area')
    filter_bedrooms = request.args.get('bedrooms')
    filter_bathrooms = request.args.get('bathrooms')
    filter_hospitals = request.args.get('hospitals')
    filter_colleges = request.args.get('colleges')

    query = {}

    if filter_place:
        query['place'] = filter_place
    if filter_area:
        query['area'] = filter_area
    if filter_bedrooms:
        query['bedrooms'] = int(filter_bedrooms)
    if filter_bathrooms:
        query['bathrooms'] = int(filter_bathrooms)
    if filter_hospitals:
        query['hospitals_nearby'] = filter_hospitals
    if filter_colleges:
        query['colleges_nearby'] = filter_colleges

    if query:
        filtered_properties = list(mongo.db.properties.find(query))
    else:
        filtered_properties = list(mongo.db.properties.find())
    if 'user_id' in session:
        user_id = ObjectId(session['user_id'])
        user = mongo.db.users.find_one({'_id': user_id})
        first_name = user.get('first_name')
        last_name = user.get('last_name')
        for property in filtered_properties:
            property['liked'] = user_id in property.get('liked_by', [])
    
    return render_template('buyer_dashboard.html', title='Buyer Dashboard', properties=filtered_properties,first_name=first_name, last_name=last_name)



@app.route('/post_property', methods=['GET', 'POST'])
@app.route('/post_property/<property_id>', methods=['GET', 'POST'])
def post_property(property_id=None):
    if 'user_id' not in session or session['user_id'] is None:
        flash('Please login to post a property.', 'warning')
        return redirect(url_for('login'))

    form = PropertyForm()
    if form.validate_on_submit():
        property_data = {
            "place": form.place.data,
            "area": form.area.data,
            "bedrooms": form.bedrooms.data,
            "bathrooms": form.bathrooms.data,
            "hospitals_nearby": form.hospitals_nearby.data,
            "colleges_nearby": form.colleges_nearby.data,
            "seller_id": session['user_id']  
        }
        if property_id:  
            mongo.db.properties.update_one({"_id": ObjectId(property_id)}, {"$set": property_data})
            flash('Property updated successfully!', 'success')
        else:
            # Storing property data in the database
            mongo.db.properties.insert_one(property_data)
            flash('Property posted successfully!', 'success')
        return redirect(url_for('seller_dashboard'))

    elif property_id:  
        property = mongo.db.properties.find_one({"_id": ObjectId(property_id)})
        
        form.place.data = property['place']
        form.area.data = property['area']
        form.bedrooms.data = property['bedrooms']
        form.bathrooms.data = property['bathrooms']
        form.hospitals_nearby.data = property['hospitals_nearby']
        form.colleges_nearby.data = property['colleges_nearby']
        

    return render_template('post_property.html', title='Post Property', form=form)

@app.route('/delete_property/<property_id>', methods=['POST'])
def delete_property(property_id):
    # Delete the property from the database
    mongo.db.properties.delete_one({"_id": ObjectId(property_id)})
    flash('Property deleted successfully!', 'success')
    return redirect(url_for('seller_dashboard'))

@app.route('/interested', methods=['POST'])
def interested():
    property_id = request.form.get('property_id')
    return jsonify({'message': 'Interested in property with ID: {}'.format(property_id)})

@app.route('/seller_details/<seller_id>')
def seller_details(seller_id):
    seller = mongo.db.users.find_one({'_id': ObjectId(seller_id)})
    buyer = mongo.db.users.find_one({'_id': ObjectId(session['user_id'])})
    if seller and buyer:
        seller_info = {
            'first_name': seller['first_name'],
            'last_name': seller['last_name'],
            'email': seller['email'],
            'phone_number': seller['phone_number'],
            'buyer_first_name': buyer['first_name'],
            'buyer_last_name': buyer['last_name'],
            'buyer_phone_number': buyer['phone_number'],
            'buyer_email': buyer['email'],
        }
        return jsonify(seller_info)
    if seller:
        seller['_id'] = str(seller['_id']) 
        return jsonify(seller)
    else:
        return jsonify({'error': 'Seller or buyer not found'}), 404
    
@app.route('/like_property', methods=['POST'])
@app.route('/like_property', methods=['POST'])
def like_property():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = ObjectId(session['user_id'])
    property_id = ObjectId(request.form['property_id'])
    
    property = mongo.db.properties.find_one({'_id': property_id})
    
    if property:
        if 'liked_by' not in property:
            property['liked_by'] = []

        if user_id in property['liked_by']:
            # Unlike the property
            mongo.db.properties.update_one({'_id': property_id}, {'$pull': {'liked_by': user_id}, '$inc': {'likes': -1}})
        else:
            # Like the property
            mongo.db.properties.update_one({'_id': property_id}, {'$addToSet': {'liked_by': user_id}, '$inc': {'likes': 1}})
    
    return redirect(url_for('buyer_dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
