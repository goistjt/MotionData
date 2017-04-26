#!/bin/bash
service mysql start
sleep 1
mysql -uroot -proot < /mysql/schema.sql
#mysql -uroot -proot -e "use six-dof; show tables;"
#sleep infinity
