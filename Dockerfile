FROM python:3.5
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY /flask_master/requirements.txt /usr/src/app/
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
# Need to keep the copy like "./", not "./*". Otherwise, the directory structure will be changed. 
COPY ./ /usr/src/app/

WORKDIR /usr/src/app/flask_master
ENTRYPOINT ["python"]
CMD ["run_server.py"]
