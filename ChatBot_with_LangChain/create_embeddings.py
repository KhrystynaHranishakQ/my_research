import pandas as pd
from utils import get_embedding
import os

DATA_DIR = 'data/products_info/'
EMBEDDINGS_DIR = 'data/products_embeddings/'


def create_embedding_data(data):
    embeddings_data = {'product_name': data['product_name'].tolist(),
                       'short_description': data['short_description'].tolist(),
                       'clean_long_description': data['clean_long_description'].tolist()}
    embeddings_data['product_name_embedding'] = [get_embedding(product) for product in embeddings_data['product_name']]
    print('Product embeddings created')
    embeddings_data['short_description_embedding'] = [get_embedding(short_description) for short_description in
                                                      embeddings_data['short_description']]
    print('Short description embeddings created')
    embeddings_data['long_description_embedding'] = [get_embedding(long_description) for long_description in
                                                     embeddings_data['clean_long_description']]
    print('Long description embeddings created')

    return embeddings_data


def main(file_path):
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
    elif file_path.endswith('.pkl'):
        df = pd.read_pickle(file_path)
    else:
        df = None
    if df is not None:
        embeddings_data = create_embedding_data(df)
        df_with_embeddings = pd.DataFrame.from_dict(embeddings_data)
        file_name = file_path.split('/')[-1]
        df_with_embeddings.to_pickle(EMBEDDINGS_DIR + file_name.split('.')[0] + '_with_embeddings' + '.pkl')
        print(f'File: {file_path} done')


if __name__ == '__main__':
    for file in os.listdir(DATA_DIR):
        main(DATA_DIR + file)
    print('Done')
