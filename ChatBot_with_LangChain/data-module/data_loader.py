import psycopg2
import os
from dotenv import load_dotenv
import time
import pandas as pd

load_dotenv()

current_dir = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = '/home/main/PycharmProjects/ProductChatBot_Bali/data/products_embeddings/clean_products_with_embeddings_no_nulls.pkl' #os.path.join(current_dir, 'data/products_embeddings/')


def get_db_connection():
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        return conn
    except Exception as e:
        print(f"Database connection error: {str(e)}")
        return None


def wait_for_db():
    """ Wait for the database to be ready """
    while True:
        try:
            # Try to connect to your database
            conn = get_db_connection()
            conn.close()
            break
        except Exception as e:
            print(f"Database is not up yet: {str(e)}")
            time.sleep(2)


def insert_embeddings(dataframe):
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        for product_name, short_description, clean_long_description, product_name_embedding, short_description_embedding, long_description_embedding in zip(
                dataframe['product_name'],
                dataframe['short_description'],
                dataframe['clean_long_description'],
                dataframe['product_name_embedding'],
                dataframe['short_description_embedding'],
                dataframe['long_description_embedding']):
            cur.execute("INSERT INTO product_embeddings (product_name, short_description, clean_long_description, product_name_embedding, short_description_embedding, long_description_embedding) VALUES (%s, %s, %s, %s, %s, %s);",
                        (product_name, short_description, clean_long_description, product_name_embedding, short_description_embedding, long_description_embedding))

        conn.commit()
        cur.close()
        conn.close()
    else:
        raise ConnectionError()


def load_data(path=DATA_PATH):
    if os.path.isdir(path):
        for filename in os.listdir(path):
            if filename.endswith('.pkl'):
                data = pd.read_pickle(path + filename)
                insert_embeddings(data)
                print(f"Data from the file {filename} has been stored in DB")
    elif os.path.isfile(path):
        data = pd.read_pickle(path)
        insert_embeddings(data)
        print(f"Data from the file {path} has been stored in DB")

if __name__ == "__main__":
    wait_for_db()
    load_data()
    print("Done!")
