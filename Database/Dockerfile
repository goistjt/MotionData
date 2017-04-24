FROM mysql:latest
ENV MYSQL_DATABASE=six-dof \
    MYSQL_ROOT_PASSWORD=root

#COPY setup.sh /mysql/setup.sh
COPY schema.sql /mysql/schema.sql
COPY my.cnf /mysql/.my.cnf
RUN service mysql start &&\ 
	sleep 5 &&\
	cd mysql &&\	
	mysql < schema.sql
#RUN  /mysql/setup.sh
#RUN /bin/bash

EXPOSE 3306
