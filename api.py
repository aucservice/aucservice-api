from flask import Flask, request
from flask_restful import Resource, Api, reqparse, abort
from flask_sqlalchemy import SQLAlchemy
import datetime, os, jwt, functools
from werkzeug.security import generate_password_hash, check_password_hash
import re
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
Config.init_app(app)
api = Api(app)
db = SQLAlchemy()
db.init_app(app)

items = {
	"A" : {"price": 123},
	"B" : {"price": 256},
	"C" : {"price": 112}
}

parser = reqparse.RequestParser()
parser.add_argument('price')

class User(db.Model):
	__tablename__ = 'user'
	username = db.Column(db.String(256), unique = True, index = True, primary_key = True)
	password_hash = db.Column(db.String(128))

	@property
	def password(self):
		raise AttributeError()

	@password.setter
	def password(self, password):
		self.password_hash = generate_password_hash(password)

def login_required(method):
	@functools.wraps(method)
	def wrapper(*args, **kwargs):
		header = request.headers.get('Authorization')
		if header is None:
			abort(403, message='Login is required')
		try:
			_, token = header.split()
		except:
			abort(400, message='Incorrect header')
		try:
			decoded = jwt.decode(token, app.config['SECRET_KEY'], algorithms='HS256')
		except jwt.DecodeError:
			abort(400, message='Token is not valid')
		except jwt.ExpiredSignatureError:
			abort(400, message='Token is expired')
		username = decoded['username']
		user = User.query.filter_by(username=username).first()
		if user == None:
			abort(400, message=f'User {username} is not found.')
		return method(*args, **kwargs)
	return wrapper

class Item(Resource):
	def get(self, item_id):
		if item_id not in items:
			abort(404, message=f"Item {item_id} does not exist")
		return items[item_id]

	@login_required
	def delete(self, item_id):
		if item_id not in items:
			abort(404, message=f"Item {item_id} does not exist")
		del items[item_id]
		return '', 204

	@login_required
	def put(self, item_id):
		args = parser.parse_args()
		item = {'price': args['price']}
		items[item_id] = item
		return item, 201

class Items(Resource):
	def get(self):
		return items

class Login(Resource):
	def get(self):
		username = request.json['username']
		password = request.json['password']
		user = User.query.filter_by(username=username).first()
		if user == None:
			abort(404, message=f"User {username} does not exist")
		if not check_password_hash(user.password_hash, password):
			abort(401, message="Password is incorrect")
		exp = datetime.datetime.utcnow() + datetime.timedelta(hours=24)
		token = jwt.encode({'username': username, 'exp': exp}, app.config['SECRET_KEY'], algorithm='HS256')
		return {'username': username, 'token': token}

class Register(Resource):
	def post(self):
		username = request.json['username']
		password = request.json['password']
		if not re.match(r'^[A-Za-z0-9_]+$', username):
			abort(400, message="Username is not valid")
		if len(password) < 4:
			abort(400, message="Password is too short")
		if User.query.filter_by(username=username).first():
			abort(409, message=f"User {username} already exists")
		user = User(username=username, password=password)
		db.session.add(user)
		db.session.commit()
		return {"message": "User registered successfully"}

class UserList(Resource):
	@login_required
	def get(self):
		return {"users": [u.username for u in User.query.all()]}


class Name(Resource):
	def get(self):
		return {'name': 'aucservice'}

api.add_resource(Name, '/')
api.add_resource(Items, '/items')
api.add_resource(Item, '/items/<item_id>')
api.add_resource(Login, '/login')
api.add_resource(Register, '/register')
api.add_resource(UserList, '/users')

if __name__ == '__main__':
	app.run(debug=True)
