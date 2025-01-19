#%%
import pandas as pd
import os
import requests
import time
import json
from dotenv import load_dotenv

# carregando variaveis de ambiente
load_dotenv()

# setando variaveis de ambiente
API_KEY = os.getenv("YOUTUBE_API_KEY")
CHANNEL_ID = os.getenv("CHANNEL_ID")

#%%
def get_videos_list(api_key: str, channel_id: str, pg_token):
    """
    Fetches a list of videos from a specified YouTube channel.

    This function makes an API call to the YouTube Data API to retrieve
    a list of videos from a specified channel, ordered by date.

    Args:
        api_key (str): The API key for accessing the YouTube Data API.
        channel_id (str): The ID of the YouTube channel.
        pg_token (str): The page token for pagination.

    Returns:
        dict: A dictionary containing the JSON response from the API,
              which includes a list of videos.
    """
    
    url_list_videos = f"https://www.googleapis.com/youtube/v3/search?key={api_key}&channelId={channel_id}&part=snippet,id&order=date&maxResults=200000&{pg_token}"
    
    return requests.get(url=url_list_videos).json()
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
    # pegando a lista de videos da caze tv
    page_token = ""

    # setando o dicionario que irá guardar os dados de todos os videos
    dict_videos = {'video_id': [],
                    'title': [],
                    'published_date': [],
                    'views_count': [],
                    'like_count': [],
                    'comments_count': []}

    # while page_token != None:

    data_videos = get_videos_list(API_KEY, CHANNEL_ID, page_token)
    # print(data_videos)

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

    # pega o token da
    # page_token = data_videos['nextPageToken']

    # criando df a partir do dicionario
    return pd.DataFrame(dict_videos)


def main():
    df_videos = collect_data_videos()
    df_videos.head()

main()

#%%
page_token = ""
data_videos = get_videos_list(API_KEY, CHANNEL_ID, page_token)
print(data_videos)