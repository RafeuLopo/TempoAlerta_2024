# %%
import os
import streamlit as st
import streamlit.components.v1 as components
import pickle
import numpy as np
import folium
import requests
from datetime import datetime, timedelta
import pytz
import base64
import io
import json
from PIL import Image
from warnings import filterwarnings
from azure.storage.blob import BlobServiceClient

filterwarnings('ignore')

st.set_page_config(layout="wide")

# %%
STORAGE_CONNECTION_STRING = os.getenv('STORAGE_CONNECTION_STRING')
CONTAINER_NAME = "minsait-challenge-data"

USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')

blob_service_client = BlobServiceClient.from_connection_string(STORAGE_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(CONTAINER_NAME)

# %%
global vento, chuva
vento, chuva = 0.0, 0.0

REGIONS_COORDINATES = {
    "Pinheiros": [-23.561684, -46.699982],
    "Butantã": [-23.573230, -46.716330],
    "Vila Mariana": [-23.588600, -46.634500]
}


@st.cache_resource
def load_model():
    blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob='model/Anomaly_Detection_Challenge_4.pkl')
    
    blob_data = blob_client.download_blob()
    model_data = blob_data.readall()

    model = pickle.load(io.BytesIO(model_data))
    return model


def predict_anomaly(valores):
    model = load_model()

    valores = valores.reshape(1, -1)
    
    anomaly_prediction = model.predict(valores)

    if anomaly_prediction == '6-15' or anomaly_prediction == '15+':    
        return {
            "anomaly_detected": True,
            "regions": ["Pinheiros", "Butantã", "Vila Mariana"],
            "valor": anomaly_prediction[0]
        }
    else:
        return {"anomaly_detected": False}


def update_map_with_circles(m, regions):
    for region in regions:
        coordinates = REGIONS_COORDINATES[region]
        folium.Circle(
            location=coordinates,
            radius=500,
            color='red',
            fill=True,
            fill_opacity=0.6,
            popup=f"Anomalia detectada em {region}"
        ).add_to(m)
    return m


def save_map(m, filename="map.html"):
    map_path = os.path.join(os.getcwd(), filename)
    m.save(map_path)
    return map_path


def display_map(map_path):
    with open(map_path, 'r', encoding='utf-8') as file:
        map_html = file.read()
    
    components.html(map_html, height=500, width=700)


def proxima_hora(custom_hour):
    fuso_sao_paulo = pytz.timezone('America/Sao_Paulo')
    
    agora = datetime.now(fuso_sao_paulo)
    
    proxima_hora = (agora + timedelta(hours=int(custom_hour))).replace(minute=0, second=0, microsecond=0)
    
    proxima_hora = proxima_hora.strftime('%Y-%m-%dT%H:00Z')

    return proxima_hora

def obter_dados_meteorologicos(hora):
    global vento, chuva
    username = USERNAME
    password = PASSWORD
    
    datetime = proxima_hora(hora)

    parameters = 'wind_speed_10m:kmh,precip_1h:mm'
    
    location = '-23.5505,-46.6333'
    
    format_type = 'json'
    
    url = f'https://{username}:{password}@api.meteomatics.com/{datetime}/{parameters}/{location}/{format_type}'

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()

        vento = data['data'][0]['coordinates'][0]['dates'][0]['value']
        chuva = data['data'][1]['coordinates'][0]['dates'][0]['value']
        
        print(f"Vento: {vento} km/h, Chuva: {chuva} mm")
        return vento, chuva
    
    else:
        print('Erro na requisição:', response.status_code)

def list_blobs_in_directory(container_client, directory_name):
    blob_list = container_client.list_blobs(name_starts_with=directory_name)
    return [blob.name for blob in blob_list]

def download_blob_to_image(container_client, blob_name):
    blob_client = container_client.get_blob_client(blob_name)
    blob_data = blob_client.download_blob()
    return Image.open(io.BytesIO(blob_data.readall()))

def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def get_image_files(directory):
    supported_formats = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')
    return [f for f in os.listdir(directory) if f.lower().endswith(supported_formats)]

def format_filename(filename):
    date_str = filename.split('_')[1]
    time_str = filename.split('_')[2].split('.')[0]
    datetime_obj = datetime.strptime(f"{date_str}_{time_str}", '%Y-%m-%d_%H-%M-%S')
    formatted_date = datetime_obj.strftime('%d-%m-%y %H-%M-%S')
    return formatted_date


# %%
st.title("Tempo & Alerta")
tabs = st.tabs(["Previsão de Risco", "PowerBI", 'ERA5'])

with tabs[0]:
    buff, col, buff2 = st.columns([1,3,1])
    with col:
        custom_hour = st.number_input("Digite o período de previsão futura", min_value=-24, max_value=168, value=0)

        if st.button("Realizar a previsão de áreas de risco: "):
            vento, chuva = obter_dados_meteorologicos(custom_hour)

            vento_input = st.number_input("Velocidade do Vento (km/h)", min_value=0.0, value=float(vento))
            chuva_input = st.number_input("Chuva (mm)", min_value=0.0, value=float(chuva))

            valores = np.array([vento_input, chuva_input])
            print(valores)

            m = folium.Map(location=[-23.550520, -46.633308], zoom_start=12)

            result = predict_anomaly(valores)
            
            if result["anomaly_detected"]:
                st.write("### Anomalia Detectada nas seguintes regiões:")
                
                updated_map = update_map_with_circles(m, result["regions"])
                
                map_path = updated_map._repr_html_()
                
                components.html(map_path, height=500, width=700)
                
                st.write(f"**Interrupções esperadas nestas regiões:** 15+")
            else:
                st.write("Nenhuma anomalia detectada, tudo está seguro.")
                
                map_path = m._repr_html_()
                components.html(map_path, height=500, width=700)

with tabs[1]:
    buff, col, buff2 = st.columns([1,3,1])
    with buff:      
        powerbi_embed_url = "https://app.powerbi.com/LINK_NAO_EXISTE_MAIS"

        st.markdown(f'<a href="{powerbi_embed_url}" target="_blank"><button style="padding:10px;background-color:green;color:white;border:none;border-radius:5px;">Acessar Dashboard</button></a>', unsafe_allow_html=True)
    with col:
        powerbi_embed_content = """
                <iframe title="Minsait_Dashboard" width="1140" height="541.25" src=""https://app.powerbi.com/LINK_NAO_EXISTE_MAIS"" frameborder="0" allowFullScreen="true"></iframe>
        """

        st.write("Dashboard BI")
        
        components.html(powerbi_embed_content, height=600, width=1200)

with tabs[2]:
    buff, col, buff2 = st.columns([1,3,1])
    with col:
        chuva_blobs = list_blobs_in_directory(container_client, 'era5-maps/chuva/')
        vento_blobs = list_blobs_in_directory(container_client, 'era5-maps/vento/')

        selected_directory = st.selectbox("Selecione o mapa:", ['Chuva (mm)', 'Vento (km/h)'])

        if selected_directory == 'Chuva (mm)':
            image_blobs = chuva_blobs
        elif selected_directory == 'Vento (km/h)':
            image_blobs = vento_blobs
        else:
            st.error("Diretório Inválido.")

        if not image_blobs:
            st.write(f"Nenhum dado encontrado para {selected_directory}.")
        else:
            slider_val = st.select_slider("Data/Hora", range(len(image_blobs)), format_func=lambda x: format_filename(os.path.basename(image_blobs[x])))

            selected_blob = image_blobs[slider_val]
            image = download_blob_to_image(container_client, selected_blob)

        html_content = f"""
            <style>
                .zoom-container {{
                    overflow: hidden;
                    position: relative;
                    width: 100%;
                    height: 100%;
                }}
                .zoom-container img {{
                    transition: transform 0.2s;
                    cursor: grab;
                }}
                .zoom-container img:active {{
                    cursor: grabbing;
                }}
            </style>
            <div class="zoom-container">
                <img src="data:image/png;base64,{image_to_base64(image)}" id="zoomable-image" style="width: 100%; height: 100%; object-fit: contain;">
            </div>
            <script>
                const image = document.getElementById('zoomable-image');
                let scale = 1;
                let posX = 0, posY = 0, startX, startY, isDragging = false;

                image.addEventListener('wheel', (event) => {{
                    event.preventDefault();
                    scale += event.deltaY * -0.01;
                    scale = Math.min(Math.max(1, scale), 4);  // Minimum zoom level set to 0.5
                    image.style.transform = `scale(${{scale}}) translate(${{posX}}px, ${{posY}}px)`;
                }});

                image.addEventListener('mousedown', (event) => {{
                    isDragging = true;
                    startX = event.clientX - posX;
                    startY = event.clientY - posY;
                    image.style.cursor = 'grabbing';
                }});

                image.addEventListener('mousemove', (event) => {{
                    if (!isDragging) return;
                    posX = event.clientX - startX;
                    posY = event.clientY - startY;
                    image.style.transform = `scale(${{scale}}) translate(${{posX}}px, ${{posY}}px)`;
                }});

                image.addEventListener('mouseup', () => {{
                    isDragging = false;
                    image.style.cursor = 'grab';
                }});

                image.addEventListener('mouseleave', () => {{
                    isDragging = false;
                    image.style.cursor = 'grab';
                }});
            </script>
        """
        buff, col, buff2 = st.columns([1,3,1])
        with col:
            components.html(html_content, height=500, width=600)

# %%

