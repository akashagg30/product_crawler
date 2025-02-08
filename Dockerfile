FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && apt install -y python3.9 python3-pip
RUN pip3 install --upgrade pip

WORKDIR /app

COPY requirements.txt .

RUN pip3 install --no-cache-dir -r requirements.txt
RUN playwright install-deps
RUN playwright install chromium

COPY . .

# ENV MONGO_URI="mongodb://host.docker.internal:27017/"
CMD ["python3", "-m", "src"]
