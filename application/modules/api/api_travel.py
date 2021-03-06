# -*- coding: utf-8 -*-

__author__ = "Vercossa"

from api_function import *
from ..agency.models_agency import AgencyModel
from ..travel.models_travel import TravelModel

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)

@app.route("/travel/get/<token>")
def get_travel_api(token):

    try:
        date = function.date_convert(request.args.get('last_update'))
    except:
        date = None

    get_agency = AgencyModel.get_by_key(token)
    if not get_agency:
        return not_found(message="Your token is not correct")

    if date:
        get_travel = TravelModel().query(
            TravelModel.date_update >= date
        )
    else:
        get_travel = TravelModel().query()

    data = {'status': 200, 'travel': []}
    for travel in get_travel:
        data['travel'].append(travel.make_to_dict())
    resp = jsonify(data)
    return resp
