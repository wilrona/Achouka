# -*- coding: utf-8 -*-

__author__ = "Vercossa"

from api_function import *
from ..agency.models_agency import AgencyModel
from ..question.models_question import QuestionModel

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)

@app.route("/question/get/<token>")
def get_question_api(token):

    get_agency = AgencyModel.get_by_key(token)
    if not get_agency:
        return not_found(message="Your token is not correct")

    get_question = QuestionModel().query()
    data = {}
    data['status'] = 200
    data['question']
    for question in get_question:
        data['question'].append(question.make_to_dict())
    resp = jsonify(data)
    return resp
