# -*- coding: utf-8 -*-

__author__ = "Vercossa"

from api_function import *
from ..agency.models_agency import AgencyModel
from ..departure.models_departure import DepartureModel

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)

@app.route('/departure/get/<token>')
def get_departure_api(token):
    
    try:
        date = datetime.datetime.combine(function.date_convert(request.args.get('last_update')), function.time_convert(request.args.get('time')))
    except:
        date = None

    get_agency = AgencyModel.get_by_key(token)
    if not get_agency:
        return not_found(message="Your token is not correct")

    if date:
        get_departure = DepartureModel().query(
            DepartureModel.date_update >= date
        )
    else:
        get_departure = DepartureModel().query()

    data = {'status': 200, 'departure': []}
    for departure in get_departure:
        data['departure'].append(departure.make_to_dict())
    resp = jsonify(data)
    return resp
