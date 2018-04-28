#!flask/bin/python
from flask import Flask, jsonify, request, abort
from models.db import *
from auth import auth_token
import re
from datetime import datetime, timedelta

app = Flask(__name__)

menuOptions = []
users = []
menu = []
orders = []

def get_user(email):
	u = [user for user in users if user.email == email]
	print(u)
	return u[0]

@app.route('/api/auth/register/', methods=['POST'])
def create_user():
	if request.method == 'POST':
			data = request.get_json()
			email = data.get('email')
			username = data.get('username')
			password = data.get('password')
			admin = data.pop('admin', False)
			
			regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
			if email == "":
				response = jsonify({'error': 'email field cannot be blank'})
				response.status_code = 400
				return response

			elif not re.match(regex, email):
				response = jsonify({
					'error':'try entering a valid email'
				})
				response.status_code = 403
				return response
			elif username == "":
			    response = jsonify({'error': 'username field cannot be blank'})
			    response.status_code = 400
			    return response
			elif not re.match("^[a-zA-Z0-9_]*$", username):
			    response = jsonify({'error':
			                        'Username cannot contain special characters'})
			    response.status_code = 403
			    return response
			elif password == "":
			    response = jsonify({'error': 'password field has to be field'})
			    response.status_code = 400
			    return response
			elif len(password) < 5:
			    response = jsonify({'error':
			                        'Password should be more than 5 characters'})
			    response.status_code = 403
			    return response
			elif(len([user for user in users if user.email == email]) > 0):
			    response = jsonify({'error': 'user already exists'})
			    # raise a conflict error
			    response.status_code = 409
			    return response
			else:
				if(len(users) == 0):
					user_id =1	
				else:
					user_id = users[-1].user_id +1 
				userslist = {
			        'user_id': user_id,
			        'username': username,
			        'email': email,
			        'password': password,
			        'admin':admin
			        }
			    
				u = User(**userslist)
				print(u.__dict__)
				users.append(u)
				#return jsonify(userslist), 201
				response = jsonify({'message': 'welcome you now can log in'})
				#users created successfully
				response.status_code = 201
				return response


@app.route('/api/auth/login/', methods=[ 'POST'])
def login():
   
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if email == "":
            response = jsonify({'error': 'email field cannot be blank'})
            response.status_code = 400
            return response
    if password == "":
        response = jsonify({'error': 'password field has to be field'})
        response.status_code = 400
        return response

    credentials = {user.email: user.password for user in users}    
    if email in credentials.keys():
        
        encrypted_password = credentials[email]
        if Bcrypt().check_password_hash(encrypted_password, password):
            access_token = User.generate_token(email)
            if access_token:
                response = {
                    'message': 'Login successfull',
                    'access_token': access_token
                }
                print (response)
                return jsonify(response), 200
        response = {'message': 'Invalid email or password'}
        return jsonify(response), 401
        

    response = {'message': 'User does not exist. Proceed to register'}
    return jsonify(response), 401
    

@app.route('/api/users/', methods=['GET'])
@auth_token
def get_all_users(current_user_email):

	userlist = []
	for user in users:
		userlist.append(
			{'user_id': user.user_id, 
			'username': user.username,
			
			'email': user.email})
	return jsonify(userlist), 200

#create menu option
@app.route('/api/meals/', methods=['POST'])
@auth_token
def create_meal_option(current_user_email):
	user_dt = get_user(current_user_email)
	if not user_dt.admin:
		abort(403, {'message':'You are not authorised'})
	if not request.json or not 'name' in request.json or not 'price' in request.json:
		message = ''
		abort(400)
	name = request.json["name"]

	if(len([menu for menu in menuOptions if menu.name == name]) > 0):
		abort(400)

	if(len(menuOptions) == 0):
		menu_id =1
	else:
		menu_id = menuOptions[-1].menu_id +1 

	mOption = {
	    'menu_id': menu_id,
	    'name': request.json['name'],
	    'description': request.json.get('description', ""),
	    'price': request.json['price']
	}
	m = MenuOption(**mOption)

	menuOptions.append(m)
	return jsonify(mOption), 201

@app.route('/api/meals/', methods=['GET'])
@auth_token
def get_meal_options(current_user_email):
	user_dt = get_user(current_user_email)
	if not user_dt.admin:
		abort(403, {'message':'You are not authorised'})
	menuOptionsList = []
	for mn in menuOptions:
		menuOptionsList.append({'name': mn.name, 'menu_id': mn.menu_id,'description': mn.description,'price': mn.price})
	return jsonify(menuOptionsList)


@app.route('/api/meals/<int:menu_id>/', methods=['GET'])
@auth_token
def get_meal_option(menu_id, current_user_email):
	user_dt = get_user(current_user_email)
	if not user_dt.admin:
		abort(403, {'message':'You are not authorised'})
	menu = [menu for menu in menuOptions if menu.menu_id == menu_id]
	if len(menu) == 0:
	    abort(404)

	mn = menu[0]
	return jsonify({'name': mn.name, 'menu_id': mn.menu_id,'description': mn.description,'price': mn.price})

@app.route('/api/meals/<int:menu_id>/', methods=['PUT'])
@auth_token
def update_menu(menu_id, current_user_email):
	user_dt = get_user(current_user_email)
	if not user_dt.admin:
		abort(403, {'message':'You are not authorised'})
	menu = [menu for menu in menuOptions if menu.menu_id == menu_id]

	if len(menu) == 0:
	    abort(404)
	if not request.json:
	    abort(400)

	mn = menu[0]

	if 'name' in request.json :
		if(len([menu for menu in menuOptions if menu.name == name]) > 0):
			abort(400)
		mn.name = request.json["name"]
	if 'description' in request.json:
	    mn.description = request.json["description"]
	if 'price' in request.json:
	    mn.price = request.json["price"]

	return jsonify({'name': mn.name, 'menu_id': mn.menu_id,'description': mn.description,'price': mn.price})

@app.route('/api/meals/<int:menu_id>/', methods=['DELETE'])
@auth_token
def delete_menu(menu_id, current_user_email):
	user_dt = get_user(current_user_email)
	if not user_dt.admin:
		abort(403, {'message':'You are not authorised'})
	menu = [menu for menu in menuOptions if menu.menu_id == menu_id]
	if len(menu) == 0:
		abort(404)
	mn = menu[0]
	menuOptions.remove(mn)
	return jsonify({'result': True})

#create menu of the day
@app.route('/api/menu/', methods=['POST'])
@auth_token
def create_daily_menu(current_user_email):
	user_dt = get_user(current_user_email)
	if not user_dt.admin:
		abort(403, {'message':'You are not authorised'})
	if not request.json or not 'name' in request.json or not 'category' in request.json:
		message = ''
		abort(400)
	name = request.json["name"]

	if(len([d_menu for d_menu in menu if d_menu.name == name]) > 0):
		abort(400)

	if(len(menu) == 0):
		dailymenu_id =1
	else:
		dailymenu_id = menu[-1].dailymenu_id +1 

	dMenu = {
	    'dailymenu_id': dailymenu_id,
	    'date':datetime.utcnow(),
	    'name': request.json["name"],
	    'category': request.json.get('category', ""),
	}
	dm = Menu(**dMenu)

	menu.append(dm)
	return jsonify(dMenu), 201

@app.route('/api/menu/', methods=['GET'])
@auth_token
def get_menu(current_user_email):
	menuList = []
	for dm in menu:
		menuList.append({'name': dm.name, 'dailymenu_id': dm.dailymenu_id,
			'category': dm.category,'date': dm.date})
	return jsonify(menuList), 200

@app.route('/api/orders/', methods=['POST'])
@auth_token
def post_order(current_user_email):
	name = request.json['name']
	if not request.json or not 'name' in request.json or not 'quantity' in request.json:
		abort(400)
		
	if(len([order for order in orders if order.name == name]) > 0):
		abort(400)

	if(len(orders) == 0):
		order_id =1
	else:
		order_id = orders[-1].order_id +1 

	od = {
	    'order_id': order_id,
	    'name': name,
	    'quantity': request.json.get('quantity'),
	    'date': datetime.utcnow()
	}
	o = Order(**od)

	orders.append(o)
	return jsonify(od), 201

@app.route('/api/orders/', methods=['GET'])
@auth_token
def get_orders(current_user_email):
	user_dt = get_user(current_user_email)
	if not user_dt.admin:
		abort(403, {'message':'You are not authorised'})
	orderList = []
	for ol in orders:
		orderList.append({'name': ol.name, 'order_id': ol.order_id,
			'quantity': ol.quantity,'date': ol.date})
	return jsonify(orderList), 201
if __name__ == '__main__':
    app.run(debug=True)