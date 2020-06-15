FROM arm64v8/python:alpine

RUN apk add git openssh-client

RUN pip install docker tornado GitPython

COPY *.py /root/

WORKDIR /root

CMD python main.py