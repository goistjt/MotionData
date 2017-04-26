#!/bin/bash
docker run --name db -e MYSQL_ROOT_PASSWORD=root -d mysql
