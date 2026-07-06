from flask import Flask, render_template, jsonify, request
import pandas as pd
from azure.storage.blob import BlobServiceClient
import io
import os
from functools import wraps

app = Flask(__name__)

CONTAINER_NAME = "minsait-challenge-data"

USERNAME = os.getenv('API_USERNAME')
PASSWORD = os.getenv('API_PASSWORD')
STORAGE_CONNECTION_STRING = os.getenv('STORAGE_CONNECTION_STRING')

blob_service_client = BlobServiceClient.from_connection_string(STORAGE_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(CONTAINER_NAME)

def check_auth(username, password):
    return username == USERNAME and password == PASSWORD

def authenticate():
    return jsonify({"message": "Authentication Required"}), 401, {'WWW-Authenticate': 'Basic realm="Login Required"'}

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

def carregar_dados_parquet(arquivo):
    try:
        blob_client = container_client.get_blob_client(arquivo)
        stream = io.BytesIO()
        blob_client.download_blob().readinto(stream)
        stream.seek(0)
        df = pd.read_parquet(stream)
        return df
    except Exception as e:
        return str(e)
    

def carregar_dados_csv(arquivo):
    try:
        blob_client = container_client.get_blob_client(arquivo)
        stream = io.BytesIO()
        blob_client.download_blob().readinto(stream)
        stream.seek(0)
        df = pd.read_csv(stream)
        return df
    except Exception as e:
        return str(e)
    

@app.route('/')
@requires_auth
def home():
    return render_template(r'index.html')


@app.route('/interrupcoes', methods=['GET'])
@requires_auth
def obter_interrupcoes():

    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    location = request.args.get('location')

    if not start_date or not end_date:
        return jsonify({"error": "Os parâmetros 'start_date' e 'end_date' são obrigatórios."}), 400

    try:
        start_date_formatada = pd.to_datetime(start_date, format='%Y-%m-%d')
        end_date_formatada = pd.to_datetime(end_date, format='%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "Formato de data inválido. Use YYYY-MM-DD."}), 400

    arquivo_interrupcoes = 'gold-data/interrupcoes-energia-eletrica-full.parquet'
    dados_interrupcoes = carregar_dados_parquet(arquivo_interrupcoes)

    if isinstance(dados_interrupcoes, str):
        return jsonify({"error": dados_interrupcoes}), 500

    dados_interrupcoes['DatInicioInterrupcao'] = pd.to_datetime(dados_interrupcoes['DatInicioInterrupcao'], errors='coerce')
    dados_interrupcoes['DatFimInterrupcao'] = pd.to_datetime(dados_interrupcoes['DatFimInterrupcao'], errors='coerce')

    dados_interrupcoes = dados_interrupcoes[
        (dados_interrupcoes['DatInicioInterrupcao'] >= start_date_formatada) &
        (dados_interrupcoes['DatInicioInterrupcao'] <= end_date_formatada)
    ]

    if location:
        dados_interrupcoes = dados_interrupcoes[dados_interrupcoes['DscConjuntoUnidadeConsumidora'].str.contains(location, case=False, na=False)]

    dados_interrupcoes = dados_interrupcoes.fillna("Valor Nulo")

    colunas_desejadas = [
        'IdeConjuntoUnidadeConsumidora', 'DscSubestacaoDistribuicao', 'IdeMotivoInterrupcao',
        'DatInicioInterrupcao', 'DatFimInterrupcao', 'DscFatoGeradorInterrupcao', 'NumNivelTensao',
        'NomAgenteRegulado', 'NumCPFCNPJ', 'DscConjuntoUnidadeConsumidora'
    ]

    dados_filtrados = dados_interrupcoes[colunas_desejadas]

    if dados_filtrados.empty:
        return jsonify({"message": "Nenhum dado encontrado para os filtros fornecidos."}), 404

    dados_json = dados_filtrados.to_dict(orient='records')
    return jsonify(dados_json)

@app.route('/estacoes', methods=['GET'])
@requires_auth
def obter_meteorologicos():
    date = request.args.get('date')
    time = request.args.get('time')
    location = request.args.get('location')
    interval_start = request.args.get('interval_start')
    interval_end = request.args.get('interval_end')

    arquivo_meteorologicos = 'gold-data/estacoes_concat.parquet'
    dados_meteorologicos = carregar_dados_parquet(arquivo_meteorologicos)

    dados_meteorologicos['DataHora'] = pd.to_datetime(dados_meteorologicos['DataHora'], errors='coerce')

    if interval_start and interval_end:
        try:
            interval_start_formatada = pd.to_datetime(interval_start, format='%d/%m/%Y')
            interval_end_formatada = pd.to_datetime(interval_end, format='%d/%m/%Y')
        except ValueError:
            return jsonify({"error": "Formato de intervalo inválido. Use DD/MM/YYYY."}), 400
        dados_meteorologicos = dados_meteorologicos[
            (dados_meteorologicos['DataHora'] >= interval_start_formatada) &
            (dados_meteorologicos['DataHora'] <= interval_end_formatada)
        ]
    elif date:
        try:
            date_formatada = pd.to_datetime(date, format='%d/%m/%Y')
            dados_meteorologicos = dados_meteorologicos[
                (dados_meteorologicos['DataHora'].dt.date == date_formatada.date())
            ]
        except ValueError:
            return jsonify({"error": "Formato de data inválido. Use DD/MM/YYYY."}), 400
    elif not interval_start and not interval_end:
        return jsonify({"error": "Pelo menos um dos parâmetros 'date', 'interval_start', ou 'interval_end' deve ser fornecido."}), 400

    if time:
        dados_meteorologicos = dados_meteorologicos[dados_meteorologicos['DataHora'].dt.strftime('%H%M') == time]

    if location:
        dados_meteorologicos = dados_meteorologicos[dados_meteorologicos['Estacao'].str.contains(location, case=False, na=False)]

    dados_meteorologicos = dados_meteorologicos.fillna("Nenhum Valor")

    colunas_desejadas = [
        'Data', 'Hora (UTC)', 'Temp. Ins. (C)', 'Temp. Max. (C)', 'Temp. Min. (C)',
        'Umi. Ins. (%)', 'Umi. Max. (%)', 'Umi. Min. (%)', 'Pto Orvalho Ins. (C)',
        'Pto Orvalho Max. (C)', 'Pto Orvalho Min. (C)', 'Pressao Ins. (hPa)', 
        'Pressao Max. (hPa)', 'Pressao Min. (hPa)', 'Vel. Vento (m/s)', 
        'Dir. Vento (m/s)', 'Raj. Vento (m/s)', 'Radiacao (KJ/m²)', 'Chuva (mm)', 
        'Estacao', 'Latitude', 'Longitude', 'DataHora'
    ]

    colunas_faltando = [col for col in colunas_desejadas if col not in dados_meteorologicos.columns]
    if colunas_faltando:
        return jsonify({"error": f"Colunas não encontradas: {', '.join(colunas_faltando)}"}), 400

    dados_filtrados = dados_meteorologicos[colunas_desejadas]

    if dados_filtrados.empty:
        return jsonify({"message": "Nenhum dado encontrado para os filtros fornecidos."}), 404

    dados_json = dados_filtrados.to_dict(orient='records')
    return jsonify(dados_json)

@app.route('/dados_agregados', methods=['GET'])
@requires_auth
def obter_dados():
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    colunas_param = request.args.get('colunas')
    
    arquivo_dados = 'gold-data/merged_df.parquet'
    dados = carregar_dados_parquet(arquivo_dados)
    
    if isinstance(dados, str):
        return jsonify({"error": dados}), 500
    
    dados['DataHora'] = pd.to_datetime(dados['DataHora'], errors='coerce')
    dados['DatInicioInterrupcao'] = pd.to_datetime(dados['DatInicioInterrupcao'], errors='coerce')

    dados = dados.dropna(subset=['DataHora', 'DatInicioInterrupcao', 'DISTRITO'])
    
    if data_inicio and data_fim:
        try:
            data_inicio_formatada = pd.to_datetime(data_inicio, format='%d/%m/%Y')
            data_fim_formatada = pd.to_datetime(data_fim, format='%d/%m/%Y')
            dados = dados[(dados['DataHora'] >= data_inicio_formatada) & (dados['DataHora'] <= data_fim_formatada)]
        except ValueError:
            return jsonify({"error": "Formato de data inválido. Use DD/MM/YYYY."}), 400

    elif data_inicio:
        try:
            data_inicio_formatada = pd.to_datetime(data_inicio, format='%d/%m/%Y')
            dados = dados[dados['DataHora'].dt.date == data_inicio_formatada.date()]
        except ValueError:
            return jsonify({"error": "Formato de data inválido. Use DD/MM/YYYY."}), 400
    
    elif not data_inicio and not data_fim:
        pass
    else:
        return jsonify({"error": "Se apenas 'data_inicio' for fornecida, não forneça 'data_fim'."}), 400

    colunas_desejadas = colunas_param.split(',') if colunas_param else [
        'DataHora', 'Vel. Vento (m/s)', 'Raj. Vento (m/s)', 'Chuva (mm)',
        'Estacao', 'Latitude', 'Longitude', 'Falha no Equipamento', 'Vento', 'Árvore', 'Total_Interrupcoes'
    ]
    
    colunas_faltando = [col for col in colunas_desejadas if col not in dados.columns]
    if colunas_faltando:
        return jsonify({"error": f"Colunas não encontradas: {', '.join(colunas_faltando)}"}), 400

    dados_filtrados = dados[colunas_desejadas]
    
    if dados_filtrados.empty:
        return jsonify({"message": "Nenhum dado encontrado para os filtros fornecidos."}), 404
    
    dados_json = dados_filtrados.to_dict(orient='records')
    return jsonify(dados_json)

if __name__ == '__main__':
    app.run(debug=True)
