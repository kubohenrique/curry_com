import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Home",
    page_icon="🛵"
)

image = Image.open('logo.png')
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.write('# Curry Company Growth Dashboard')

st.markdown(
    """
    Growth Dashboard foi construído para acompanhar as métricas de crescimento dos entregadores e restaurantes.
    ### Como utilizar esse Dashboard?
    - Visão Empresa:
        - Visão Gerencial: Métricas gerais de comportamento.
        - Visão Tática: Indicadores de crescimento.
        - Visão geográfica: Insights de geolocalização.
    - Visão entregador:
        - Acompnahamento dos indicadores semanais de crescimento.
    - Visão Restaurantes:
        - Indicadores semanais de crescimento dos restaurantes.
    ### Ask for Help
    - Henrique Kubo
        - @kubohenrique
    """
)