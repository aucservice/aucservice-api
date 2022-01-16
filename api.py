from flask import Flask
from flask_restful import Resource, Api, reqparse, abort

app = Flask(__name__)
api = Api(app)

items = {
	"A" : {"price": 123},
	"B" : {"price": 256},
	"C" : {"price": 112}
}

parser = reqparse.RequestParser()
parser.add_argument('price')

class Item(Resource):
	def get(self, item_id):
		if item_id not in items:
			abort(404, message=f"Item {item_id} does not exist")
		return items[item_id]

	def delete(self, item_id):
		if item_id not in items:
			abort(404, message=f"Item {item_id} does not exist")
		del items[item_id]
		return '', 204

	def put(self, item_id):
		args = parser.parse_args()
		item = {'price': args['price']}
		items[item_id] = item
		return item, 201

class Items(Resource):
	def get(self):
		return items

class HelloWorld(Resource):
    def get(self):
        return {'name': 'aucservice'}

api.add_resource(HelloWorld, '/')
api.add_resource(Items, '/items')
api.add_resource(Item, '/items/<item_id>')

if __name__ == '__main__':
    app.run(debug=True)
