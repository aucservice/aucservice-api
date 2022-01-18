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

def get_token(username):
	exp = datetime.datetime.utcnow() + datetime.timedelta(hours=24)
	token = jwt.encode({'username': username, 'exp': exp}, app.config['SECRET_KEY'], algorithm='HS256')
	return token

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

class LotModel(db.Model):
	__tablename__ = 'lot'
	id = db.Column(db.String(256), primary_key = True)
	title = db.Column(db.String(256), index = True)
	image_url = db.Column(db.String(256))
	description = db.Column(db.Text)
	bidding_end = db.Column(db.DateTime, index = True, default = datetime.datetime.utcnow)

class BidModel(db.Model):
	__tablename__ = 'bid'
	lot_id = db.Column(db.String(256), db.ForeignKey('lot.id'), primary_key=True)
	username = db.Column(db.String(256), db.ForeignKey('user.username'), primary_key=True)
	amount = db.Column(db.Integer)
	timestamp = db.Column(db.DateTime, index = True, default = datetime.datetime.utcnow)

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
		kwargs['current_user'] = user
		return method(*args, **kwargs)
	return wrapper

class LotItem(Resource):
	def get(self, lot_id):
		item = LotModel.query.filter_by(id=lot_id).first()
		if item == None:
			abort(404, message=f"Lot item {lot_id} does not exist")
		return {"id": item.id,
		"title": item.title,
		"image_url": item.image_url,
		"description": item.description,
		"bidding_end": int(item.bidding_end.timestamp())}

	@login_required
	def delete(self, lot_id, *args, **kwargs):
		item_query = LotModel.query.filter_by(id=lot_id)
		if item_query.first() == None:
			abort(404, message=f"Lot item {lot_id} does not exist")
		item_query.delete()
		db.session.commit()
		return '', 204

	@login_required
	def put(self, lot_id, *args, **kwargs):
		item_query = LotModel.query.filter_by(id=lot_id)
		if item_query.first():
			abort(409, message=f"Lot item {lot_id} already exists")
		try:
			title = request.json['title']
			description = request.json['description']
			image_url = request.json['image_url']
		except:
			abort(400, message='Incorrect header (json is required)')
		bidding_end = datetime.datetime.now()
		item = LotModel(id = lot_id, title = title, description = description, image_url = image_url, bidding_end = bidding_end)
		db.session.add(item)
		db.session.commit()
		return {"id": item.id,
		"title": item.title,
		"image_url": item.image_url,
		"description": item.description,
		"bidding_end": int(item.bidding_end.timestamp())}, 201

class LotItems(Resource):
	def get(self):
		items = LotModel.query.all()
		result = {}
		for item in items:
			result[item.id] = {"id": item.id,
			"title": item.title,
			"image_url": item.image_url,
			"description": item.description,
			"bidding_end": int(item.bidding_end.timestamp())}
		return result

class MyBid(Resource):
	@login_required
	def get(self, lot_id, *args, **kwargs):
		user = kwargs['current_user']
		bid = BidModel.query.filter_by(lot_id=lot_id, username=user.username).first()
		if bid == None:
			abort(404, message=f"Bid for lot {lot_id} by {user.username} does not exist")
		return {"lot_id": bid.lot_id,
		"username": bid.username,
		"amount": bid.amount,
		"timestamp": int(bid.timestamp.timestamp())}

	@login_required
	def delete(self, lot_id, *args, **kwargs):
		user = kwargs['current_user']
		bid_query = BidModel.query.filter_by(lot_id=lot_id, username=user.username)
		if bid_query.first() == None:
			abort(404, message=f"Bid for lot {lot_id} by {user.username} does not exist")
		bid_query.delete()
		db.session.commit()
		return '', 204

	@login_required
	def put(self, lot_id, *args, **kwargs):
		user = kwargs['current_user']
		username = user.username
		bid_query = BidModel.query.filter_by(lot_id=lot_id, username=username)
		if bid_query.first():
			abort(409, message=f"Bid for lot item {lot_id} by {username} already exists")
		try:
			amount = request.json['amount']
		except:
			abort(400, message='Incorrect header (json is required)')
		timestamp = datetime.datetime.now()
		bid = BidModel(lot_id = lot_id, username = username, amount = amount, timestamp = timestamp)
		db.session.add(bid)
		db.session.commit()
		return {"lot_id": bid.lot_id,
		"username": bid.username,
		"amount": bid.amount,
		"timestamp": int(bid.timestamp.timestamp())}

class Login(Resource):
	def get(self):
		username = request.json['username']
		password = request.json['password']
		user = User.query.filter_by(username=username).first()
		if user == None:
			abort(404, message=f"User {username} does not exist")
		if not check_password_hash(user.password_hash, password):
			abort(401, message="Password is incorrect")
		token = get_token(username)
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
	def get(self, *args, **kwargs):
		return {"users": [u.username for u in User.query.all()]}

class WhoAmI(Resource):
	@login_required
	def get(self, *args, **kwargs):
		return {"username": kwargs['current_user'].username}

class Name(Resource):
	def get(self):
		return {'name': 'aucservice'}

class RefreshToken(Resource):
	@login_required
	def get(self, *args, **kwargs):
		username = kwargs['current_user'].username
		token = get_token(username)
		return {'username': username, 'token': token}

api.add_resource(Name, '/')
api.add_resource(LotItems, '/lots')
api.add_resource(LotItem, '/lot/<lot_id>')
api.add_resource(MyBid, '/my_bid/<lot_id>')
api.add_resource(Login, '/login')
api.add_resource(Register, '/register')
api.add_resource(RefreshToken, '/refresh')
api.add_resource(UserList, '/users')
api.add_resource(WhoAmI, '/whoami')

if __name__ == '__main__':
	app.run(debug=True)
