FROM python:3.5
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY ./ /usr/src/app/
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Need to keep the copy like "./", not "./*". Otherwise, the directory structure will be changed. 
ENTRYPOINT ["python"]
CMD ["run_server.py"]

EXPOSE 5000
