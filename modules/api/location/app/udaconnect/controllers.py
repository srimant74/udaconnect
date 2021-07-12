import logging
from app.udaconnect.models import  Location
from app.udaconnect.schemas import  LocationSchema
from app.udaconnect.services import  LocationService
from flask import request,jsonify
from flask_accepts import accepts, responds
from flask_restx import Namespace, Resource

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

DATE_FORMAT = "%Y-%m-%d"

api = Namespace("Location", description="Location API")  # noqa


@api.route("/locations")
class LocationCreateResource(Resource):
    @accepts(schema=LocationSchema)
    def post(self):
        location = LocationService.create(request.get_json())
        logger.warning('PRINTING MESSAGE')
        logger.warning(location)
        return location,202

@api.route("/locations/<location_id>", methods=['GET'])
@api.param("location_id", "Unique ID for a given Location", _in="query")
class LocationResource(Resource):

    @responds(schema=LocationSchema)
    def get(self, location_id) -> Location:
        location: Location = LocationService.retrieve(location_id)
        return location



