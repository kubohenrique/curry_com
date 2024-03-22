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

st.set_page_config(page_title='Visão Empresa', page_icon='📈', layout='wide')

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
def pedidos_dia(df1):
    df_aux = df1.loc[:, ['ID', 'Order_Date']].groupby('Order_Date').count().reset_index()
    fig = px.bar(df_aux, x='Order_Date', y='ID')
    return fig
# ---------------------------------------------------------------------------------------------------------------------------------
def pedido_trafego(df1):
    cols = ['ID', 'Road_traffic_density']
    df1 = df1.loc[df1['Road_traffic_density'] != 'NaN',:]
    df_aux = df1.loc[:, cols].groupby('Road_traffic_density').count().reset_index()
    df_aux['percentage'] = df_aux['ID'] / df_aux['ID'].sum()
    fig2 = px.pie(df_aux, values='percentage', names='Road_traffic_density')
    return fig2
# ---------------------------------------------------------------------------------------------------------------------------------
def trafego_cidade(df1):
    df1 = df1.loc[df1['Road_traffic_density'] != 'NaN',:]
    df1 = df1.loc[df1['City'] != 'NaN',:]
    df_aux = df1.loc[:, ['ID', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).count().reset_index()
    fig3 = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID', color='City')
    return fig3
# ---------------------------------------------------------------------------------------------------------------------------------
def vendas_semana(df1):
    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
    cols = ['ID', 'week_of_year']
    df_aux = df1.loc[:, cols].groupby('week_of_year').count().reset_index()
    fig5 = px.line(df_aux, x='week_of_year', y='ID')
    return fig5
# ---------------------------------------------------------------------------------------------------------------------------------
def entregador_semana(df1):
    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
    df_aux1 = df1.loc[:,['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
    df_aux2 = df1.loc[:,['Delivery_person_ID', 'week_of_year']].groupby('week_of_year').nunique().reset_index()
    df_aux = pd.merge(df_aux1, df_aux2, how = 'inner')
    df_aux['order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    fig4 = px.line(df_aux, x='week_of_year', y='order_by_deliver')
    return fig4
# ---------------------------------------------------------------------------------------------------------------------------------
def mapa_india(df1):
    df1 = df1.loc[df1['Road_traffic_density'] != 'NaN',:]
    df1 = df1.loc[df1['City'] != 'NaN',:]

    df_aux = df1.loc[:,['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']].groupby(['City', 'Road_traffic_density']).median().reset_index()

    map = folium.Map()

    for index, location_info in df_aux.iterrows():
        folium.Marker([location_info['Delivery_location_latitude'],
                        location_info['Delivery_location_longitude']],
                        popup = location_info[['City', 'Road_traffic_density']]).add_to(map)
    
    folium_static( map, width=1024, height=600)

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
st.header('Market Place - Visão Empresa')

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
st.sidebar.markdown('#### Feito por Henrique Kubo')

# Filtro de Data
linhas_selecionadas = df1['Order_Date'] < data_slider
df1 = df1.loc[linhas_selecionadas, :]

# Filtro de Tráfego
linhas_selecionadas = df1['Road_traffic_density'].isin(data_select)
df1 = df1.loc[linhas_selecionadas, :]

# =====================================================================================
#                           LAYOUT STREAMNLIT
# =====================================================================================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial','Visão Tática','Visão Geográfica'])

with tab1:
    with st.container():
        fig = pedidos_dia(df1)
        st.markdown('# Pedidos por Dia')
        st.plotly_chart(fig, use_container_width=True)
    
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            fig2 = pedido_trafego(df1)
            st.markdown('# Pedidos por Tráfego')
            st.plotly_chart(fig2, use_container_width=True)
                   
        with col2:
            fig3 = trafego_cidade(df1)
            st.markdown('# Tráfego por Cidade')
            st.plotly_chart(fig3, use_container_width=True)
      
with tab2:
    
    with st.container():
        fig5 = vendas_semana(df1)
        st.markdown('# Vendas por Semana')
        st.plotly_chart(fig5, use_container_width=True)

    with st.container():
        fig4 = entregador_semana(df1)
        st.markdown('# Pedidos por Entregador/Semana')
        st.plotly_chart(fig4, use_container_width=True)


with tab3:
    st.markdown('# Localização Central Cidade por Tráfego')
    mapa_india(df1)