from flask import Flask, request, jsonify
from flask_restx import Api, Resource, fields, reqparse
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from datetime import datetime, timedelta
import uuid
from functools import wraps

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # In production, use a secure environment variable
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
jwt = JWTManager(app)
app.wsgi_app = ProxyFix(app.wsgi_app)

# Initialize Flask-RestX API
api = Api(
    app,
    version='1.0',
    title='UAP Hackathon API',
    description='API documentation for the UAP Hackathon project',
    doc='/api/docs',
    authorizations={
        'Bearer Auth': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'Type "Bearer" followed by a space and the access token'
        }
    },
    security='Bearer Auth'
)

# Define namespaces
auth_ns = api.namespace('auth', description='Authentication operations')
user_ns = api.namespace('users', description='User operations')
job_ns = api.namespace('jobs', description='Job operations')
project_ns = api.namespace('projects', description='Project operations')

# Model definitions
user_model = api.model('User', {
    'id': fields.String(readonly=True, description='Unique identifier for the user'),
    'email': fields.String(required=True, description='User email address'),
    'name': fields.String(required=True, description='Full name of the user'),
    'role': fields.String(required=True, description='User role (industry or job_seeker)'),
    'profile': fields.Nested(api.model('Profile', {
        'bio': fields.String(description='User biography'),
        'skills': fields.List(fields.String, description='User skills'),
        'experience': fields.List(fields.String, description='Work experience'),
        'education': fields.List(fields.String, description='Educational background')
    }))
})

login_model = api.model('Login', {
    'email': fields.String(required=True, description='User email address'),
    'password': fields.String(required=True, description='User password')
})

register_model = api.model('Register', {
    'email': fields.String(required=True, description='User email address'),
    'password': fields.String(required=True, description='User password'),
    'name': fields.String(required=True, description='Full name of the user'),
    'role': fields.String(required=True, description='User role (industry or job_seeker)')
})

token_model = api.model('Token', {
    'access_token': fields.String(description='JWT access token'),
    'token_type': fields.String(description='Token type'),
    'user': fields.Nested(user_model)
})

job_model = api.model('Job', {
    'id': fields.String(readonly=True, description='Unique identifier for the job'),
    'title': fields.String(required=True, description='Job title'),
    'description': fields.String(required=True, description='Job description'),
    'requirements': fields.List(fields.String, required=True, description='Job requirements'),
    'company': fields.String(required=True, description='Company name'),
    'location': fields.String(required=True, description='Job location'),
    'salary': fields.String(description='Salary range'),
    'type': fields.String(required=True, description='Job type (full-time, part-time, etc.)'),
    'createdAt': fields.DateTime(readonly=True, description='Creation timestamp'),
    'createdBy': fields.String(readonly=True, description='ID of the user who created the job')
})

project_model = api.model('Project', {
    'id': fields.String(readonly=True, description='Unique identifier for the project'),
    'title': fields.String(required=True, description='Project title'),
    'description': fields.String(required=True, description='Project description'),
    'requirements': fields.List(fields.String, required=True, description='Project requirements'),
    'company': fields.String(required=True, description='Company name'),
    'type': fields.String(required=True, description='Project type (paid or job)'),
    'budget': fields.Float(description='Project budget'),
    'deadline': fields.DateTime(description='Project deadline'),
    'createdAt': fields.DateTime(readonly=True, description='Creation timestamp'),
    'createdBy': fields.String(readonly=True, description='ID of the user who created the project')
})

submission_model = api.model('Submission', {
    'id': fields.String(readonly=True, description='Unique identifier for the submission'),
    'projectId': fields.String(required=True, description='ID of the project'),
    'userId': fields.String(readonly=True, description='ID of the user who submitted'),
    'type': fields.String(required=True, description='Submission type (quiz or project)'),
    'content': fields.Raw(required=True, description='Submission content'),
    'status': fields.String(description='Submission status'),
    'review': fields.String(description='Review feedback'),
    'paymentStatus': fields.String(description='Payment status'),
    'applicationStatus': fields.String(description='Application status'),
    'createdAt': fields.DateTime(readonly=True, description='Creation timestamp')
})

# Authentication endpoints
@auth_ns.route('/register')
class Register(Resource):
    @auth_ns.doc('user_register')
    @auth_ns.expect(register_model)
    @auth_ns.response(201, 'Success', token_model)
    @auth_ns.response(400, 'Validation Error')
    def post(self):
        """Register a new user"""
        data = request.json
        # Mock implementation
        user_id = "usr-" + str(uuid.uuid4())[:8]
        user = {
            'id': user_id,
            'email': data['email'],
            'name': data['name'],
            'role': data['role']
        }
        access_token = create_access_token(identity=user_id)
        return {
            'access_token': access_token,
            'token_type': 'Bearer',
            'user': user
        }, 201

@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.doc('user_login')
    @auth_ns.expect(login_model)
    @auth_ns.response(200, 'Success', token_model)
    @auth_ns.response(401, 'Authentication Failed')
    def post(self):
        """Log in a user and receive an access token"""
        data = request.json
        # Mock implementation
        user_id = "usr-" + str(uuid.uuid4())[:8]
        user = {
            'id': user_id,
            'email': data['email'],
            'name': 'Test User',
            'role': 'user'
        }
        access_token = create_access_token(identity=user_id)
        return {
            'access_token': access_token,
            'token_type': 'Bearer',
            'user': user
        }, 200

@auth_ns.route('/me')
class Me(Resource):
    @auth_ns.doc('get_current_user')
    @auth_ns.response(200, 'Success', user_model)
    @auth_ns.response(401, 'Unauthorized')
    @jwt_required()
    def get(self):
        """Get the current user's profile"""
        current_user_id = get_jwt_identity()
        # Mock implementation
        return {
            'id': current_user_id,
            'email': 'user@example.com',
            'name': 'Test User',
            'role': 'user'
        }, 200

# User endpoints
@user_ns.route('/<string:id>')
class UserById(Resource):
    @user_ns.doc('get_user_by_id')
    @user_ns.response(200, 'Success', user_model)
    @user_ns.response(404, 'User not found')
    @jwt_required()
    def get(self, id):
        """Get a user by ID"""
        # Mock implementation
        return {
            'id': id,
            'email': 'user@example.com',
            'name': 'Test User',
            'role': 'user'
        }, 200

@user_ns.route('/profile')
class UserProfile(Resource):
    @user_ns.doc('update_user_profile')
    @user_ns.expect(user_model)
    @user_ns.response(200, 'Success', user_model)
    @user_ns.response(401, 'Unauthorized')
    @jwt_required()
    def put(self):
        """Update the current user's profile"""
        data = request.json
        current_user_id = get_jwt_identity()
        # Mock implementation
        return {
            'id': current_user_id,
            **data
        }, 200

# Job endpoints
@job_ns.route('/')
class JobList(Resource):
    @job_ns.doc('list_jobs')
    @job_ns.response(200, 'Success', [job_model])
    def get(self):
        """Get all jobs"""
        # Mock implementation
        return [{
            'id': 'job-1',
            'title': 'Software Engineer',
            'description': 'Job description',
            'requirements': ['Python', 'Flask'],
            'company': 'Tech Corp',
            'location': 'Remote',
            'type': 'full-time'
        }], 200

    @job_ns.doc('create_job')
    @job_ns.expect(job_model)
    @job_ns.response(201, 'Success', job_model)
    @job_ns.response(401, 'Unauthorized')
    @jwt_required()
    def post(self):
        """Create a new job"""
        data = request.json
        # Mock implementation
        return {
            'id': 'job-' + str(uuid.uuid4())[:8],
            **data
        }, 201

# Project endpoints
@project_ns.route('/')
class ProjectList(Resource):
    @project_ns.doc('list_projects')
    @project_ns.response(200, 'Success', [project_model])
    @jwt_required()
    def get(self):
        """Get all projects"""
        # Mock implementation
        return [{
            'id': 'proj-1',
            'title': 'Web Development Project',
            'description': 'Project description',
            'requirements': ['React', 'Node.js'],
            'company': 'Tech Corp',
            'type': 'paid',
            'budget': 5000.0
        }], 200

    @project_ns.doc('create_project')
    @project_ns.expect(project_model)
    @project_ns.response(201, 'Success', project_model)
    @project_ns.response(401, 'Unauthorized')
    @jwt_required()
    def post(self):
        """Create a new project"""
        data = request.json
        # Mock implementation
        return {
            'id': 'proj-' + str(uuid.uuid4())[:8],
            **data
        }, 201

@project_ns.route('/<string:id>')
class ProjectById(Resource):
    @project_ns.doc('get_project')
    @project_ns.response(200, 'Success', project_model)
    @project_ns.response(404, 'Project not found')
    @jwt_required()
    def get(self, id):
        """Get a project by ID"""
        # Mock implementation
        return {
            'id': id,
            'title': 'Web Development Project',
            'description': 'Project description',
            'requirements': ['React', 'Node.js'],
            'company': 'Tech Corp',
            'type': 'paid',
            'budget': 5000.0
        }, 200

if __name__ == '__main__':
    app.run(debug=True) 