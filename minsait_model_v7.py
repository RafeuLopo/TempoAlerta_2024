# %%
import pandas as pd
from sklearn.ensemble import IsolationForest
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import IsolationForest
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from sklearn.metrics import f1_score, precision_recall_curve, auc, roc_auc_score
from sklearn.model_selection import GridSearchCV
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix

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

df = merged_df

df['DataHora'] = pd.to_datetime(df['DataHora'])

df = df.dropna(subset=['Vel. Vento (m/s)'])
df['Chuva (mm)'] = df['Chuva (mm)'].fillna(0)
df = df[['DataHora', 'Vel. Vento (m/s)', 'Vento', 'Chuva (mm)', 'Umi. Ins. (%)', 'Árvore', 'Falha no Equipamento', 'Total_Interrupcoes']]

# %%
df = df[df['Vel. Vento (m/s)'] != 0.0]

df['Data'] = df['DataHora'].dt.date

df['Vento_kmh'] = df['Vel. Vento (m/s)'] * 3.6
df.drop(columns='Vel. Vento (m/s)')

df_agrupado = df.groupby('Data').agg({
    'Vento': 'sum',
    'Vento_kmh': 'max',
    'Chuva (mm)': 'max',
    'Umi. Ins. (%)': 'max',
    'Árvore': 'sum',
    'Falha no Equipamento': 'sum',
    'Total_Interrupcoes': 'sum'
}).reset_index()

df_agrupado['Data'] = pd.to_datetime(df_agrupado['Data'])

df_agrupado.info()

# %%
df_agrupado['Interrupcoes_Grupo'] = pd.cut(df_agrupado['Total_Interrupcoes'], 
                                  bins=[-0.1, 1, 5, 15, float('inf')],
                                  labels=['0', '1-5', '6-15', '15+'])

# %%
df_agrupado['Interrupcoes_Grupo'].value_counts()

# %%
df_agrupado.sort_values(by='Interrupcoes_Grupo')

# %%
df_agrupado.drop(columns=['Vento', 'Árvore', 'Falha no Equipamento', 'Total_Interrupcoes'], inplace=True)

# %%
'''
Verificar depois se precisa tirar o 0!
'''
df_agrupado = df_agrupado[df_agrupado['Interrupcoes_Grupo'] != '0']

# %%
df_agrupado = df_agrupado[
    (df_agrupado['Vento_kmh'] >= 5) | 
    ((df_agrupado['Vento_kmh'] < 5) & (df_agrupado['Chuva (mm)'] > 30))
]

# %%
df_agrupado.info()

# %%
from sklearn.preprocessing import LabelEncoder

le = LabelEncoder()

df_agrupado['Interrupcoes_Grupo_Encoded'] = le.fit_transform(df_agrupado['Interrupcoes_Grupo'])

# %%
df_agrupado.info()

# %%
df_agrupado.head()

# %%
mapping = df_agrupado[['Interrupcoes_Grupo', 'Interrupcoes_Grupo_Encoded']].drop_duplicates().reset_index(drop=True)

# %%
import matplotlib.pyplot as plt
import seaborn as sns

_ = sns.heatmap(df_agrupado.drop(columns=['Data', 'Interrupcoes_Grupo']).corr(method='pearson'), vmin=-1, vmax=1, annot=True)

# %%
X = df_agrupado.drop(columns=['Data', 'Interrupcoes_Grupo', 'Interrupcoes_Grupo_Encoded'])
y = df_agrupado['Interrupcoes_Grupo']

# %%
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)

# %%
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

param_grid = {
    'n_estimators': [100, 200],
    'max_depth': [3, 6, 9]
}

rf = RandomForestClassifier(class_weight='balanced', random_state=42)

grid_search = GridSearchCV(estimator=rf, param_grid=param_grid, scoring='recall_micro', cv=5)
grid_search.fit(X_train, y_train)

print(f"Best parameters: {grid_search.best_params_}")
print(f"Best score: {grid_search.best_score_}")

best_params = grid_search.best_params_
best_rf = RandomForestClassifier(**best_params)
best_rf.fit(X_train, y_train)

y_pred = best_rf.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, average='micro')
recall = recall_score(y_test, y_pred, average='micro')
f1 = f1_score(y_test, y_pred, average='micro')

y_proba = best_rf.predict_proba(X_test)

roc_auc = roc_auc_score(y_test, y_proba, multi_class='ovr', average='micro')

print(f"Accuracy: {accuracy}")
print(f"Precision: {precision}")
print(f"Recall: {recall}")
print(f"F1 Score: {f1}")
print(f"ROC AUC: {roc_auc}")

cm = confusion_matrix(y_test, y_pred)

plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
plt.ylabel('True Label')
plt.title('Confusion Matrix')
plt.show()

# %%
import pickle
model_pkl_file = "Anomaly_Detection_Challenge_4.pkl"  

with open(model_pkl_file, 'wb') as file:  
    pickle.dump(best_rf, file)

# %%
