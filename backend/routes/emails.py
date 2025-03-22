# routes/emails.py
from flask import Blueprint, jsonify

email_blueprint = Blueprint('emails', __name__)

@email_blueprint.route('/emails')
def emails():
    data = {"message": "Hello from the Flask backend!"}
    return jsonify(data)
