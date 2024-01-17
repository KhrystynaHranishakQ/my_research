import psycopg2
import os
import sys
from dotenv import load_dotenv
import utils
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from typing import List, Any

load_dotenv()

TESTING_MODE = False

SIMILARITY_THRESHOLD = 0.8


class CustomEmbeddingRetriever(BaseRetriever):
    def __init__(self, n: int, **kwargs: Any):
        super().__init__(**kwargs)

    def get_db_connection(self):
        try:
            conn = psycopg2.connect(
                dbname=os.getenv("DB_NAME", 'postgres'),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                host=os.getenv("DB_HOST"),
                port=os.getenv("DB_PORT")
            )
            return conn
        except Exception as e:
            print(f"Database connection error: {str(e)}")
            return None

    def search_context(self, query_embedding, search_by_column):

        results = None
        conn = self.get_db_connection()
        if conn:
            cur = conn.cursor()
            try:
                if search_by_column != 'short_description_embedding':
                    cur.execute(f"""
                        SELECT product_name, short_description, clean_long_description,  1 - ({search_by_column} <=> '{query_embedding}') AS cosine_similarity
                        FROM product_embeddings
                        ORDER BY cosine_similarity desc
                        LIMIT 3
                    """)
                else:
                    cur.execute(f"""
                                        SELECT product_name, short_description, clean_long_description,  1 - ({search_by_column} <=> '{query_embedding}') AS cosine_similarity
                                        FROM product_embeddings
                                        ORDER BY cosine_similarity desc
                                        LIMIT 3
                                    """)
                results = cur.fetchall()
            except Exception as error:
                print(f'Course search error: {error}')
            conn.commit()
            cur.close()
            conn.close()
        else:
            raise ConnectionError()
        return results

    def _get_relevant_documents(self, query: str, *, run_manager: CallbackManagerForRetrieverRun) -> List[Document]:
        query_embedding = utils.get_embedding(query)
        search_by_name_results = self.search_context(query_embedding, search_by_column='product_name_embedding')
        search_by_short_description_results = self.search_context(query_embedding, search_by_column='short_description_embedding')
        search_by_long_description_results = self.search_context(query_embedding, search_by_column='long_description_embedding')
        relevant_documents = []
        for result in search_by_name_results:
            if result[3] >= SIMILARITY_THRESHOLD:
                content = 'Product name: ' + result[0] + '\n' + 'Short description: ' + result[1] + '\n' + 'Long description: ' + result[2]
                doc = Document(page_content=content, metadata={'similarity': result[3], 'similarity_type': 'product_name'})
                relevant_documents.append(doc)
        for result in search_by_short_description_results:
            if result[3] >= SIMILARITY_THRESHOLD:
                content = 'Product name: ' + result[0] + '\n' + 'Short description: ' + result[1] + '\n' + 'Long description: ' + result[2]
                doc = Document(page_content=content, metadata={'similarity': result[3], 'similarity_type': 'short_description'})
                relevant_documents.append(doc)
        for result in search_by_long_description_results:
            if result[3] >= SIMILARITY_THRESHOLD:
                content = 'Product name: ' + result[0] + '\n' + 'Short description: ' + result[1] + '\n' + 'Long description: ' + result[2]
                doc = Document(page_content=content, metadata={'similarity': result[3], 'similarity_type': 'long_description'})
                relevant_documents.append(doc)
        return relevant_documents


# # TO-DO: Play with testing more
# if TESTING_MODE:
#     input_query = sys.argv[1]
#     input_query_embedding = utils.get_embedding(input_query)
#
#     search_results = search_context(input_query_embedding, search_by_column='short_description_embedding')
#     products = []
#     for r in search_results:
#         print(r[0])
#         products.append(r[0])
#     # #print(products)
#     # print('PreWash B шампунь для безконтактного миття, видалення комах')
