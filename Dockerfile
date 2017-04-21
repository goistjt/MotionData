FROM python:3.5
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY /flask_master/requirements.txt /usr/src/app/
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY ./* /usr/src/app/

WORKDIR /usr/src/app/flast_master
ENTRYPOINT ["python"]
CMD ["run_server.py"]
