# Libraries
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import plotly.colors
import datetime

# bibliotecas necessárias
import folium
import pandas as pd
import streamlit as st
from PIL import Image

from streamlit_folium import folium_static

st.set_page_config( page_title = 'Visão Empresa', layout = 'wide')

                        #Funções 
#-------------------------------------------------------------#


def clean_code( df1 ):
    """ Está função tem a resposabilidade de limpar o dataframe 
    
        Tipos de limpeza:
        1. Remoção dos dados NaN
        2. Mundança do tipo de coluna de dados
        3. Remoção dos espaços das variáveis de texto
        4. Formatação da coluna de datas 
        5. Limpeza da coluna de tempo ( remoção de texto da variável númerica )
    
    
        Input: DataFrame
        Output: DataFrame
    
    """
    
    linhas_vazias = df['Delivery_person_Age'] != 'NaN '
    df1 = df1.loc[linhas_vazias, :]

    linhas_vazias2 = df['City'] != 'NaN '
    df1 = df1.loc[linhas_vazias2, :]

    linhas_vazias3 = df['multiple_deliveries'] != 'NaN '
    df1 = df1.loc[linhas_vazias3, :]

    linhas_vazias4 = df['Road_traffic_density'] != 'NaN '
    df1 = df1.loc[linhas_vazias4, :]

    linhas_vazias5 = df['Festival'] != 'NaN '
    df1 = df1.loc[linhas_vazias5, :]

    
    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Delivery_person_ID'] = df1.loc[:, 'Delivery_person_ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()

    

    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)

    df1['Order_Date'] = pd.to_datetime( df['Order_Date'], format='%d-%m-%Y' )

    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: x.split('(min)')[1])

    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)

    df1 = df1.reset_index( drop=True )
    
    
    return df1
#-------------------------------------------------------------#

def order_metric( df1 ):
        
    cols = ['ID', 'Order_Date']


    df_aux = df1.loc[:, cols].groupby('Order_Date').count().reset_index()

    df_aux.head()

   
    fig =px.bar(df_aux, x='Order_Date', y='ID')
        
    return fig
#-------------------------------------------------------------#

def traffic_order_share(df1):
    df_aux = df1.loc[:, ['ID', 'Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()
    df_aux['entregas_percent'] = df_aux['ID'] / df_aux['ID'].sum()

    # Define as cores para cada fatia do gráfico
    colors = plotly.colors.qualitative.Plotly

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_aux['Road_traffic_density'],
        y=df_aux['ID'],
        text=df_aux['entregas_percent'].apply(lambda x: f"{x:.1%}"), # Formata o texto com a porcentagem de entregas
        textposition='auto',
        marker_color=colors
    ))
    fig.update_layout(
        xaxis_title='Nível de tráfego',
        yaxis_title='Número de entregas',
        showlegend=False,
        uniformtext_minsize=10,
        uniformtext_mode='hide'
    )
    return fig
#-------------------------------------------------------------#

def traffic_orde_city( df1 ):
        
    df_aux = (df1.loc[:, ['ID','City','Road_traffic_density']]
                      .groupby(['City','Road_traffic_density' ])
                      .count()
                      .reset_index())      
    
    colors = plotly.colors.qualitative.Plotly
    fig = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID', color= 'City')
    
        
    return fig 
#-------------------------------------------------------------#          
    
def order_by_week( df1 ):
    
    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')

    df_aux = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()

    df_aux
    fig = px.line(df_aux, x='week_of_year', y='ID')

    return fig 
#-------------------------------------------------------------#

def order_share_by_week ( df1 ):
        
    df_aux01 = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
    df_aux02 = df1.loc[:,['Delivery_person_ID', 'week_of_year']].groupby('week_of_year').nunique().reset_index()

    df_aux = pd.merge(df_aux01,df_aux02, how='inner')
    df_aux['order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']

    df_aux

    fig = px.line(df_aux, x='week_of_year', y='order_by_deliver')

    return fig

#-------------------------------------------------------------#

def country_maps( df1 ):
    
    df_aux = (df1.loc[:, ['City','Road_traffic_density', 'Delivery_location_latitude','Delivery_location_longitude' ]]
                  .groupby(['City', 'Road_traffic_density'])
                  .median()
                  .reset_index())

    mapa = folium.Map()

    for index, location_info in df_aux.iterrows():
        folium.Marker([location_info['Delivery_location_latitude'], 
                       location_info['Delivery_location_longitude']],
                          popup=location_info[['City', 'Road_traffic_density']]).add_to(mapa)

    folium_static(mapa, width=1024, height=600)

    


        
        #Inicio da Estrutura lógica do código 
#-------------------------------------------------------------#


#------------ Importar o arquivo------------------------------#  

df = pd.read_csv('train.csv')

#------------- Limpar o dataframe ----------------------------#

df1 = clean_code( df )

                    # SIDEBAR
#-------------------------------------------------------------#


# image_path = '/Users/dinizjp/Programação /Repos_DS/Ciclo FTC/Codigos/Cury_company_1.0/logo1.png'
image = Image.open('logo1.png')
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.sidebar.markdown('## Selecione uma data limite')

data_slider = st.sidebar.slider(
    'Até qual valor?',
    value=datetime.datetime(2022, 4, 13),
    min_value=datetime.datetime(2022, 2, 11),
    max_value=datetime.datetime(2022, 4, 6),
    format='DD-MM-YYYY')


st.sidebar.markdown("""---""")


traffic_options = st.sidebar.multiselect(
    'Quais as condições de trânsito',
    ['Low', 'Medium', 'High', 'Jam'],
    default= ['Low', 'Medium', 'High', 'Jam']
)
st.sidebar.markdown("""---""")
st.sidebar.markdown('### Powered by Comunidade DS')

#Filtro de data 
linhas_selecionadas = df1['Order_Date'] < data_slider

df1 = df1.loc[linhas_selecionadas,:]

#Filtro de transito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)

df1 = df1.loc[linhas_selecionadas,:]



#-------------------------------------------------------------#
#Layout no Streamlit 
#-------------------------------------------------------------#

st.header('Marketplace - Visão Empresa')


                   #Cria abas 
#-------------------------------------------------------------#
 
tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])


                   #ABA 1
#-------------------------------------------------------------#

with tab1:
    with st.container():
        
        st.markdown('# Quantidade de pedidos por dia')
        
        fig = order_metric( df1 )
        
        st.plotly_chart(fig, use_container_width=True)
        
        
        

    with st.container():
        col1, col2 = st.columns(2)
        
       
    with col1:
        
        st.markdown('# Distribuição dos pedidos por tipo de tráfego.')
        fig = traffic_order_share ( df1 ) 
        st.plotly_chart(fig, use_container_width=True)
        
    
        
    with col2:
        st.markdown('# Comparação do volume de pedidos por cidade e tipo de tráfego.')
        fig = traffic_orde_city ( df1)
        st.plotly_chart(fig, use_container_width=True)
        
           
            
                   #ABA 2
#-------------------------------------------------------------#           
            
with tab2:
    with st.container():
        st.markdown('# Quantidade de pedidos por semana.')
        fig = order_by_week ( df1 )
        st.plotly_chart(fig, use_container_width=True)
         
            
        
    
    with st.container():
        st.markdown('# A quantidade de pedidos por entregador por semana')
        fig = order_share_by_week ( df1 )
        st.plotly_chart(fig, use_container_width=True)
        
        
       
                   #ABA 3
#-------------------------------------------------------------#
    
with tab3:
    
    st.markdown('# A localização central de cada cidade por tipo de tráfego.')
    country_maps ( df1 )
    
