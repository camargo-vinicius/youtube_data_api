#%%
import pickle
import streamlit as st
import pandas as pd

#%%
# fazendo o unpickling do arquivo data/videos_stats.pkl
with open('../data/videos_stats.pkl', 'rb') as f:
    df = pickle.load(f)

# criando o dashboard

# título
st.title('📊 Dashboard de estatísticas de vídeos do Youtube')

# visualização do dataframe
st.dataframe(df)