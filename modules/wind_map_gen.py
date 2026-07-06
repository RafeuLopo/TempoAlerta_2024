import folium
import os

def add_wind_map_layer(m):
    latitude_north = -18.23
    longitude_west = -54.33
    longitude_east = -40.52
    latitude_south = -28.46
    
    wind_image_folder = "wind_images"
    wind_image_files = sorted([file for file in os.listdir(wind_image_folder) if file.endswith(".png")])
    def add_image_to_map(file_path, name, control):
        img = folium.raster_layers.ImageOverlay(
            name=name,
            image=file_path,
            bounds=[[latitude_south, longitude_west], [latitude_north, longitude_east]],
            opacity=0.7,
            interactive=True,
            cross_origin=False,
            zindex=1,
            show=False,
            pixelated=False
        )
        img.add_to(m)
        control.add_child(img)

    wind_layer_control = folium.LayerControl(collapsed=True, name='Wind Data')
    for wind_image_file in wind_image_files:
        wind_image_path = os.path.join(wind_image_folder, wind_image_file)
        add_image_to_map(wind_image_path, wind_image_file, wind_layer_control)

    m.add_child(wind_layer_control)

    html = """
                <div class="floating-icon">
                    <a href="mapa_chuva.html" target="_blank"><i class="fa fa-info-circle fa-2x" style="color:green;"></i></a>
                </div>
            """

    css = """
            <style>
            .floating-icon {
                position: fixed;
                bottom: 20px;
                right: 20px;
                z-index: 1000; /* Ensure it's above other elements */
            }
            </style>
        """
    m.get_root().html.add_child(folium.Element(html))
    m.get_root().html.add_child(folium.Element(css))

def wind_map_gen(dados_coordenada, dados_ocorrencia):
    icon_energy = r'D:\Data_Science_Test\icones\Energy-icon-blue.png'
    icon_tree = r'D:\Data_Science_Test\icones\tree-icon.png'

    map_center = [dados_coordenada['latitude'].mean(), dados_coordenada['longitude'].mean()]
    m = folium.Map(location=map_center, zoom_start=6, min_zoom=6, max_zoom=18)

    fg1 = folium.FeatureGroup(name='Unidades Consumidoras')
    for i, row in dados_coordenada.iterrows():
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=(
                f"CEP: {row['CEP']}<br>"
                f"CONJ: {row['CONJ']}<br>"
            ),
            icon=folium.CustomIcon(icon_energy, icon_size=(30,30))
        ).add_to(fg1)
    fg1.add_to(m)

    fg2 = folium.FeatureGroup(name='Quedas de Árvores')
    for i, row in dados_ocorrencia.iterrows():
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=(
                f"SubPrefeitura: {row['Nome_Bairro']}<br>"
                f"Data: {row['Data']}<br>"
                f"Coordenadas: {[row['Latitude'], row['Longitude']]}"
            ),
            icon=folium.CustomIcon(icon_tree, icon_size=(30,30))
        ).add_to(fg2)
    fg2.add_to(m)

    add_wind_map_layer(m)

    m.save('mapa_vento.html')
