FROM python:3.9-alpine

WORKDIR .

RUN apk add --no-cache gcc musl-dev linux-headers geos libc-dev postgresql-dev
COPY requirements.txt requirements.txt
COPY script.sh ./script.sh
RUN pip install -r requirements.txt


EXPOSE 5002

COPY . .
#CMD ["python", "person_consumer.py"]
CMD ["/bin/sh", "./script.sh"]
#RUN ./script.sh
