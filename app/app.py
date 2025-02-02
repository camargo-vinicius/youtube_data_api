#%%
import pickle
import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
import plotly.express as px

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

# criando checkbox: se o usr selecionar, mostra o sample. Caso contrário, fica oculto.
if st.checkbox('Visualizar amostra'):
    # tabela de amostra dos 5 vídeos com mais views
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

col1.metric(value=f'{total_videos: ,}', label= 'Total videos')
col2.metric(value=f'{total_views: ,}', label='Total views')
col3.metric(value=f'{total_likes: ,}', label='Total likes')
col4.metric(value=f'{total_comments: ,}', label='Total comments')

st.divider()
#%%
# desempenho dos videos
st.subheader('3. Desempenho dos videos')
st.write('##### 3.1. Quantidade de visualizações por data de publicação')

# criando uma coluna de mes/ano para diminuir a granularidade das datas
df['mes_ano'] = df['published_date'].to_numpy().astype('datetime64[M]')

df_views_mes = df.groupby(by='mes_ano')['views_count'].sum()\
                                                      .reset_index()\
                                                      .sort_values(by='mes_ano') # para garantir que o eixo será ordenado corretamente

# Gráfico de visualizações ao longo do tempo para entender o engajamento com os vídeos
# alt.Chart(df) - cria o gráfico a partir do df
# .mark_line() - define que será um gráfico de linha
# .encode() - mapeia os eixos x e y

line_chart = alt.Chart(df_views_mes).mark_line().encode(
                                                            x=alt.X('mes_ano:T', title='Mes/ano de publicação', axis=alt.Axis(format=f"%Y-%m-%d")), # especifica que a coluna mes_ano do df é temporal  e qual o seu formato
                                                            y=alt.Y('views_count:Q', title='Visualizações') # especifica quue a coluna views_count é quantitativa
                                               ).properties(
                                                            width=700,
                                                            height=400
                                                        )

# exibe no streamlit
st.altair_chart(line_chart, use_container_width=True)
st.divider()

#%%
# top 10 videos com mais engajamento (likes + views + comments)
st.write(
"""##### 3.2. Top 10 vídeos maiores engajamentoss
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
                  xaxis_title='Engajamento total',
                  yaxis_title='Video',
                  height=600)

# atualiza o gráfico para exibir gráfico em ordem decrescente
fig.update_yaxes(categoryorder='total ascending')

# mostra na tela
st.plotly_chart(fig)
