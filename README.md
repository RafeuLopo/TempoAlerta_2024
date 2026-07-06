# Tempo & Alerta
Um projeto completo de engenharia de dados e machine learning para analisar, correlacionar e prever interrupções no fornecimento de energia elétrica na cidade de São Paulo com base em condições meteorológicas.

# O Problema e a Solução
Este projeto nasceu da necessidade de entender e mitigar os impactos das condições climáticas extremas na rede elétrica. A proposta de solução foi dividida em três pilares principais:

Construção de um Data Lake: Coleta de dados de localização de quedas de árvores, dados meteorológicos (INMET, ERA5, Meteomatics) e unidades consumidoras de energia.

Análise de Dados: Correlação entre interrupções de energia, condições climáticas e as principais causas registradas (ex: falhas de equipamento, ventos, vegetação).

Previsão e Alerta: Construção de um modelo de Machine Learning, uma API Rest para integração e uma interface gráfica (Dashboard e Web App) para apontamento de possíveis áreas de risco.

# Arquitetura e Tecnologias
Para não reinventar a roda e otimizar os recursos disponíveis, a arquitetura foi desenhada com as seguintes ferramentas:

ClickUp: Gerenciamento e integração dos stakeholders.

Azure Blob Storage: Hospedagem e construção das camadas do Data Lake.

Python: Extração, Tratamento de Dados (ETL) e modelagem de Machine Learning.

PowerBI: Dashboard interativo para visualização dos dados.

Streamlit: Interface web gráfica e simplificada para o usuário final.

Render: Hospedagem segura da API Rest (Flask).

# Estrutura do Data Lake
Os scripts desenvolvidos (como minsait_datalake_extraction.py e raw_data_processor.py) orquestram a movimentação dos dados através de quatro camadas principais no Azure Blob Storage:

Camada Raw (Dados Brutos): Arquivos nos formatos originais (.shp, .kmz, .nc).

Camada Bronze: Dados convertidos para .csv, com renomeação de colunas e ajustes de tipos de dados. Dados originalmente pesados em .csv entram direto aqui.

Camada Silver: Dados devidamente limpos, padronizados e salvos em formato .parquet para preservação de tipagem e otimização de leitura.

Camada Gold: Dados agregados e prontos para consumo pelos modelos, dashboards e API.

# Análise e Modelo de Machine Learning
Ao realizar a análise exploratória, um insight crucial surgiu: a correlação entre chuva/vento e queda de energia não é sempre direta. A principal causa física costuma ser a falha de material/equipamento, que é agravada pelo vento e pela chuva (ex: galhos balançando e atingindo a fiação).

Com base nisso (e analisando a Escala de Beaufort para ventos), o modelo preditivo foi construído (minsait_model_v7.py):

Algoritmo: RandomForestClassifier.

Entradas: Velocidade do Vento (km/h) e Chuva (mm).

Saída: Classificação do risco baseado no número de interrupções esperadas (1-5, 6-15, 15+).

Métrica de Avaliação: Priorização do Recall. Em um contexto de segurança energética, minimizar falsos negativos (não prever um risco real) é mais crítico do que a acurácia geral, que oscilou na casa dos 70%.

# Aplicações e Interfaces
1. Interface Web (Streamlit)
O app (minsait_streamlit_app_azure.py) possui três abas principais:

Previsão de Risco: Integração com a API do Meteomatics. O usuário insere um intervalo de horas (ex: previsão para as próximas 24h), o modelo processa os dados meteorológicos esperados e exibe um mapa folium com marcação de áreas de risco em distritos mapeados (Vila Mariana, Butantã, Pinheiros).

PowerBI: Visualização nativa do Dashboard com panoramas gerais (causas de quedas, locais, vulnerabilidades).

ERA5: Visualização de mapas de calor históricos (precipitação e vento) gerados pelo script plot.py e minsait_era_plot.py.

2. API Rest (Flask)
Hospedada no Render (app_azure.py), fornece endpoints para consulta dos dados da Camada Gold:

GET /interrupcoes: Filtra interrupções por data de início/fim e localização.

GET /estacoes: Retorna dados meteorológicos por intervalo de tempo e estação.

GET /dados_agregados: Cruza e retorna os agregados de clima e quantidade de interrupções.

# Organização dos Scripts no Repositório
azure_functions.py: Módulo para download e upload no Azure Blob Storage.

raw_data_processor.py / processor_test.py: Funções auxiliares para extração de kml, conversão de shapefiles (.shp) e netCDF (.nc).

minsait_datalake_extraction.py: Pipeline principal de ETL (Raw -> Bronze -> Silver -> Gold).

plot.py / minsait_era_plot.py: Módulos para geração de gráficos geoespaciais baseados em arquivos .nc.

minsait_model_v7.py: Script de treinamento, teste e exportação do modelo RandomForestClassifier.

app_azure.py: Script da API Flask.

minsait_streamlit_app_azure.py: Script do frontend em Streamlit.

# Desafios e Considerações Finais
Executar um projeto de ponta a ponta (arquitetura, ETL, modelagem e deploy) traz grandes aprendizados. Algumas limitações enfrentadas incluíram:

Qualidade e Frequência dos Dados: Dados abertos de meteorologia (INMET) possuem muitos valores faltantes. Além disso, as bases públicas de interrupção não são atualizadas em tempo real (frequência mensal), dificultando um sistema de alerta "live" perfeito.

Limitações de Hardware e Custos: Para preservar os créditos do Azure, a orquestração do pipeline de dados foi mantida em scripts Python locais ao invés de ferramentas mais robustas (e custosas) como Azure Data Factory + Databricks. Limitações de hardware também impediram o uso de modelos Ensemble mais complexos e deep tuning de hiperparâmetros.
