#!/bin/bash
service mysql start
echo "test"
sleep 15
mysql -uroot -proot < /mysql/schema.sql
mysql -uroot -proot -e "use six-dof; show tables;"
service mysql stop
#sleep infinity
