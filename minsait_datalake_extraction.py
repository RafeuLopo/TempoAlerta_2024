# %%
from modules import azure_functions
from modules import raw_data_processor
import geopandas as gpd
import pandas as pd
import shutil

# %%
connection_string = '<CONNECTION_STRING>'
container_name = "minsait-challenge-data"

quedas_raw_blob_name = 'raw-data/quedas/'
quedas_raw_file_path = r'D:\Data_Science_Test\raw-data\quedas'

coordenada_raw_blob_name = 'raw-data/coordenada/'
coordenada_raw_file_path = r'D:\Data_Science_Test\raw-data\coordenada'

distrito_raw_blob_name = 'raw-data/distrito/'
distrito_raw_file_path = r'D:\Data_Science_Test\raw-data\distrito'

nc_files_raw_blob_name = 'raw-data/nc_files/'
nc_files_raw_file_path = r'D:\Data_Science_Test\raw-data\nc_files'

quedas_bronze_blob_name = 'bronze-data/quedas/'
quedas_bronze_file_path = r'D:\Data_Science_Test\bronze-data\quedas'

distrito_bronze_blob_name = 'bronze-data/distrito/'
distrito_bronze_file_path = r'D:\Data_Science_Test\bronze-data\distrito'

nc_files_bronze_blob_name = 'bronze-data/nc_files/'
nc_files_bronze_file_path = r'D:\Data_Science_Test\bronze-data\nc_files'

coordenada_bronze_blob_name = 'bronze-data/coordenada/'
coordenada_bronze_file_path = r'D:\Data_Science_Test\bronze-data\coordenada'

consumidora_bronze_blob_name = 'bronze-data/consumidoras/'
consumidora_bronze_file_path = r'D:\Data_Science_Test\bronze-data\consumidoras'

interrupcoes_bronze_blob_name = 'bronze-data/interrupcoes/'
interrupcoes_bronze_file_path = r'D:\Data_Science_Test\bronze-data\interrupcoes'

quedas_silver_blob_name = 'silver-data/quedas/'
quedas_silver_file_path = r'D:\Data_Science_Test\silver-data\quedas'

nc_files_silver_blob_name = 'silver-data/nc_files/'
nc_files_silver_file_path = r'D:\Data_Science_Test\silver-data\nc_files'

coordenada_silver_blob_name = 'silver-data/coordenada/'
coordenada_silver_file_path = r'D:\Data_Science_Test\silver-data\coordenada'

consumidora_silver_blob_name = 'silver-data/consumidoras/'
consumidora_silver_file_path = r'D:\Data_Science_Test\silver-data\consumidoras'

interrupcoes_silver_blob_name = 'silver-data/interrupcoes/'
interrupcoes_silver_file_path = r'D:\Data_Science_Test\silver-data\interrupcoes'

gold_blob_name = 'gold-data/'
gold_file_path = r'D:\Data_Science_Test\Datalake\gold-data'

# %%
azure_functions.download_all_blobs(connection_string, container_name, quedas_raw_blob_name, quedas_raw_file_path)
azure_functions.download_all_blobs(connection_string, container_name, coordenada_raw_blob_name, coordenada_raw_file_path)
azure_functions.download_all_blobs(connection_string, container_name, distrito_raw_blob_name, distrito_raw_file_path)
azure_functions.download_all_blobs(connection_string, container_name, nc_files_raw_blob_name, nc_files_raw_file_path)

# %%

'''
Tratamento da camada Raw (.kmz, .shp e .nc) para Bronze (.csv).
'''

kmz_file_2023 = r'D:\Data_Science_Test\raw-data\quedas\LL_WGS84_KMZ_riscoocorrencia_2023.kmz'
kmz_file_2024 = r'D:\Data_Science_Test\raw-data\quedas\LL_WGS84_KMZ_riscoocorrencia_2024.kmz'
coordenada = gpd.read_file(r'D:\Data_Science_Test\raw-data\coordenada\LOG2020_CEM_RMSP.shp')
distritos = gpd.read_file(r'D:\Data_Science_Test\raw-data\distrito\SAD69-96_SHP_distrito.shp')

kml_data_2023 = raw_data_processor.extract_kml_from_kmz(kmz_file_2023)
kml_data_2024 = raw_data_processor.extract_kml_from_kmz(kmz_file_2024)

dados_ocorrencias_2023 = raw_data_processor.parse_placemarks(kml_data_2023)
dados_ocorrencias_2024 = raw_data_processor.parse_placemarks(kml_data_2024)

dados_ocorrencias_2023 = raw_data_processor.process_ocorrencias(dados_ocorrencias_2023)
dados_ocorrencias_2024 = raw_data_processor.process_ocorrencias(dados_ocorrencias_2024)

dados_ocorrencias_2023.to_csv(r'D:\Data_Science_Test\bronze-data\quedas\quedas_dados_2023.csv', index=False)
dados_ocorrencias_2024.to_csv(r'D:\Data_Science_Test\bronze-data\quedas\quedas_dados_2024.csv', index=False)

dados_concatenados = pd.concat([dados_ocorrencias_2023, dados_ocorrencias_2024])
dados_concatenados.to_csv(r'D:\Data_Science_Test\bronze-data\quedas\quedas_dados_full.csv', index=False)

coordenada = raw_data_processor.filter_by_municipio(coordenada)
coordenada_data = coordenada.to_crs('EPSG:3857')

coordenada_data['centroid'] = coordenada_data.geometry.centroid
coordenada_data = raw_data_processor.get_centroid(coordenada)
coordenada_data = raw_data_processor.process_coordenadas(coordenada_data)
coordenada_data.to_csv(r'D:\Data_Science_Test\bronze-data\coordenada\coordenada_dados.csv', index=False)

distritos.to_csv(r'D:\Data_Science_Test\bronze-data\distrito\distritos.csv', index=False)

# %%
azure_functions.upload_all_blobs_from_folder(connection_string, container_name, quedas_bronze_blob_name, quedas_bronze_file_path)
azure_functions.upload_all_blobs_from_folder(connection_string, container_name, distrito_bronze_blob_name, distrito_bronze_file_path)
azure_functions.upload_all_blobs_from_folder(connection_string, container_name, coordenada_bronze_blob_name, coordenada_bronze_file_path)
azure_functions.upload_all_blobs_from_folder(connection_string, container_name, consumidora_bronze_blob_name, consumidora_bronze_file_path)
azure_functions.upload_all_blobs_from_folder(connection_string, container_name, interrupcoes_bronze_blob_name, interrupcoes_bronze_file_path)

# %%
azure_functions.download_all_blobs(connection_string, container_name, quedas_bronze_blob_name, quedas_bronze_file_path)
azure_functions.download_all_blobs(connection_string, container_name, distrito_bronze_blob_name, distrito_bronze_file_path)
azure_functions.download_all_blobs(connection_string, container_name, coordenada_bronze_blob_name, coordenada_bronze_file_path)
azure_functions.download_all_blobs(connection_string, container_name, consumidora_bronze_blob_name, consumidora_bronze_file_path)
azure_functions.download_all_blobs(connection_string, container_name, interrupcoes_bronze_blob_name, interrupcoes_bronze_file_path)

# %%

'''
Tratamento da camada bronze (.csv) para a silver (.parquet com tratamento dos dados).
'''

ocorrencias_path = r'D:\Data_Science_Test\bronze-data\quedas\quedas_dados_full.csv'
interrupcoes_path_2023 = r'D:\Data_Science_Test\bronze-data\interrupcoes\interrupcoes-energia-eletrica-2023.csv'
interrupcoes_path_2024 = r'D:\Data_Science_Test\bronze-data\interrupcoes\interrupcoes-energia-eletrica-2024.csv'
consumidoras_path = r'D:\Data_Science_Test\bronze-data\consumidoras\dados_consumidoras_media_tensao.csv'
coordenadas_path = r'D:\Data_Science_Test\bronze-data\coordenada\coordenada_dados.csv'

ocorrencias = pd.read_csv(ocorrencias_path)

ocorrencias[['Longitude', 'Latitude', '_']] = ocorrencias['Coordinates'].str.split(',', expand=True)
ocorrencias = ocorrencias.drop(columns=['Coordinates', '_'], axis=1)

ocorrencias['Longitude'] = pd.to_numeric(ocorrencias['Longitude'])
ocorrencias['Longitude'] = ocorrencias['Longitude'].round(6)
ocorrencias['Latitude'] = pd.to_numeric(ocorrencias['Latitude'])
ocorrencias['Latitude'] = ocorrencias['Latitude'].round(6)

ocorrencias['Data'] = pd.to_datetime(ocorrencias['Data'], format='%Y-%m-%d')
ocorrencias = ocorrencias.rename(columns={'Subpreit': 'Sub_Prefeitura'})

ocorrencias[['Sigla_Bairro', 'Nome_Bairro']] = ocorrencias['Sub_Prefeitura'].str.split(' - ', expand=True)
ocorrencias = ocorrencias.drop(columns='Sub_Prefeitura')

ocorrencias.to_parquet(r'D:\Data_Science_Test\silver-data\quedas\quedas_dados.parquet', index=False)

interrupcoes_2023 = pd.read_csv(interrupcoes_path_2023, encoding='latin1', low_memory=False, sep=';')
interrupcoes_2024 = pd.read_csv(interrupcoes_path_2024, encoding='latin1', low_memory=False, sep=';')
interrupcoes_full = pd.concat([interrupcoes_2023, interrupcoes_2024])
interrupcoes = interrupcoes_full[interrupcoes_full['NumCPFCNPJ'] == '61695227000193']

interrupcoes['DatGeracaoConjuntoDados'] = pd.to_datetime(interrupcoes['DatGeracaoConjuntoDados'], format='%Y-%m-%d')
interrupcoes['DatInicioInterrupcao'] = pd.to_datetime(interrupcoes['DatInicioInterrupcao'], format='%Y-%m-%d %H:%M:%S')
interrupcoes['DatFimInterrupcao'] = pd.to_datetime(interrupcoes['DatFimInterrupcao'], format='%Y-%m-%d %H:%M:%S')
interrupcoes['NumAno'] = pd.to_datetime(interrupcoes['NumAno'], format='%Y')

interrupcoes['IdeConjuntoUnidadeConsumidora'] = interrupcoes['IdeConjuntoUnidadeConsumidora'].astype('int')
interrupcoes['IdeMotivoInterrupcao'] = interrupcoes['IdeMotivoInterrupcao'].astype('int')

interrupcoes.to_parquet(r'D:\Data_Science_Test\silver-data\interrupcoes\interrupcoes-energia-eletrica-full.parquet', index=False)

consumidoras = pd.read_csv(consumidoras_path)

consumidoras['UNI_TR_MT'] = pd.to_numeric(consumidoras['UNI_TR_MT'], errors='coerce')

consumidoras.to_parquet(r'D:\Data_Science_Test\silver-data\consumidoras\dados_consumidoras_media_tensao.parquet', index=False)

coordenada = pd.read_csv(coordenadas_path)

coordenada = coordenada.drop(columns=['NOMESIGLA', 'NOMETIT', 'NOMEPREP', 'CEP_D', 'ONIBUS_MSP', 'coordenadas'])

coordenada['longitude'] = coordenada['longitude'].round(6)
coordenada['latitude'] = coordenada['latitude'].round(6)

coordenada = coordenada.drop_duplicates(subset=['CEP_E'])
coordenada = coordenada.rename(columns={'CEP_E': 'CEP'})

coordenada.to_parquet(r'D:\Data_Science_Test\silver-data\coordenada\coordenada_dados.parquet', index=False)

# %%
azure_functions.upload_all_blobs_from_folder(connection_string, container_name, quedas_silver_blob_name, quedas_silver_file_path)
azure_functions.upload_all_blobs_from_folder(connection_string, container_name, nc_files_silver_blob_name, nc_files_silver_file_path)
azure_functions.upload_all_blobs_from_folder(connection_string, container_name, coordenada_silver_blob_name, coordenada_silver_file_path)
azure_functions.upload_all_blobs_from_folder(connection_string, container_name, consumidora_silver_blob_name, consumidora_silver_file_path)
azure_functions.upload_all_blobs_from_folder(connection_string, container_name, interrupcoes_silver_blob_name, interrupcoes_silver_file_path)

# %%
azure_functions.download_all_blobs(connection_string, container_name, quedas_silver_blob_name, quedas_silver_file_path)
azure_functions.download_all_blobs(connection_string, container_name, nc_files_silver_blob_name, nc_files_silver_file_path)
azure_functions.download_all_blobs(connection_string, container_name, coordenada_silver_blob_name, coordenada_silver_file_path)
azure_functions.download_all_blobs(connection_string, container_name, consumidora_silver_blob_name, consumidora_silver_file_path)
azure_functions.download_all_blobs(connection_string, container_name, interrupcoes_silver_blob_name, interrupcoes_silver_file_path)

# %%
interrupcoes = pd.read_parquet(r'D:\Data_Science_Test\Datalake\silver-data\interrupcoes\interrupcoes-energia-eletrica-full.parquet')

interrupcoes['DscFatoGeradorInterrupcao'].value_counts()
name_mapping = {
    'INTERNA;NAO PROGRAMADA;PROPRIAS DO SISTEMA;FALHA DE MATERIAL OU EQUIPAMENTO': 'Falha no equipamento',
    'INTERNA;NAO PROGRAMADA;MEIO AMBIENTE;ARVORE OU VEGETACAO': 'Árvore',
    'INTERNA;NAO PROGRAMADA;MEIO AMBIENTE;VENTO': 'Vento'
}

filtered_interrupcoes = interrupcoes[
    interrupcoes['DscFatoGeradorInterrupcao'].isin(name_mapping.keys())
]

filtered_interrupcoes['DscFatoGeradorInterrupcao'] = filtered_interrupcoes[
    'DscFatoGeradorInterrupcao'
].map(name_mapping)

filtered_interrupcoes['DatInicioInterrupcao'] = pd.to_datetime(filtered_interrupcoes['DatInicioInterrupcao'])
filtered_interrupcoes['DatFimInterrupcao'] = pd.to_datetime(filtered_interrupcoes['DatFimInterrupcao'])

filtered_interrupcoes['DatInicioInterrupcao'] = filtered_interrupcoes['DatInicioInterrupcao'].dt.strftime('%Y-%m-%d %H:00:00')
filtered_interrupcoes['DatFimInterrupcao'] = filtered_interrupcoes['DatFimInterrupcao'].dt.strftime('%Y-%m-%d %H:00:00')

filtered_interrupcoes['DatInicioInterrupcao'] = pd.to_datetime(filtered_interrupcoes['DatInicioInterrupcao'])

contagem_interrupcao_bairro_data = filtered_interrupcoes.groupby(
    ['DatInicioInterrupcao', 'DscConjuntoUnidadeConsumidora', 'DscFatoGeradorInterrupcao']
).size().reset_index(name='Contagem')

contagem_interrupcao_bairro_data.rename(
    columns={
        'DscConjuntoUnidadeConsumidora': 'DISTRITO',
        'IdeConjuntoUnidadeConsumidora': 'CONJ'
    },
    inplace=True
)

contagem_interrupcao_bairro_data = contagem_interrupcao_bairro_data[
    contagem_interrupcao_bairro_data['DISTRITO'].isin(['PINHEIROS', 'VILA MARIANA', 'BUTANTÃ', 'ITAQUERA', 'SANTO AMARO'])]

pivot_df = contagem_interrupcao_bairro_data.pivot_table(
    index=['DatInicioInterrupcao', 'DISTRITO'],
    columns='DscFatoGeradorInterrupcao',
    values='Contagem',
    fill_value=0,
    aggfunc='sum'
)

pivot_df = pivot_df.reset_index()

pivot_df.columns.name = None
pivot_df = pivot_df.rename(columns={
    'Falha no equipamento': 'Falha no Equipamento',
    'Árvore': 'Árvore',
    'Vento': 'Vento'
})

pivot_df['Total_Interrupcoes'] = pivot_df[['Falha no Equipamento', 'Árvore', 'Vento']].sum(axis=1)

origem = r'D:\Data_Science_Test\Datalake\silver-data\interrupcoes\interrupcoes-energia-eletrica-full.parquet'

destino = r'D:\Data_Science_Test\Datalake\gold-data\interrupcoes-energia-eletrica-full.parquet'

shutil.copy(origem, destino)

# %%
clima_vila_mariana_2023 = pd.read_csv(r'D:\Data_Science_Test\Meteorologicos\VILA_MARIANA_2023.csv', sep=';')
clima_vila_mariana_2024 = pd.read_csv(r'D:\Data_Science_Test\Meteorologicos\VILA_MARIANA_2024.csv', sep=';')

clima_pinheiros_2023 = pd.read_csv(r'D:\Data_Science_Test\Meteorologicos\PINHEIROS_2023.csv', sep=';')
clima_pinheiros_2024 = pd.read_csv(r'D:\Data_Science_Test\Meteorologicos\PINHEIROS_2024.csv', sep=';')

clima_butanta_2023 = pd.read_csv(r'D:\Data_Science_Test\Meteorologicos\BUTANTA_2023.csv', sep=';')
clima_butanta_2024 = pd.read_csv(r'D:\Data_Science_Test\Meteorologicos\BUTANTA_2024.csv', sep=';')

clima_vila_mariana = pd.concat([clima_vila_mariana_2023, clima_vila_mariana_2024], ignore_index=True)
clima_pinheiros = pd.concat([clima_pinheiros_2023, clima_pinheiros_2024], ignore_index=True)
clima_butanta = pd.concat([clima_butanta_2023, clima_butanta_2024], ignore_index=True)

clima_vila_mariana['Estacao'] = 'VILA MARIANA'
clima_pinheiros['Estacao'] = 'PINHEIROS'
clima_butanta['Estacao'] = 'BUTANTÃ'

clima_vila_mariana['Latitude'] = -23.58
clima_vila_mariana['Longitude'] = -46.64

clima_pinheiros['Latitude'] = -23.55
clima_pinheiros['Longitude'] = -46.70

clima_butanta['Latitude'] = -23.55
clima_butanta['Longitude'] = -46.73

clima_combined = pd.concat([clima_butanta, clima_pinheiros, clima_vila_mariana], ignore_index=True)

clima_combined['Hora (UTC)']

clima_combined['Hora (UTC)'] = clima_combined['Hora (UTC)'].astype(str)

clima_combined['Hora (UTC)'] = clima_combined['Hora (UTC)'].str.zfill(4)

clima_combined['DataHora'] = clima_combined['Data'] + ' ' + clima_combined['Hora (UTC)']

clima_combined['DataHora'] = pd.to_datetime(clima_combined['DataHora'], format='%d/%m/%Y %H%M')

clima_combined.to_parquet(r'D:\Data_Science_Test\Datalake\gold-data\estacoes_concat.parquet')

# %%
merged_df = pd.merge(clima_combined, pivot_df, how='left', left_on=['DataHora', 'Estacao'], right_on=['DatInicioInterrupcao', 'DISTRITO'])

columns_of_interest = ['Falha no Equipamento', 'Vento', 'Árvore']
for col in columns_of_interest:
    merged_df[col] = merged_df[col].fillna(0)

merged_df['Total_Interrupcoes'] = merged_df['Total_Interrupcoes'].fillna(0)

cols_to_convert = [
    'Temp. Ins. (C)', 'Temp. Max. (C)', 'Temp. Min. (C)',
    'Umi. Ins. (%)', 'Umi. Max. (%)', 'Umi. Min. (%)',
    'Pressao Ins. (hPa)', 'Pressao Max. (hPa)', 'Pressao Min. (hPa)',
    'Vel. Vento (m/s)', 'Dir. Vento (m/s)', 'Raj. Vento (m/s)',
    'Chuva (mm)'
]

for col in cols_to_convert:
    merged_df[col] = pd.to_numeric(merged_df[col].str.replace(',', '.'), errors='coerce')

cols_to_int = [
    'Falha no Equipamento', 'Vento', 'Árvore', 'Total_Interrupcoes'
]

for col in cols_to_int:
    merged_df[col] = merged_df[col].astype(int)

merged_df['DataHora'] = pd.to_datetime(merged_df['DataHora'])
merged_df = merged_df[merged_df['DataHora'] <= '2024-06-29']

merged_df.to_parquet(r'D:\Data_Science_Test\Datalake\gold-data\merged_df.parquet')

columns_of_interest = ['Falha no Equipamento', 'Vento', 'Árvore']
for col in columns_of_interest:
    pivot_df[col] = pivot_df[col].fillna(0)

cols_to_int = [
    'Falha no Equipamento', 'Vento', 'Árvore', 'Total_Interrupcoes'
]

for col in cols_to_int:
    pivot_df[col] = pivot_df[col].astype(int)

# %%
meteorologicos = pd.read_parquet(r'D:\Data_Science_Test\Datalake\gold-data\estacoes_concat.parquet')
quedas = pd.read_parquet(r'D:\Data_Science_Test\Datalake\silver-data\quedas\quedas_dados_full.parquet')
interrupcoes = pd.read_parquet(r'D:\Data_Science_Test\Datalake\gold-data\interrupcoes-energia-eletrica-full.parquet')

# %%
distrito_lat_lon = pd.read_csv(r'D:\Data_Science_Test\Datalake\gold-data\distrito_lat_lon.csv')
contagem_bairro = distrito_lat_lon.merge(pivot_df, on='DISTRITO')
contagem_bairro.to_csv(r'D:\Data_Science_Test\Datalake\gold-data\contagem_bairro.csv')

# %%
interrupcoes_bairro = filtered_interrupcoes.groupby(['IdeConjuntoUnidadeConsumidora', 'DatInicioInterrupcao', 'DscConjuntoUnidadeConsumidora']).size().reset_index(name='Contagem')

teste = interrupcoes_bairro[interrupcoes_bairro['DscConjuntoUnidadeConsumidora'].isin(['VILA MARIANA', 'PINHEIROS', 'BUTANTÃ', 'MOOCA', 'SANTO AMARO','ITAQUERA'])]

teste.rename(columns={"DscConjuntoUnidadeConsumidora": "DISTRITO"}, inplace=True)
teste.rename(columns={"Contagem": "Total_Interrupcoes"}, inplace=True)
contagem_bairro_conj = teste.merge(contagem_bairro, on=['DISTRITO', 'DatInicioInterrupcao', 'Total_Interrupcoes'])
contagem_bairro_conj = contagem_bairro_conj[(contagem_bairro_conj['DatInicioInterrupcao'] >= '2024-01-01') & (contagem_bairro_conj['DatInicioInterrupcao'] <= '2024-06-29')]
contagem_bairro_conj.to_csv(r'D:\Data_Science_Test\Datalake\gold-data\contagem_bairro_conj.csv')

# %%
quedas['Data'] = pd.to_datetime(quedas['Data'])

contagem_por_bairro_e_data = quedas.groupby(['Data', 'Nome_Bairro']).size().reset_index(name='Contagem')

contagem_por_bairro_e_data

localizacao_media_por_bairro = quedas.groupby('Nome_Bairro').agg({
    'Latitude': 'mean',
    'Longitude': 'mean'
}).reset_index()

localizacao_media_por_bairro

contagem_localizacao_data = contagem_por_bairro_e_data.merge(localizacao_media_por_bairro, on='Nome_Bairro')
contagem_localizacao_data

contagem_localizacao_data.to_csv(r'D:\Data_Science_Test\Datalake\gold-data\contagem_localizacao_data.csv')

# %%
interrupcoes['DataInterrupcao'] = interrupcoes['DatInicioInterrupcao'].dt.date

interrupcoes_por_data = interrupcoes.groupby(['IdeConjuntoUnidadeConsumidora', 'DataInterrupcao']).size().reset_index(name='QuantidadeInterrupcoes')

interrupcoes_por_data.to_csv(r'D:\Data_Science_Test\Datalake\gold-data\interrupcoes_data.csv')

# %%
azure_functions.upload_all_blobs_from_folder(connection_string, container_name, gold_blob_name, gold_file_path)
