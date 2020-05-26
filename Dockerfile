FROM python:3.7-alpine
RUN apk --update --no-cache add git openssh-client

COPY requirements.txt /app/
RUN pip3 install -r /app/requirements.txt

COPY devman.py /app/

WORKDIR /app
ENTRYPOINT ["python3" , "devman.py"]
