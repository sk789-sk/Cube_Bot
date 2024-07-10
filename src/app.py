
from flask import make_response, jsonify, request
import uuid

from config import app , db
from models import * 

##Test Routes##

@app.route('/')
def home():
    return 'll'

@app.route('/matches')
def matches():
    matches = Match.query.all()
    match_list = [match.to_dict() for match in matches]

    response = make_response(jsonify(match_list),200)
    return response
if __name__ == '__main__':

    app.run(port=5555, debug=True)

