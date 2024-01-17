CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS product_embeddings (
    id serial PRIMARY KEY,
    product_name text,
    short_description text,
    clean_long_description text,
    product_name_embedding vector,
    short_description_embedding vector,
    long_description_embedding vector
                                              );
