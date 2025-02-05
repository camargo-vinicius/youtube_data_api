#%%
import pandas as pd
import os
import requests
import time
import pickle
from dotenv import load_dotenv

# carregando variaveis de ambiente
load_dotenv()

# setando variaveis de ambiente
API_KEY = os.getenv("YOUTUBE_API_KEY")

# id do canal desejado 
CHANNEL_ID = 'UC-Xa9J9-B4jBOoBNIHkMMKA'

#%%
def get_videos_list(pg_token: str):
    
    # url para paginacao
    url_list_videos = f"https://www.googleapis.com/youtube/v3/search?key={API_KEY}&channelId={CHANNEL_ID}&part=snippet,id&order=date&maxResults=50&pageToken={pg_token}"
    
    response = requests.get(url=url_list_videos)

    if response.status_code != 200:
        raise Exception(f"Falha na requisição da lista de vídeos! status code = {response.status_code} - {response.json()['error']['message']}")
            
    return response.json()

# --------------------------------------------------------------------
#%%
def get_videos_stats(video_id: str) -> tuple:
    """
    Fetches statistics for a given YouTube video.

    This function makes an API call to the YouTube Data API to retrieve
    the view count, like count, and comment count for a specified video.

    Args:
        video_id (str): The ID of the YouTube video.

    Returns:
        tuple: A tuple containing the view count, like count, and comment count
               of the video as strings.
    """
    # pegando as estatisticas de cada video com uma segunda chamada de API
    url_stats = f'https://www.googleapis.com/youtube/v3/videos?part=statistics&id={video_id}&key={API_KEY}'

    response = requests.get(url=url_stats)

    if response.status_code != 200:
        raise Exception(f"Falha na requisição da lista de vídeos! status code = {response.status_code} - {response.json()['error']['message']}")
        
    video_stats = response.json()
        
    # parsing 
    views = video_stats['items'][0]['statistics'].get('viewCount', '0')
    likes = video_stats['items'][0]['statistics'].get('likeCount', '0')
    comments = video_stats['items'][0]['statistics'].get('commentCount', '0')
    
    return views, likes, comments
# --------------------------------------------------------------------
#%%
def collect_data_videos() -> pd.DataFrame:
    """
    Collects video data from a YouTube channel using pagination.

    Returns:
        pd.DataFrame: A DataFrame containing the collected video data.
    """

    # setando o dicionario que irá guardar os dados de todos os videos
    dict_videos = {'video_id': [],
                    'title': [],
                    'published_date': [],
                    'views_count': [],
                    'like_count': [],
                    'comments_count': []
                    }

    # setando page_token para iniciar
    page_token = ""

    while page_token is not None:

        try:
            data_videos = get_videos_list(page_token)

        except Exception as e:
            print(e)
            break

        # delay de 1s para API conseguir coletar todos os dados sem atingir limite de cotas
        time.sleep(1)

        # percorre a lista de vídeo, coletando as infos de cada um
        for video in data_videos['items']:
            
            # pegando dados somente de videos
            if video['id']['kind'] == 'youtube#video':
            
                video_id = video['id']['videoId']
                dict_videos['video_id'].append(video_id)
                
                dict_videos['title'].append(video['snippet']['title'])
                
                dict_videos['published_date'].append(video['snippet']['publishedAt'].split('T')[0])

                try:
                    # chamando função para pegar views, likes e comentarios do video
                    views_count, like_count, comments_count = get_videos_stats(video_id)

                    # appendando cada estatística na sua respectiva chave do dict
                    dict_videos['views_count'].append(views_count)
                    dict_videos['like_count'].append(like_count)
                    dict_videos['comments_count'].append(comments_count)
                
                except Exception as e:
                    print(e)
                    break
        
        else:
            # pega o token da prox pag somente se o programa não der um break no for loop
            page_token = data_videos.get('nextPageToken')

    else:
        # se page_token é None, sai do while e gera o df final. Este bloco só é executado, se get_videos_list(page_token) não gerar
        return pd.DataFrame(dict_videos)
# --------------------------------------------------------------------
#%%
def transform(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform the input DataFrame by converting specific columns to integer type.

    This function takes a DataFrame containing YouTube video statistics and
    converts the 'views_count', 'like_count', and 'comments_count' columns
    from their original data type to 32-bit integers.

    Args:
        df (pd.DataFrame): The input DataFrame containing YouTube video statistics.

    Returns:
        pd.DataFrame: The transformed DataFrame with the specified columns
                      converted to int32 data type.
    """
    
    # convertendo colunas de estatisticas para inteiro e published_date para datetime
    cols = ['views_count', 'like_count', 'comments_count'] 

    df = df.astype({'views_count': 'int32',
                    'like_count': 'int32',
                    'comments_count': 'int32',
                    'published_date': 'datetime64[ns]'})
    return df

#%%
def main():
    df_videos = collect_data_videos()
    df_processed = transform(df_videos)

    # salvando como pickle em formato binário

    try:
        with open('../app/videos_stats.pkl', 'wb') as f:
            pickle.dump(df_processed, f)
    
    except Exception as e:
        print(e)

    else:
        print('Arquivo salvo com sucesso.')
#%%
main()
