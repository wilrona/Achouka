# -*- coding: utf-8 -*-

__author__ = "Vercossa"

from api_function import *
from ..agency.models_agency import AgencyModel
from ..destination.models_destination import DestinationModel

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)

@app.route("/destination/get/<token>")
def get_destination_api(token):

    get_agency = AgencyModel.get_by_key(token)
    if not get_agency:
        return not_found(message="Your token is not correct")

    get_destination = DestinationModel().query()
    data = {}
    data['status'] = 200
    data['departure'] = []
    for destination in get_destination:
        data['departure'].append(destination.make_to_dict())
    resp = jsonify(data)
    return resp
