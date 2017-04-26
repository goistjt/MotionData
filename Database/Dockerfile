FROM mysql:latest
ENV MYSQL_DATABASE=six-dof \
    MYSQL_ROOT_PASSWORD=root

#COPY setup.sh /mysql/setup.sh
#COPY schema.sql setup.sh /mysql/init/
COPY my.cnf /mysql/.my.cnf
COPY schema.sql /docker-entrypoint-initdb.d/
#WORKDIR /mysql/init/
#COPY setup.sh /mysql/setup.sh
#WORKDIR /mysql
#RUN service mysql start && mysql < schema.sql
#RUN  /mysql/setup.sh
#RUN /bin/bash
#CMD ["service", "mysql", "start"]
EXPOSE 3306
