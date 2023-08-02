FROM python:3

RUN mkdir -p /opt/src/application
WORKDIR /opt/src/application

COPY application/courier.py ./courier.py
COPY application/configuration.py ./configuration.py
COPY application/models.py ./models.py
COPY application/requirements_1.txt ./requirements_1.txt
COPY application/bytecode.bin ./bytecode.bin
COPY application/abi.json ./abi.json

RUN pip install -r ./requirements_1.txt

ENTRYPOINT ["python", "./courier.py"]