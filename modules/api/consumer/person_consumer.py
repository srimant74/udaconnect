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
person_consumer = KafkaConsumer(PERSON_TOPIC,bootstrap_servers=[KAFKA_SERVER])
logger.warning('Created KafkaConsumers for person')

class Person(db.Model):
    __tablename__ = "person"

    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    company_name = Column(String, nullable=False)


for message in person_consumer:
    logger.warning (message)
    logger.warning (json.loads (message.value.decode('utf-8')))
    person = json.loads (message.value.decode('utf-8'))
    new_person = Person()
    new_person.first_name = person["first_name"]
    new_person.last_name = person["last_name"]
    new_person.company_name = person["company_name"]
    logger.warning(new_person)
    with app.app_context():
        db.session.add(new_person)
        db.session.commit()
        logger.warning('Committed')
        logger.warning(new_person)
        persons: List = db.session.query(Person).all()
        logger.warning(persons.count)
        for perz in persons:   
            logger.warning(perz)


