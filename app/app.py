#%%
import pickle
import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
import plotly.express as px
import datetime
from dateutil.relativedelta import relativedelta
#%%
#%%
@st.cache_data # as datas não vão variar, então podemos usar o cache_data
def diff_months(date1, date2):
    """
    Calculate the difference in months between two dates.

    Parameters:
    date1 : First date - datetime object
    date2 : Second date - datetime object

    Returns:
    relativedelta
        A relativedelta object describing the difference in months
    """
    diff = relativedelta(date1, date2).years * 12 + relativedelta(date1, date2).months

    if diff <= 3:
        return '3 meses'
    
    elif diff <= 6:
        return '6 meses'
    
    else:
        return '+ 6 meses'

#%%
# fazendo o unpickling do arquivo data/videos_stats.pkl
with open('../data/videos_stats.pkl', 'rb') as f:
    df = pickle.load(f)
#%%
# ----------- criando o dashboard -----------------

# título do dashbaord
st.title('📊 Análise de performance de um canal Youtube')
df_sample = df.sort_values(by='views_count', ascending=False).reset_index(drop=True).head()

st.write("""
### 1. Amostra dos dados utilizados para as análises
Os dados são referentes ao canal 'Teo Me Why'.""") # equivalente à st.subheader('texto')

# para salvar o estado do usr e evitar que o app rode toda vez que o usr alterar o toggle
# if 'toggle' not in st.session_state:
#     st.session_state.toggle = False

# st.session_state.toggle = st.toggle(label='Visualizar amostra', value=st.session_state.toggle)
# # criando checkbox: se o usr selecionar, mostra o sample. Caso contrário, fica oculto.

# if st.session_state.toggle:
#     # tabela de amostra dos 5 vídeos com mais views
#     df_sample

if st.toggle('Visualizar amostra'):
    # tabela de amostra dos 5 videos com mais views
    df_sample

st.divider()
#%%
# visao geral do canal - total de videos, views, likes e comentários
total_videos = df.shape[0]
total_views = df['views_count'].sum()
total_likes = df['like_count'].sum()
total_comments = df['comments_count'].sum()

st.write('### 2. Visão geral do canal')

# criando 4 cards para mostrar os big numbers
col1, col2, col3, col4 = st.columns(4)

# exibindo os big numbers
col1.metric(value=f'{total_videos: ,}', label= 'Total videos')
col2.metric(value=f'{total_views: ,}', label='Total views')
col3.metric(value=f'{total_likes: ,}', label='Total likes')
col4.metric(value=f'{total_comments: ,}', label='Total comments')

st.divider()
#%%
# desempenho dos videos
st.subheader('3. Desempenho dos videos')
st.write('##### 3.1. Evolução de views por data de publicação')

# criando uma coluna de mes/ano para diminuir a granularidade das datas
df['mes_ano'] = df['published_date'].to_numpy().astype('datetime64[M]')

# agregando views por mes/ano de publicacao
df_views_mes = df.groupby(by='mes_ano')['views_count'].sum()\
                                                      .reset_index()\
                                                      .sort_values(by='mes_ano') # para garantir que o eixo será ordenado corretamente
#%%
# Gráfico de visualizações ao longo do tempo para entender o engajamento com os vídeos
# alt.Chart(df) - cria o gráfico a partir do df
# .mark_line() - define que será um gráfico de linha
# .encode() - mapeia os eixos x e y
line_chart = alt.Chart(df_views_mes).mark_line().encode(
                                                        x=alt.X('mes_ano:T', title='Mes/ano de publicação', axis=alt.Axis(format=f"%Y-%m-%d")), # especifica que a coluna mes_ano do df é temporal  e qual o seu formato,
                                                        y=alt.Y('views_count:Q', title='Visualizações'))\
                                                .properties(
                                                        width=700,
                                                        height=400)

# exibe no streamlit
st.altair_chart(line_chart, use_container_width=True)

st.divider()
#%%

# top 10 videos com mais engajamento (likes + views + comments)
st.write(
"""##### 3.2. Top 10 vídeos maiores engajamentos
O gráfico foi feito considerando (likes + comments) / views, já que naturalmente a quantidade de views
é muito maior do que likes e comentários.\n 
Podemos ver pelo gráfico abaixo que os vídeos que possuem um 
engajamento relativo maior são no estilo vlog, onde o Teo fala sobre carreira, estudos, planos futuros etc e não aqueles de
conteúdo técnico e hands-on. Uma hipótese para isso é que as lives de conteúdo técnico são gravadas também na twitch e ao vivo,
então isso pode acabar canibalizando com o mesmo conteúdo no youtube.""")

# criando métricas de engajamento relativo (likes + comments) / views
df['engajamento_relativo'] = (df['like_count'] + df['comments_count']) / df['views_count']
df_top_10 = df.sort_values(by='engajamento_relativo', ascending=False).head(10)

# criando um gráfico de barras horizontal com os dados do top 10 videos
fig = px.bar(df_top_10, 
             x='engajamento_relativo',
             y='title',
             orientation='h',
             color_discrete_sequence=["skyblue"])

# adicionando os rótulos ao gráfico
for x, y in zip(df['engajamento_relativo'], df['title']):
    fig.add_annotation(
        x=x - 0.03, # o sinal negativo traz o valor de x mais para a esquerda da barra (qto menor o valor subtraido, mais p// esquerda o rotulo aparece)
        y=y, # posicao do eixo y
        text=f'{x:.2f}', # configura o formato do valor do rótulo
        font=dict(size=12, color='black'), # tamanho e cor do rótulo
        showarrow=False
    )

# configurando nomes dos eixos, título e altura
fig.update_layout(title='Top 10 vídeos com maior engajamento',
                  xaxis_title='Engajamento relativo',
                  yaxis_title='Video',
                  height=600)

# atualiza o gráfico para exibir rótulos em ordem decrescente
fig.update_yaxes(categoryorder='total ascending')

# mostra na tela o gráfico 
st.plotly_chart(fig)

st.divider()
#%%
# segmentando top 10 videos por 3 meses, 6 meses e 1 ano da dt de publicacao em relacao a data atual
df['datediff'] = df['published_date'].apply(lambda x: diff_months(datetime.datetime.now(), x))

# criando o slicer
st.write("""
##### 4. Top 10 vídeos por período de tempo
Podemos perceber que os vídeos com mais views publicados nos últimos 06 meses são menos técnicos
em relação à vídeos publicados há mais de um ano""")

# check box para o usr selecionar o periodo desejado (3 meses, 6 meses e 1 ano)
opcao = st.selectbox(
    'Selecione uma das opções',
    list(df['datediff'].unique())
)

# filtrando o df por opcao
df_top_10_periodo = df.query("datediff == @opcao").sort_values(by='views_count', ascending=False).head(10)

# exibindo na tela
cols = ['title', 'published_date', 'views_count', 'like_count', 'comments_count']
st.dataframe(df_top_10_periodo[cols].style.highlight_max(axis=0, subset=cols[2:], color='skyblue'))

st.divider()
#%%
# correlação de métricas
st.write("""
##### 5. Correlação de méticas
""")

st.scatter_chart(data=df, 
                 x='views_count', 
                 y='like_count', 
                 size='comments_count', 
                 x_label='Quantidade de views', 
                 y_label='Quantidade de likes')

