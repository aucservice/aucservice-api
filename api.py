from flask import Flask, request
from flask_restful import Resource, Api, reqparse, abort
import datetime, os, jwt, functools

app = Flask(__name__)
api = Api(app)

KEY = os.environ['SECRET_KEY']

items = {
	"A" : {"price": 123},
	"B" : {"price": 256},
	"C" : {"price": 112}
}

users = {
	"user" : {"password": "pass"}
}

parser = reqparse.RequestParser()
parser.add_argument('price')

def login_required(method):
	@functools.wraps(method)
	def wrapper(*args, **kwargs):
		header = request.headers.get('Authorization')
		if header is None:
			abort(400, message='Login is required')
		_, token = header.split()
		try:
			decoded = jwt.decode(token, KEY, algorithms='HS256')
		except jwt.DecodeError:
			abort(400, message='Token is not valid.')
		except jwt.ExpiredSignatureError:
			abort(400, message='Token is expired.')
		username = decoded['username']
		if username not in users:
			abort(400, message=f'User {username} is not found.')
		user = users[username]
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
		args = parser.parse_args()
		username = request.json['username']
		password = request.json['password']
		if username not in users:
			abort(404, message=f"User {username} does not exist")
		user = users['user']
		if password != user['password']:
			abort(400, message="Password is incorrect")
		exp = datetime.datetime.utcnow() + datetime.timedelta(hours=24)
		token = jwt.encode({'username': username, 'exp': exp}, KEY, algorithm='HS256')
		return {'username': username, 'token': token}

class HelloWorld(Resource):
	def get(self):
		return {'name': 'aucservice'}

api.add_resource(HelloWorld, '/')
api.add_resource(Items, '/items')
api.add_resource(Item, '/items/<item_id>')
api.add_resource(Login, '/login')

if __name__ == '__main__':
	app.run(debug=True)
