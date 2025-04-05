from kafka import KafkaConsumer
import json
import pandas as pd
import os

def consume_bds_news(df, columns):
    consumer = KafkaConsumer(
        'bds_news',
        bootstrap_servers=['localhost:9092'],
        # max_poll_records=100,s
        enable_auto_commit=True,
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    print("Consuming messages from 'bds_news' topic...")
    try:
        for message in consumer:
            data = message.value
            out = data["price"], data["s"], data["position"], data["types"], data["benefit"]
            new_data = [out]
            df_new = pd.DataFrame(new_data, columns=columns)
            df = pd.concat([df, df_new], ignore_index=True)
            df.to_csv(csv_path, mode='a', header=False, index=False, encoding='utf-8')
            
    except Exception as e:
        print(f"Error consuming messages: {e}")
    finally:
        consumer.close()
        print("Consumer closed.")

if __name__ == "__main__":

    csv_path = "../info/info.csv"
    columns = ["Price", "Area", "Position", "Type", "Benefit"]
    
    # If the CSV file doesn't exist, create it with headers
    if not os.path.exists(csv_path):
        pd.DataFrame(columns=columns).to_csv(csv_path, index=False, encoding='utf-8')

    # Read the existing CSV into a Pandas DataFrame
    df = pd.read_csv(csv_path, encoding='utf-8')
    
    consume_bds_news(df, columns)
