from multiprocessing import Pool, cpu_count
from functools import partial
from io import BytesIO
import threading
from simplify import get_df
import requests
import urllib
from os.path import exists
from multiprocessing.pool import ThreadPool
import concurrent.futures

DIRECTORY = 'E:\\Documents\\.DolphinGameFiles\\.vault\\.main'

def download_video(i_url):
    i, url = i_url
    print(f'\rscraping video {i}/{7000}: {url}' + ' ' * 20, end='')
    try:
        # print(f'\rscraping video {i+1}/{len(videos)}: {v}' + ' ' * 20, end='')
        file_name = DIRECTORY + url.split("//")[1].replace('/', '_')
        if not exists(file_name):
            urllib.request.urlretrieve(url, file_name)
    except:
        pass
    return 'done'
    # print('\n'+e)
    # with open('unscraped.txt', 'a') as f:
    #     # print(f'\rFailed to download {i+1}/{len(videos)}: {v}')
    #     f.write(url + '\n')

# def scape_videos(videos):
#     for i, v in enumerate(videos):

urls = enumerate(list(get_df()['video']))

with concurrent.futures.ThreadPoolExecutor(max_workers=4) as exector:
    exector.map(download_video, urls)
