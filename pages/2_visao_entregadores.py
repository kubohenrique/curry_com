# ===========================================================================================
#                                       BIBLIOTECA
# ===========================================================================================

import pandas as pd
import plotly.express as px
import folium
import streamlit as st
import datetime

from haversine import haversine
from PIL import Image
from streamlit_folium import folium_static

st.set_page_config(page_title='Visão Entregadores', page_icon='🚚', layout='wide')

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
def avaliacao(df1, col ):
    df1_traffic = df1.loc[:,[col, 'Delivery_person_Ratings']].groupby(col).agg({'Delivery_person_Ratings':['mean', 'std']})
    df1_traffic.columns = ['delivery_mean', 'delivery_std']
    media_transito = df1_traffic.reset_index()
    return media_transito
# ---------------------------------------------------------------------------------------------------------------------------------
def top_entrega(df1, top_ordem):
    df2 = df1.loc[:, ['City', 'Delivery_person_ID','Time_taken(min)']].groupby(['City', 'Delivery_person_ID']).max().sort_values(['City', 'Time_taken(min)'], ascending=top_ordem).reset_index()
    aux01 = df2.loc[df2['City'] == 'Urban', :].head(10)
    aux02 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
    aux03 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)
    df3 = pd.concat([aux01, aux02, aux03]).reset_index(drop=True)
    return df3

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

        col1, col2, col3, col4 = st.columns(4, gap='medium')
        with col1:
            maior_idade = df1.loc[:,'Delivery_person_Age'].max()
            col1.metric('Maior Idade', maior_idade)

        with col2:
            menor_idade = df1.loc[:,'Delivery_person_Age'].min()
            col2.metric('Menor Idade', menor_idade)

        with col3:
            melhor_condicao = df1.loc[:,'Vehicle_condition'].max()
            col3.metric('A melhor Condição', melhor_condicao)
           
        with col4:
             pior_condicao = df1.loc[:,'Vehicle_condition'].min()
             col4.metric('A pior Condição', pior_condicao)

    with st.container():
        st.markdown('---')
        st.title('Avaliações')

        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Avaliação média por Entregador')
            avg_deliver = df1.loc[:,['Delivery_person_ID', 'Delivery_person_Ratings']].groupby('Delivery_person_ID').mean().reset_index()
            st.dataframe(avg_deliver)

        with col2:
            st.markdown('##### Avaliação média por Trânsito')
            media_transito = avaliacao(df1,col= 'Road_traffic_density' )
            st.dataframe(media_transito)

            st.markdown('##### Avaliação média por Clima')
            media_transito = avaliacao(df1,col= 'Weatherconditions' )
            st.dataframe(media_transito)
    
    with st.container():
        st.markdown('---')
        st.title('Velocidade de Entrega')

        col1, col2 = st.columns(2)
        with col1:
            df3 = top_entrega(df1, top_ordem=True)
            st.markdown('##### Top Entregadores Mais Rápidos')
            st.dataframe(df3)
            
        with col2:
            df3 = top_entrega(df1, top_ordem=False)
            st.markdown('##### Top Entregadores Mais Lerdos')
            st.dataframe(df3)