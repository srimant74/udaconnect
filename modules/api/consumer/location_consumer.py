from kafka import KafkaConsumer
from flask import Flask
import logging
import json
from flask_sqlalchemy import SQLAlchemy
from app.config import config_by_name
from datetime import datetime
from typing import List
from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape
from shapely.geometry.point import Point
from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.ext.hybrid import hybrid_property
from geoalchemy2.functions import ST_AsText, ST_Point

db = SQLAlchemy()


logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("udaconnect-consumer")

app = Flask(__name__)
app.config.from_object(config_by_name["prod"])
db.init_app(app)



LOCATION_TOPIC = 'locations'
PERSON_TOPIC = 'persons'
KAFKA_SERVER = 'kafka:9092'
logger.warning('Creating KafkaConsumer')
location_consumer = KafkaConsumer(LOCATION_TOPIC,bootstrap_servers=[KAFKA_SERVER])
logger.warning('Created KafkaConsumers for location ')

class Person(db.Model):
    __tablename__ = "person"

    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    company_name = Column(String, nullable=False)

class Location(db.Model):
    __tablename__ = "location"

    id = Column(BigInteger, primary_key=True)
    person_id = Column(Integer, ForeignKey(Person.id), nullable=False)
    coordinate = Column(Geometry("POINT"), nullable=False)
    creation_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    _wkt_shape: str = None

    @property
    def wkt_shape(self) -> str:
        # Persist binary form into readable text
        if not self._wkt_shape:
            point: Point = to_shape(self.coordinate)
            # normalize WKT returned by to_wkt() from shapely and ST_AsText() from DB
            self._wkt_shape = point.to_wkt().replace("POINT ", "ST_POINT")
        return self._wkt_shape

    @wkt_shape.setter
    def wkt_shape(self, v: str) -> None:
        self._wkt_shape = v

    def set_wkt_with_coords(self, lat: str, long: str) -> str:
        self._wkt_shape = f"ST_POINT({lat} {long})"
        return self._wkt_shape

    @hybrid_property
    def longitude(self) -> str:
        coord_text = self.wkt_shape
        return coord_text[coord_text.find(" ") + 1 : coord_text.find(")")]

    @hybrid_property
    def latitude(self) -> str:
        coord_text = self.wkt_shape
        return coord_text[coord_text.find("(") + 1 : coord_text.find(" ")]


for message in location_consumer:
    logger.warning (message)
    logger.warning (json.loads (message.value.decode('utf-8')))
    location = json.loads (message.value.decode('utf-8'))
    new_location = Location()
    new_location.person_id = location["person_id"]
    new_location.creation_time = location["creation_time"]
    new_location.coordinate = ST_Point(location["latitude"], location["longitude"])
    logger.warning(new_location)
    with app.app_context():
        db.session.add(new_location)
        db.session.commit()
        logger.warning('Committed')
        logger.warning(new_location)
        locations: List = db.session.query(Location).all()
        logger.warning(locations.count)
        for loc in locations:   
            logger.warning(loc)


