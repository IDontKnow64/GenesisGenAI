from flask import Blueprint, jsonify

auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/login', methods=['POST'])
def login():
    # Handle login logic
    return jsonify({"message": "Login successful!"})

@auth_blueprint.route('/register', methods=['POST'])
def register():
    # Handle registration logic
    return jsonify({"message": "Registration successful!"})
