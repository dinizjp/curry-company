# Libraries
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import datetime
import numpy as np

# bibliotecas necessárias
import pandas as pd
import streamlit as st
from PIL import Image

st.set_page_config( page_title = 'Visão Restaurantes', layout = 'wide')

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
    
    
    
    df1 = df1.rename(columns={'ID':'ID', 
                          'Delivery_person_ID':'ID do entregador',
                          'Delivery_person_Age':'Idade do entregador',
                          'Delivery_person_Ratings':'Avaliação por entregador',
                          'Restaurant_latitude':'Latitude do restaurante',
                          'Restaurant_longitude':'Longitude do restaurante',
                          'Delivery_location_latitude':'Latitude da entrega',
                          'Delivery_location_longitude':'Longitude da entrega',
                          'Order_Date':'Data do pedido',
                          'Time_Orderd':'Hora do pedido',
                          'Time_Order_picked':'Hora que foi recolhido',
                          'Weatherconditions':'Condições climáticas',
                          'Road_traffic_density':'Intensidade do trânsito',
                          'Vehicle_condition':'Condição do veículo',
                          'Type_of_order':'Tipo de pedido',
                          'Type_of_vehicle':'Veículo',
                          'multiple_deliveries':'Multiplos deliverys',
                          'Festival':'Festival',
                          'City':'Tipo de cidade',
                          'Time_taken(min)':'Tempo da entrega',})

    return df1
#-------------------------------------------------------------#


def distance( df1 ):
        
    df1['Distância'] = (df1[['Latitude do restaurante', 'Longitude do restaurante',
        'Latitude da entrega','Longitude da entrega']]
        .apply(lambda x: haversine((x['Latitude do restaurante'], x['Longitude do restaurante'])
         ,(x['Latitude da entrega'], x['Longitude da entrega'])), axis=1).round(2))

    distancia_media = df1['Distância'].mean().round(2)
        
    return distancia_media
#-------------------------------------------------------------#

def mean_std_time_delivery( df1, festival, op ):
        '''
        Está função calcula o tempo medio e desvio padrao do tempo de entrega 
        Parâmetros: 
            input:
                 - df: DataFrame com os dados necessários para o cálculo 
                 - ps: Tipo de operação que precisa ser calculada
                     'mean_time' or 'std_time'
                 - festival: Se é com ou sem festival 
                      'Yes' or 'No'
                 
                 
             output: DataFrame         
        
        '''
        df_aux = (df1[['Tempo da entrega', 'Festival']].groupby('Festival')
              .agg({'Tempo da entrega' : ['mean','std']}).round(2))

        df_aux.columns = ['mean_time', 'std_time']
        df_aux = df_aux.reset_index()
        df_aux = df_aux.loc[df_aux['Festival'] == festival , op]
        
        return df_aux

#-------------------------------------------------------------#
    
def mean_std_time_graph( df1 ):
  
    st.markdown('## Tempo médio e desvio padrão das entregas por cidade ')
    df_aux = (df1[['Tipo de cidade', 'Tempo da entrega']].groupby('Tipo de cidade')
              .agg({'Tempo da entrega' : ['mean','std']}).round(2))

    df_aux.columns = ['Tempo médio', 'Desvio Padrão']

    df_aux = df_aux.reset_index()

    st.dataframe(df_aux, width=1100, height=142)

    fig = go.Figure()
    fig.add_trace( go.Bar( name='Control', x= df_aux['Tipo de cidade'], y=df_aux['Tempo médio'], 
                          error_y=dict(type='data', array=df_aux['Desvio Padrão'])))

    fig.update_layout(barmode='group', width=1000, height=600,
                          yaxis_title='Tempo médio', xaxis_title='Tipo de cidade')
    return fig 

 
    
#-------------------------------------------------------------#
def mean_std_city_order( df1 ):
    
    st.markdown("""---""")
    st.markdown('## O tempo médio e o desvio padrão de entrega por cidade e tipo de pedido')

    df_aux = (df1[['Tipo de cidade', 'Tempo da entrega', 'Tipo de pedido']]
              .groupby(['Tipo de cidade','Tipo de pedido'])
              .agg({'Tempo da entrega' : ['mean','std']})
              .round(2))
    df_aux.columns = ['Tempo Médio', 'Desvio Padrão']
    df_aux = df_aux.reset_index()

    return df_aux 
#-------------------------------------------------------------#

def mean_std_city_traffic ( df1 ):
    
    st.markdown('## O tempo médio e o desvio padrão de entrega por cidade e tipo de tráfego. ')
    df_aux = (df1[['Tipo de cidade', 'Tempo da entrega', 'Intensidade do trânsito']]
                  .groupby(['Tipo de cidade','Intensidade do trânsito'])
                  .agg({'Tempo da entrega' : ['mean','std']}).round(2))


    df_aux.columns = ['Tempo Médio', 'Desvio Padrão']

    df_aux = df_aux.reset_index()
        
    return df_aux


def mean_std_festival ( df1 ):
    
    st.markdown('## O tempo médio de entrega durantes os Festivais.')
    df_aux = (df1[['Tempo da entrega', 'Festival']].groupby('Festival')
              .agg({'Tempo da entrega' : ['mean','std']}).round(2))

    df_aux.columns = ['mean_time', 'std_time']

    df_aux =df_aux.reset_index()

    fig = go.Figure()
    fig.add_trace(go.Bar(name='Control', x=df_aux['Festival'], y=df_aux['mean_time'], 
                             error_y=dict(type='data', array=df_aux['std_time'])))
    fig.update_layout(barmode='group', width=1100, height=600,
                          yaxis_title='Tempo médio', xaxis_title='Festival')
        
    return fig 




    
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
linhas_selecionadas = df1['Data do pedido'] < data_slider

df1 = df1.loc[linhas_selecionadas,:]

#Filtro de transito
linhas_selecionadas = df1['Intensidade do trânsito'].isin(traffic_options)

df1 = df1.loc[linhas_selecionadas,:]


#-------------------------------------------------------------#
# Layout no Streamlit
#-------------------------------------------------------------#
st.markdown('# Visão Restaurantes')

#-------------------------------------------------------------#
st.markdown('## Métricas gerais')
    
col1, col2, col3, col4, col5, col6 = st.columns(6)
    
with col1:

    delivery_unique = len(df1['ID do entregador'].unique())
    col1.metric('Entregadores', delivery_unique)

with col2:
    
    distancia_media = distance(df1)
    col2.metric('Distância média', distancia_media) 
    
        
with col3:
    
    df_aux = mean_std_time_delivery (df1, 'Yes', 'mean_time')   
    col3.metric('Tempo médio festival', df_aux)

    
with col4:
    
    df_aux = mean_std_time_delivery (df1,'Yes', 'std_time')   
    col4.metric('Desvio padrão festival', df_aux)
        
        
with col5:
    
    df_aux = mean_std_time_delivery (df1, 'No', 'mean_time')   
    col5.metric('Tempo médio sem festival', df_aux)
        
        
with col6:
    df_aux = mean_std_time_delivery (df1, 'No', 'std_time')   
    col6.metric('Desvio padrão sem festival', df_aux)

#-------------------------------------------------------------#  
    
with st.container():
    st.markdown("""---""")
    fig = mean_std_time_graph(df1)
    st.plotly_chart (fig)
   
    
#-------------------------------------------------------------#    

with st.container():
    df_aux = mean_std_city_order (df1)
    st.dataframe(df_aux, width=1100, height=458)
    

    
    
with st.container():   
    st.markdown("""---""")
    df_aux = mean_std_city_traffic( df1 )
    st.dataframe(df_aux, width=1100, height=422)
    
    
with st.container():
    st.markdown("""---""")
    fig = mean_std_festival (df1)
    st.plotly_chart(fig)
    