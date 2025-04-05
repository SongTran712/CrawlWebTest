FROM gcr.io/datamechanics/spark:platform-3.1-latest

WORKDIR /app
# Install Kafka Python client
RUN pip install kafka-python pyspark==3.2.1
# COPY consumer.py /app/consumer.py