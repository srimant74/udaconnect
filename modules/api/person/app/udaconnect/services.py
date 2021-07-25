import logging
import json
from typing import Dict, List
from kafka import KafkaProducer
from app import db
from app.udaconnect.models import Person

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("udaconnect-person-api")

TOPIC_NAME = 'persons'
KAFKA_SERVER = 'kafka:9092'
producer = KafkaProducer(bootstrap_servers=KAFKA_SERVER)

class PersonService:
    @staticmethod
    def create(person: Dict) -> Person:
        person_json_data = json.dumps(person).encode()
        # Kafka producer has already been set up in Flask context
        producer.send(TOPIC_NAME, person_json_data)
        logger.warning('Persisted Persons')
        logger.warning(TOPIC_NAME)
        logger.warning(person)
        return person

    @staticmethod
    def retrieve(person_id: int) -> Person:
        person = db.session.query(Person).get(person_id)
        return person

    @staticmethod
    def retrieve_all() -> List[Person]:
        return db.session.query(Person).all()

    @staticmethod
    def persistInDB(person: Dict) :
        new_person = Person()
        new_person.first_name = person["first_name"]
        new_person.last_name = person["last_name"]
        new_person.company_name = person["company_name"]
        db.session.add(new_person)
        db.session.commit()

