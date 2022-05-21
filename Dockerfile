FROM ubuntu

COPY . /opt/
WORKDIR /opt/

RUN apt-get update
RUN apt-get install -y \
    python3 \
    python3-pip

RUN pip install -r requirements.txt

CMD ["python3", "value.py"]