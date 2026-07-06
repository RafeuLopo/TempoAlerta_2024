import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import haversine_distances

class DataProcessor:
    def __init__(self, ocorrencias_path, interrupcoes_path, consumidoras_path, coordenadas_path):
        self.dados_ocorrencias = pd.read_parquet(ocorrencias_path)
        self.dados_interrupcoes = pd.read_parquet(interrupcoes_path)
        self.dados_consumidoras = pd.read_parquet(consumidoras_path)
        self.dados_coordenadas = pd.read_parquet(coordenadas_path)

    def preprocess_cep_conj_data(self):
        cep_conj_data = self.dados_consumidoras[['CEP', 'CONJ']]
        cep_conj_data['CONJ'] = cep_conj_data['CONJ'].astype('object')
        cep_conj_data = cep_conj_data.drop_duplicates('CEP')
        cep_conj_data['CEP'] = cep_conj_data['CEP'].str.replace(
            '.', '').str.replace('-', '')
        cep_conj_data['CEP'] = pd.to_numeric(cep_conj_data['CEP'], errors='coerce')
        cep_conj_data.dropna(inplace=True)
        cep_conj_data['CEP'] = cep_conj_data['CEP'].astype('int')
        sp_cep_range = range(1000001, 6000000)
        cep_conj_data = cep_conj_data[cep_conj_data['CEP'].between(sp_cep_range.start, sp_cep_range.stop - 1)]
        cep_conj_data['CEP'] = cep_conj_data['CEP'].astype('object')
        cep_conj_data['CEP'] = '0' + cep_conj_data['CEP'].astype(str)
        self.cep_conj_data = cep_conj_data
        return self.cep_conj_data

    def preprocess_coordenada_data(self):
        columns_to_keep = ['CEP', 'longitude', 'latitude']
        cep_coordenada_data = self.dados_coordenadas[columns_to_keep]
        cep_coordenada_data['longitude'] = cep_coordenada_data['longitude'].round(6)
        cep_coordenada_data['latitude'] = cep_coordenada_data['latitude'].round(6)
        cep_coordenada_data['CEP'] = '0' + cep_coordenada_data['CEP'].astype(str)
        self.cep_coordenada_data = cep_coordenada_data

    def merge_data(self):
        self.cep_conj_coord_data = self.cep_conj_data.merge(self.cep_coordenada_data, how='left', left_on='CEP', right_on='CEP')
        self.cep_conj_coord_data = self.cep_conj_coord_data.dropna()
        self.cep_conj_coord_data.drop_duplicates(subset=['CEP'], inplace=True)

    def clean_interrupcoes_data(self):
        self.dados_interrupcoes['DscFatoGeradorInterrupcao'] = self.dados_interrupcoes['DscFatoGeradorInterrupcao'].replace(
            'INTERNA;NAO PROGRAMADA;MEIO AMBIENTE;ARVORE OU VEGETACAO')
        self.dados_interrupcoes = self.dados_interrupcoes.drop_duplicates(subset=['IdeConjuntoUnidadeConsumidora', 'DatInicioInterrupcao'], keep=False)
        self.dados_interrupcoes.rename(columns={'IdeConjuntoUnidadeConsumidora': 'CONJ'}, inplace=True)

    def group_data(self):
        self.grouped_data = self.cep_conj_coord_data.groupby('CONJ').agg({'CEP': list, 'longitude': list, 'latitude': list}).reset_index()
        self.grouped_conj_interrup_data = self.dados_interrupcoes.merge(self.grouped_data, on='CONJ', how='inner')
