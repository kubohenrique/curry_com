# ===========================================================================================
#                                       BIBLIOTECA
# ===========================================================================================

import pandas as pd
import plotly.express as px
import folium
import streamlit as st
import datetime
import numpy as np
import plotly.graph_objects as go

from haversine import haversine
from PIL import Image
from streamlit_folium import folium_static

st.set_page_config(page_title='Visão Restaurante', page_icon='🍽️', layout='wide')

# ===========================================================================================
#                                       FUNÇÕES
# ===========================================================================================

def clean_code(df):

    """ Esta função tem a responsabilidade fazer a limpeza do dataframe
         Tipos de Limpeza:
         1. Remoção de NaN
         2. Mudança de Tipos de Dados
         3. Remoção dos espacos das variáveis texto
         4. Formatação da coluna de datas
         5. Limpeza da coluna tempo (Remoção do texto da variável numérica)
    """
    df.loc[:, 'ID'] = df.loc[:, 'ID'].str.strip()
    df.loc[:, 'Delivery_person_ID'] = df.loc[:, 'Delivery_person_ID'].str.strip()
    df.loc[:, 'Road_traffic_density'] = df.loc[:, 'Road_traffic_density'].str.strip()
    df.loc[:, 'Type_of_order'] = df.loc[:, 'Type_of_order'].str.strip()
    df.loc[:, 'City'] = df.loc[:, 'City'].str.strip()
    df.loc[:, 'Festival'] = df.loc[:, 'Festival'].str.strip()


    linhas_vazias = df['Delivery_person_Age'] != 'NaN '
    df = df.loc[linhas_vazias, :]

    df['Delivery_person_Age'] = df['Delivery_person_Age'].astype( int )

    df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].astype( float )

    df['Order_Date'] = pd.to_datetime( df['Order_Date'], format='%d-%m-%Y' )

    linhas_vazias = df['multiple_deliveries'] != 'NaN '
    df = df.loc[linhas_vazias, :]
    df['multiple_deliveries'] = df['multiple_deliveries'].astype( int )

    linhas_vazias = df['Road_traffic_density'] != 'NaN '
    df = df.loc[linhas_vazias, :]

    linhas_vazias = df['City'] != 'NaN'
    df = df.loc[linhas_vazias, :]

    linhas_vazias = df['Road_traffic_density'] != 'NaN'
    df = df.loc[linhas_vazias, :]

    linhas_vazias = df['Festival'] != 'NaN'
    df = df.loc[linhas_vazias, :]

    df['Time_taken(min)'] = df['Time_taken(min)'].apply(lambda x:x.split('(min) ')[1])
    df['Time_taken(min)'] = df['Time_taken(min)'].astype(int)

    return df
# ---------------------------------------------------------------------------------------------------------------------------------

def distancia_media(df1):
    cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
    df1['distance'] = df1.loc[:,cols ].apply(lambda x: 
                                              haversine((x['Restaurant_latitude'], x['Restaurant_longitude']), 
                                                        (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)
    a = np.round(df1['distance'].mean(),2)
    return a
# ---------------------------------------------------------------------------------------------------------------------------------
def aux_coisa(df1, festival, operacao):
    """ df1 = Dataset
        festival = 'Yes' | 'No''
        operacao = 'avg_time' | 'std_time'
    """
    df_aux = (df1.loc[:, ['Time_taken(min)', 'Festival']]
                 .groupby('Festival')
                 .agg({'Time_taken(min)' : ['mean', 'std']}))
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    df_aux = np.round(df_aux.loc[df_aux['Festival'] == festival, operacao])
    return df_aux
# ---------------------------------------------------------------------------------------------------------------------------------
def grafico(df1):
    cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
    df1['distance'] = df1.loc[:,cols ].apply(lambda x: 
                                                     haversine((x['Restaurant_latitude'], x['Restaurant_longitude']), 
                                                               (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)
        
    avg_distance = df1.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()
    fig = go.Figure(data=[go.Pie(labels=avg_distance['City'], values=avg_distance['distance'], pull=[0, 0.1, 0] )])
    return fig

# ---------------------------------------------------------------------------------------------------------------------------------
def tabela(df1):
    df_aux = df1.loc[:, ['City', 'Time_taken(min)']].groupby('City').agg({'Time_taken(min)': ['mean','std']})
    df_aux.columns = ['avg_time', 'std_time']
    df_aux.reset_index()
    return df_aux

# ===========================================================================================
#                               INICIO DA ESTRUTURA LÓGICA
# ===========================================================================================

# Importando o Data set

df_r = pd.read_csv('dataset/train.csv')
df = df_r.copy()

# Limpeza dos dados

df = clean_code(df)

# cópia do código

df1 = df.copy()

# =====================================================================================
#                           BARRA LATERAL
# =====================================================================================
st.header('Market Place - Visão Entregadores')

image = Image.open('logo.png')
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.sidebar.markdown('## Selecione uma data Limite')

data_slider = st.sidebar.slider(
    'Até qual valor ?',
    value=datetime.datetime(2022,2,13),
    min_value=datetime.datetime(2022,2,11),
    max_value=datetime.datetime(2022,4,6),
    format='DD-MM-YYYY') 

st.sidebar.markdown("""---""")

data_select = st.sidebar.multiselect(
    'Quais as condições do trânsito ?',
    ['Low', 'Medium', 'High', 'Jam'],
    default= ['Low', 'Medium', 'High', 'Jam'])

st.sidebar.markdown("""---""")

data_selectbox = st.sidebar.multiselect(
    'Quais as condições do Tempo ?',
    ['conditions Sunny', 'conditions Stormy', 'conditions Sandstorms','conditions Cloudy', 'conditions Fog', 'conditions Windy'],
    default= ['conditions Sunny', 'conditions Stormy', 'conditions Sandstorms','conditions Cloudy', 'conditions Fog', 'conditions Windy'])

st.sidebar.markdown("""---""")
st.sidebar.markdown('#### Feito por Henrique Kubo')

# Filtro de Data
linhas_selecionadas = df1['Order_Date'] < data_slider
df1 = df1.loc[linhas_selecionadas, :]

# Filtro de Tráfego
linhas_selecionadas = df1['Road_traffic_density'].isin(data_select)
df1 = df1.loc[linhas_selecionadas, :]

# Filtro de Tempo
linhas_selecionadas = df1['Weatherconditions'].isin(data_selectbox)
df1 = df1.loc[linhas_selecionadas, :]

# =====================================================================================
#                           LAYOUT STREAMNLIT
# =====================================================================================

tab1, tab2, tab3  = st.tabs(['Visão Gerencial', '-','-'])

with tab1:
    with st.container():
        st.title('Métricas Gerais')

        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            entregador_unico = df1['Delivery_person_ID'].nunique()
            col1.metric('Entregadores Únicos', entregador_unico)

        with col2:
            a = distancia_media(df1)
            col2.metric('Distância Média (KM)', a)

        with col3:
            df_aux = aux_coisa(df1, 'Yes', 'avg_time')
            col3.metric('Tempo médio no Festival', df_aux)
            
        with col4:
            df_aux = aux_coisa(df1, 'Yes', 'std_time')
            col4.metric('desvio médio no Festival', df_aux)
        
        with col5:
            df_aux = aux_coisa(df1, 'No', 'avg_time')
            col5.metric('Tempo médio sem Festival', df_aux)
            
        with col6:
            df_aux = aux_coisa(df1, 'No', 'std_time')
            col6.metric('desvio médio sem Festival', df_aux)

    with st.container():
        st.markdown('---')
        st.title('Tempo medio de entrega por cidade ')
        fig = grafico(df1)
        st.plotly_chart(fig)
        
    with st.container():
        st.markdown('---')
        st.title('Distribuição do Tempo')
        df_aux = tabela(df1)
        st.dataframe(df_aux)