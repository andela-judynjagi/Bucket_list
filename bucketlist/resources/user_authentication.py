from flask import Flask, request, g
from sqlalchemy.exc import IntegrityError
from flask_restful import reqparse, Resource, marshal
from flask_httpauth import HTTPTokenAuth

from bucketlist.resources.models import Users, db																							
from bucketlist.functionalities.permissions import unauthorized

class Register(Resource):
	def post(self):
		parser = reqparse.RequestParser()
		parser.add_argument('username', type=str, \
			required= True, help= 'Provide a username')
		parser.add_argument('email', type=str, \
			required= True, help= 'You must provide a valid email address')
		parser.add_argument('password', type=str, \
			required= True, help= 'This is a required field')
		parser.add_argument('verify_password', type=str, \
			required= True, help= 'This is a required field')
		args = parser.parse_args(strict=True)

		username, email, password, verify_password = args.username, args.email, args.password, args.verify_password
		try:
			new_user = Users(username = username, \
				email = email, password_hash = password, )
			new_user.hash_password(password)
			new_user.hash_password(verify_password)
			if password == verify_password:
				db.session.add(new_user)
				db.session.commit()
				return {'message': 'User successfully created', 'Username': '%s.' %username, 'email address': ' %s ' %email}, 200
			return {'message': 'Sorry! Passwords do not match'}

		except (IntegrityError, AssertionError):
			db.session.rollback()
			return {'message': 'Cannot create a new user. Please enter a valid email address'}, 400

class Login(Resource):
	def post(self):
		parser = reqparse.RequestParser()
		parser.add_argument('username', type=str, required= True, \
			help= 'Provide a username', location='json')
		parser.add_argument('password', type=str, required= True, \
			help= 'This is a required field', location='json')
		args = parser.parse_args(strict=True)
		username, password = args['username'], args['password']

		# If username and password is provided, check that username matches the one in the db
		if username and password:
			user = Users.query.filter_by(username=username).first()
		else:
			return {'message': 'A username and password must be provided'}

		# Authenticate with username and password
		if user and user.verify_password(password):
			token = user.generate_auth_token(36000)
			return {'message': 'Successfully logged in. This is your  token', 'token': token.decode('ascii'), 'duration': 36000}
		else:
			return unauthorized("Incorrect username or password.")






 
