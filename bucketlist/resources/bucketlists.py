from flask_restful import reqparse, Resource, marshal
from flask_httpauth import HTTPTokenAuth
from flask import Flask, request, g

from bucketlist.resources.models import BucketList, db	
from bucketlist.functionalities.serailizer import bucketlist_serializer
from bucketlist.functionalities.permissions import auth


class BucketListAPI(Resource):
	decorators = [auth.login_required]
	def get(self, id):
		"""Get a single bucket list selected by item_id
		"""
		bucket_list = BucketList.query.filter_by(list_id = id, \
			created_by = g.user.user_id).first()
		if bucket_list:
			listrequested = marshal(bucket_list, bucketlist_serializer)
			return {"listrequested": listrequested, \
			'message': 'The bucket list requested is ID: %s' %id}, 200
		else:
			return {'message': 'Error! Could not find the Bucketlist with ID:%s' %id}, 404

	def delete(self, id):
		bucket_list = BucketList.query.filter_by(list_id=id, \
			created_by = g.user.user_id).first()
		if bucket_list is not None:
			db.session.delete(bucket_list)
			db.session.commit()
			return {"message": "You have successfully deleted bucketlist with ID:%s" %id}, 200
		return {'message': 'Bucketlist not found'}, 404

class BucketListsAPI(Resource):
	decorators = [auth.login_required]
	def get(self):
		"""
		Get all the bucket lists
		"""
		search_name = request.args.get("q")
		offset = int(request.args.get("offset",1))
		limit = int(request.args.get("limit", 20))

		if search_name:
			all_bucket_lists = BucketList.query.filter_by(created_by = g.user.user_id).all()
			bucket_list = BucketList.query.filter_by(list_title=search_name,\
			 created_by = g.user.user_id).first()
			if bucket_list is not None:
				return marshal(bucket_list, bucketlist_serializer)

			return {"message": "The Bucketlist" + ", " +  search_name + ", " + "was not found", "try this instead": marshal(all_bucket_lists, bucketlist_serializer)}

		bucket_lists = BucketList.query.filter_by(created_by = g.user.user_id)\
		.paginate(page=offset, per_page=limit, error_out=False)

		pages = bucket_lists.pages
		has_prev = bucket_lists.has_prev
		has_next = bucket_lists.has_next

		if has_next:
			next_page = request.url_root + "bucketlists?" + \
				"limit=" + str(limit) + "&offset=" + str(offset + 1)
		else:
			next_page = 'Null'

		if has_prev:
			previous_page = request.url_root + "bucketlists?" + \
				"limit=" + str(limit) + "&offset=" + str(offset - 1)
		else:
			previous_page = 'Null'

		bucket_lists = bucket_lists.items

		result = {"bucketl_ists": marshal(bucket_lists, bucketlist_serializer),
				  "has_next": has_next,
				  "total_pages": pages,
				  "previous_page": previous_page,
				  "next_page": next_page
				  }
		if bucket_lists:
			return result
		else:
			return "Error"

	def post(self):
		parser = reqparse.RequestParser()
		parser.add_argument('title', type=str, \
			required=True, help= 'Provide a BucketList name')
		parser.add_argument('description', type=str)
		args = parser.parse_args(strict=True)
		title, description = args['title'], args['description']

		existing_bucketlist = BucketList.query.filter_by(list_title=title, \
			created_by=g.user.user_id).all()
		if existing_bucketlist:
			return {'message': 'Bucketlist already exits'}
		else:
			new_bucketlist = BucketList(list_title = title, \
				list_description=description, created_by=g.user.user_id)
			db.session.add(new_bucketlist)
			db.session.commit()
			return {"new_bucketlist": marshal(new_bucketlist, bucketlist_serializer)}
			

class BucketListsPutAPI(Resource):
	decorators = [auth.login_required]
	def put(self, id):
		bucket_list = BucketList.query.filter_by(list_id=id, \
			created_by=g.user.user_id).first()
		if bucket_list is None:
			return {'message': 'Bucketlist not found'}, 404

		parser = reqparse.RequestParser()
		parser.add_argument('title', type=str, required=True, \
			help='Provide a Bucketlist item')
		parser.add_argument('description', type=str)
		args = parser.parse_args(strict=True)

		
		title, description = args['title'], args['description']

		if title:
			bucket_list.list_title = title

		if description:
			bucket_list.list_description = description

		db.session.commit()

		if bucket_list is not None:
			return {"bucket_list": marshal(bucket_list, bucketlist_serializer)}, 200

