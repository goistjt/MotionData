sudo docker build -t motiondata .

#To run server
 sudo docker run -p 5000:5000 motiondata


# To run shell
sudo docker run  -it motiondata bash
