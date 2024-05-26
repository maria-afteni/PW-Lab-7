from flask import Flask, request, jsonify
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS
import jwt
import datetime
from functools import wraps
import logging
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)  # Enable CORS for all routes and origins by default
app.config['SECRET_KEY'] = 'your_secret_key'

# Configure logging
logging.basicConfig(level=logging.DEBUG)

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

@app.errorhandler(500)
def handle_500_error(e):
    response = jsonify({'message': 'Internal Server Error', 'error': str(e)})
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response, 500

@app.route('/projects', methods=['OPTIONS'])
@app.route('/projects/<int:project_id>', methods=['OPTIONS'])
def handle_options(*args, **kwargs):
    response = jsonify()
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

# Dummy data storage
projects = {}
current_id = 0

# Dummy user data
users = {
    'admin': {'password': 'admin_pass', 'role': 'ADMIN'},
    'user': {'password': 'user_pass', 'role': 'USER'},
}

# Swagger UI configuration
SWAGGER_URL = '/docs'
API_URL = '/static/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "CRUD API",
        'securityDefinitions': {
            'jwt': {
                'type': 'apiKey',
                'name': 'Authorization',
                'in': 'header'
            }
        },
        'security': [{'jwt': []}]
    }
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

def token_required(permissions=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = request.headers.get('Authorization', '').split("Bearer ")[-1]
            if not token:
                return jsonify({'message': 'Token is missing!'}), 401
            try:
                data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
                current_role = data['role']
                logging.debug(f"JWT token decoded successfully. Role: {current_role}")
            except Exception as e:
                logging.error(f"JWT decode error: {e}")  # Log JWT decode errors
                return jsonify({'message': 'Token is invalid or expired!'}), 401
            if permissions and current_role not in permissions:
                return jsonify({'message': 'Not authorized!'}), 403
            return f(current_role, *args, **kwargs)
        return decorated_function
    return decorator


@app.route('/token', methods=['POST'])
def create_token():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password required'}), 400

    user = users.get(username)
    if not user or user['password'] != password:
        return jsonify({'message': 'Invalid credentials'}), 401

    payload = {
        'role': user['role'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
    }
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    return jsonify({'token': token}), 200

@app.route('/projects', methods=['GET'])
@token_required(permissions=['ADMIN', 'WRITER', 'VISITOR'])
def get_projects(current_role):
    limit = request.args.get('limit', default=10, type=int)
    offset = request.args.get('offset', default=0, type=int)
    if limit < 0 or offset < 0:
        return jsonify({"message": "Invalid values for limit or offset. They must be non-negative."}), 400
    project_list = list(projects.values())[offset:offset+limit]
    return jsonify(project_list), 200

@app.route('/projects/<int:project_id>', methods=['GET'])
@token_required(permissions=['ADMIN', 'WRITER', 'VISITOR'])
def get_project(current_role, project_id):
    project = projects.get(project_id)
    if project:
        return jsonify(project), 200
    else:
        return jsonify({"message": "Project not found"}), 404

@app.route('/projects', methods=['POST'])
@token_required(permissions=['ADMIN', 'WRITER'])
def add_project(current_role):
    global current_id
    data = request.get_json()
    project_id = current_id
    projects[project_id] = data
    current_id += 1
    return jsonify({"message": "Project added", "id": project_id}), 201

@app.route('/projects/<int:project_id>', methods=['PUT'])
@token_required(permissions=['ADMIN', 'WRITER'])
def update_project(current_role, project_id):
    data = request.get_json()
    if project_id in projects:
        projects[project_id].update(data)
        return jsonify({"message": "Project updated"}), 200
    else:
        return jsonify({"message": "Project not found"}), 404

@app.route('/projects/<int:project_id>', methods=['DELETE'])
@token_required(permissions=['ADMIN'])
def delete_project(current_role, project_id):
    if project_id in projects:
        del projects[project_id]
        return jsonify({"message": "Project deleted"}), 200
    else:
        return jsonify({"message": "Project not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
