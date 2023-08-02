FROM python:3

RUN mkdir -p /opt/src/application
WORKDIR /opt/src/application

COPY application/owner.py ./owner.py
COPY application/configuration.py ./configuration.py
COPY application/models.py ./models.py
COPY application/requirements.txt ./requirements.txt


RUN pip install -r ./requirements.txt


ENTRYPOINT ["python", "./owner.py"]