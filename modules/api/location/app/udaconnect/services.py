import logging
import json
from typing import Dict
from kafka import KafkaProducer
from app import db
from app.udaconnect.models import Location
from app.udaconnect.schemas import LocationSchema
from geoalchemy2.functions import ST_AsText, ST_Point
from sqlalchemy.sql import text

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("udaconnect-location-api")

TOPIC_NAME = 'locations'
KAFKA_SERVER = 'kafka:9092'
producer = KafkaProducer(bootstrap_servers=KAFKA_SERVER)


class LocationService:
    @staticmethod
    def retrieve(location_id) -> Location:
        location, coord_text = (
            db.session.query(Location, Location.coordinate.ST_AsText())
            .filter(Location.id == location_id)
            .one()
        )

        # Rely on database to return text form of point to reduce overhead of conversion in app code
        location.wkt_shape = coord_text
        return location

    @staticmethod
    def create(location: Dict) -> Location:
        validation_results: Dict = LocationSchema().validate(location)
        if validation_results:
            logger.warning(f"Unexpected data format in payload: {validation_results}")
            raise Exception(f"Invalid payload: {validation_results}")

        #new_location = Location()
        #new_location.person_id = location["person_id"]
        #new_location.creation_time = location["creation_time"]
        #new_location.coordinate = ST_Point(location["latitude"], location["longitude"])

        location_json_data = json.dumps(location).encode()
        # Kafka producer has already been set up in Flask context
        producer.send(TOPIC_NAME, location_json_data)

        logger.warning(location)
        return location

    @staticmethod
    def persistInDB(location: Dict) :

        new_location = Location()
        new_location.person_id = location["person_id"]
        new_location.creation_time = location["creation_time"]
        new_location.coordinate = ST_Point(location["latitude"], location["longitude"])
        logger.warning(new_location)
        db.session.add(new_location)
        db.session.commit()

    

