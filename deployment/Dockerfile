FROM ubuntu

ENV DEBIAN_FRONTEND=noninteractive

RUN echo "APT::Get::Assume-Yes \"true\";" > /etc/apt/apt.conf.d/90assumeyes
RUN mkdir /root/bin
RUN apt update
RUN apt install python3 python3-pip wget curl libcurl4
RUN pip3 install flask
RUN pip3 install flask_cors
RUN pip3 install pymongo
RUN pip3 install dnspython
RUN wget https://downloads.mongodb.org/linux/mongodb-shell-linux-x86_64-ubuntu2004-4.4.6.tgz
RUN tar zxvf *.tgz
RUN mkdir mongo
RUN tar -xzf *.tgz -C mongo --strip-components=1
RUN export PATH=$PATH:/app/mongo/bin

WORKDIR /app
COPY api.py .
RUN chmod 0755 api.py
CMD ["python3", "./api.py"]

EXPOSE 8600
