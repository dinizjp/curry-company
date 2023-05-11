# Libraries
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import datetime

# bibliotecas necessárias
import pandas as pd
import streamlit as st
from PIL import Image


st.set_page_config( page_title = 'Visão Entregadores', layout = 'wide')


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


def top_deliverys( df1, top_asc ):
    
    df_aux = (df1[['Delivery_person_ID', 'Time_taken(min)', 'City']]
              .groupby(['Delivery_person_ID', 'City']).max()
              .sort_values(['City', 'Time_taken(min)'], ascending=top_asc)
              .reset_index())
        

    df_aux01 = df_aux.loc[df_aux['City'] == 'Metropolitian', :].head(10)
    df_aux02 = df_aux.loc[df_aux['City'] == 'Urban', :].head(10)
    df_aux03 = df_aux.loc[df_aux['City'] == 'Semi-Urban', :].head(10)

    df_aux_total = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index(drop=True)

    return df_aux_total


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

clime_options = st.sidebar.multiselect(
    'Quais as condições de Clima', 
    ['conditions Cloudy','conditions Fog','conditions Sandstorms','conditions Stormy','conditions Sunny','conditions Windy'],
    default= ['conditions Cloudy','conditions Fog','conditions Sandstorms','conditions Stormy','conditions Sunny','conditions Windy'])
    

st.sidebar.markdown("""---""")
st.sidebar.markdown('### Powered by Comunidade DS')

#Filtro de data 
linhas_selecionadas = df1['Order_Date'] < data_slider

df1 = df1.loc[linhas_selecionadas,:]

#Filtro de transito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)

df1 = df1.loc[linhas_selecionadas,:]

#Filtro de clima
linhas_selecionadas = df1['Weatherconditions'].isin(clime_options)

df1 = df1.loc[linhas_selecionadas,:]


#-------------------------------------------------------------#
#Layout no Streamlit 
#-------------------------------------------------------------#
st.markdown('# Marketplace - Visão Entregadores')



                #Primeiro container 
#-------------------------------------------------------------#

with st.container():
    st.markdown( """---""" )
    st.markdown('## Métricas Gerais')
    
    
    col1, col2, col3, col4 = st.columns( 4, gap='large' )
    with col1:
        
        # A maior idade dos entregadores
        maior_idade = df1.loc[:, 'Delivery_person_Age'].max()
        col1.metric( 'Maior de idade', maior_idade )


    with col2:
        # A menor idade dos entregadores
        menor_idade = df1.loc[:, 'Delivery_person_Age'].min()
        col2.metric( 'Menor idade', menor_idade )

    with col3:
        # A maior idade dos entregadores
        melhor_condicao = df1.loc[:, 'Vehicle_condition'].max()
        col3.metric( 'Melhor condicao', melhor_condicao )

    with col4:
        # A menor idade dos entregadores
        pior_condicao = df1.loc[:, 'Vehicle_condition'].min()
        col4.metric( 'Pior condicao', pior_condicao )


        
        
                #Segundo container 
#-------------------------------------------------------------#

with st.container():
    st.sidebar.markdown("""---""")
    st.markdown('### Avaliações')
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader('Avaliação média por Entregador ')
    
        df_aux = (df1[['Delivery_person_ID', 'Delivery_person_Ratings']].groupby('Delivery_person_ID')
          .mean().round(2).reset_index())

        st.dataframe(df_aux,  width = 700, height=700)    

    with col2:
        st.subheader('Avaliação média e desvio padrão por Trânsito ')
        
        df_aux = (df1[['Delivery_person_Ratings','Road_traffic_density']]
          .groupby('Road_traffic_density')
          .agg({'Delivery_person_Ratings': ['mean', 'std']})
          .round(2))

        df_aux.columns = ['delivery_mean', 'delivery_std']         

        df_aux.reset_index()
        st.dataframe(df_aux, width = 800, height=178) 
        
        st.subheader('Avaliação média e desvio padrão por Clima ')
        
        df_aux = (df1[['Delivery_person_Ratings','Weatherconditions']]
         .groupby('Weatherconditions')
         .agg({'Delivery_person_Ratings':['mean', 'std']})
         .round(2))

        df_aux.columns = ['delivery_mean', 'delivery_std'] 

        df_aux.reset_index()
        
        st.dataframe(df_aux, width = 800, height=248)
                      
            #Terceiro container 
#-------------------------------------------------------------#
        
with st.container():
    st.sidebar.markdown("""---""")
    st.markdown('## Velocidade de Entrega')
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader('Entregadores mais rápidos por cidade ')
        df_aux_total = top_deliverys( df1, top_asc=True )
        st.dataframe(df_aux_total,  width = 800, height=1088)

    
    with col2:
        st.subheader('Entregadores mais Lentos por cidade')
        df_aux_total = top_deliverys( df1, top_asc=False )
        st.dataframe(df_aux_total, width = 800, height=1088)     

    