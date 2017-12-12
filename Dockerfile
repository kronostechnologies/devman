FROM python:alpine
RUN apk --update --no-cache add git openssh-client
RUN pip install gitpython --upgrade && pip install pyyaml --upgrade
COPY devman /app/devman
COPY devman.conf /app/devman.conf
WORKDIR /app
entrypoint [ "python" , "devman" ]
