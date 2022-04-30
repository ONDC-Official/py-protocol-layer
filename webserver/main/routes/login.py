from http import HTTPStatus

from flask import jsonify, make_response
from flask_jwt_extended import set_access_cookies
from flask_restplus import Resource, reqparse, Namespace, abort

from main.service.login import login_with_args
from main.service.roles import get_role_types

login_namespace = Namespace('login', description='login utils')



@login_namespace.route("/login")
class Login(Resource):

    def create_parser_with_args(self):
        parser = reqparse.RequestParser()
        parser.add_argument("email", required=True)
        # False in case of OTP or jwt
        parser.add_argument("password", required=True)
        parser.add_argument("role", required=False, type=str,choices=get_role_types())
        return parser.parse_args()

    def post(self):
        args = self.create_parser_with_args()
        access_token = login_with_args(**args)
        if access_token:
            response_object = jsonify({'status': 'success', 'Authorization': access_token})
            set_access_cookies(response_object, access_token, max_age=86400)
            return response_object
        abort(401,message="Unable to login, either password is wrong or user is not onboarded")



@login_namespace.route('/logout')
class Logout(Resource):

    def get(self):
        resp = make_response()
        resp.set_cookie('auth_token', '', expires=0)
        return resp

