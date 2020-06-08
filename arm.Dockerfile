FROM arm64v8/python:alpine

RUN pip install docker tornado

COPY *.py /root/
COPY setup.json /root/

WORKDIR /root

CMD python main.py