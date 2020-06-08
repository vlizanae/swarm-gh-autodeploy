FROM arm64v8/python:alpine

RUN pip install docker tornado

COPY *.py /root/

WORKDIR /root

CMD python main.py