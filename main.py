#%%
import pandas as pd
import os
import requests
import time
from dotenv import load_dotenv

# carregando variaveis de ambiente
load_dotenv()

# setando variaveis de ambiente
API_KEY = os.getenv("YOUTUBE_API_KEY")

CHANNEL_ID = os.getenv("CHANNEL_ID")

#%%
def get_videos_list(pg_token: str):
    """
    Fetches a list of videos from a specified YouTube channel.

    This function makes an API call to the YouTube Data API to retrieve
    a list of videos from a specified channel, ordered by date.

    Args:
        pg_token (str): The page token for pagination.

    Returns:
        dict: A dictionary containing the JSON response from the API,
              which includes a list of videos.
    """
    
    # url base
    url_list_base = f"https://www.googleapis.com/youtube/v3/search?key={API_KEY}&channelId={CHANNEL_ID}&part=snippet,id&order=date&maxResults=50"
    
    # url para paginacao
    url_list_videos = f"{url_list_base}&pageToken={pg_token}" if pg_token else url_list_base

    response = requests.get(url=url_list_videos)

    if response.status_code != 200:
        raise Exception(f"Falha na requisição da lista de vídeos! status code = {response.status_code} - {response.json()['error']['message']}")

    return response.json()
# --------------------------------------------------------------------

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
    video_stats = requests.get(url=url_stats).json()

    return video_stats['items'][0]['statistics']['viewCount'],\
           video_stats['items'][0]['statistics']['likeCount'],\
           video_stats['items'][0]['statistics']['commentCount']

#%%

def collect_data_videos() -> pd.DataFrame:
    """
    Collects video data from a YouTube channel using pagination.

    Returns:
        pd.DataFrame: A DataFrame containing the collected video data.
    """
    
    # setando page_token para iniciar
    page_token = ""

    # setando o dicionario que irá guardar os dados de todos os videos
    dict_videos = {'video_id': [],
                    'title': [],
                    'published_date': [],
                    'views_count': [],
                    'like_count': [],
                    'comments_count': []}

    while True:

        try:
            data_videos = get_videos_list(page_token)

            # delay de 1s para API conseguir coletar todos os dados sem atingir limite de cotas
            time.sleep(1)

            # pegando as infos de todos os videos
            for video in data_videos['items']:
                
                # pegando dados somente de videos
                if video['id']['kind'] == 'youtube#video':
                
                    video_id = video['id']['videoId']
                    dict_videos['video_id'].append(video_id)
                    
                    dict_videos['title'].append(video['snippet']['title'])
                    
                    dict_videos['published_date'].append(video['snippet']['publishedAt'].split('T')[0])

                    # chamando função para pegar views, likes e comentarios do video
                    views_count, like_count, comments_count = get_videos_stats(video_id)

                    dict_videos['views_count'].append(views_count)
                    
                    dict_videos['like_count'].append(like_count)
                    
                    dict_videos['comments_count'].append(comments_count)

            # pega o token da prox pag
            page_token = data_videos.get('nextPageToken')

            if page_token is None: # sai do loop while
                break

        except Exception as error:
            print(f'Erro na coleta dos dados: {error}')
            break

        else:
            print(f'Coleta feito com sucessso! criando df...')
            df = pd.DataFrame(dict_videos)

            return df



#%%
df_videos = collect_data_videos()

if isinstance(df_videos, pd.DataFrame):
    df_videos.shape

else:
    df_videos