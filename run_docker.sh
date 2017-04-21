sudo docker build -t motiondata .

#To run server
 sudo docker run -p 5000:5000 motiondata


# To run shell
sudo docker run  -it motiondata bash

#docker mysql
docker run --name db -e MYSQL_ROOT_PASSWORD=root -d -p 3306:3306 mysql
docker run --name db -e MYSQL_ROOT_PASSWORD=root -d mysql

docker exec -it db mysql -uroot -proot
