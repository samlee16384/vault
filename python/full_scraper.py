from bs4 import BeautifulSoup
import requests
import pandas as pd
import csv
import time
import random
import string
# SCRAPING
# build set of URLS in reference video_data.csv
# scrape website videos until an existing url is found
# obtain all metadata for each video and add to video_data.csv
# id,url,thumbnail,title,video,tags,n_comments,stars,date,description_A,description_B,affiliate_link,affiliate_image,affiliate_image_desc
# increment the release date by 8 days
# download the thumbail, affiliate image, and video files into the folder E:\Documents\Misc\.DolphinGameFiles\.vault\.{video_id}. preserve filename but postfix with _t, _a, and _v respectivley
# verify that video is noncorrupt, otherwise add to database of corrupt videos corrupt.json and discard from video_data.csv
def download_img(url, location):
    filename = url[url.find('.com') + 5:].replace('/', '_')
    img_data = requests.get(url).content
    with open(f'./{location}/{filename}', 'wb') as handler:
        handler.write(img_data)

def scrape_video_data(url):
    video_data = {}
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')

    id = url.split('/')[-2]
    video_data['id'] = id
    video_data['url'] = url
    # download thumbnail
    thumbnail_url = soup.select_one('video').attrs['poster']
    video_data['thumbnail'] = thumbnail_url
    download_img(thumbnail_url, 'thumbnails')

    # scrape video url, tags, ncomments
    video_data['title'] = soup.select_one('.entry-title').contents[0]
    video_data['video'] = soup.select_one('source').attrs['src']
    video_data['tags'] = [c.contents[0] for c in soup.select_one('.entry-category').contents if c.name == 'a']
    n_comments = soup.select_one('.action-item.comments').contents[0]
    n_comments = n_comments.split(' ')[0].replace(',', '')
    video_data['n_comments'] = int(n_comments) if n_comments != 'Add' else 0

    # scrape pornstars
    try:
        video_data['stars'] = [c.contents[0] for c in soup.select_one('.entry_tags_tags').contents if c.name == 'a']
    except:
        video_data['stars'] = []
    video_data['date'] = soup.select_one('.meta-item.meta-date').contents[0].contents[0]

    # scrape desc and site
    descriptions = soup.select_one('.entry-content-single').contents[1].contents
    video_data['description_A'] = descriptions[0]
    try:
        video_data['description_B'] = descriptions[14]
    except:
        video_data['description_B'] = ''

    # scrape affiliate advertizing data
    video_data['affiliate_link'] = soup.select_one('a[target]').attrs['href'] if soup.select_one('a[target]') is not None else ''
    try:
        video_data['affiliate_image'] = list(descriptions[10].children)[0].attrs['src']
        video_data['affiliate_image_desc'] = list(descriptions[10].children)[0].attrs['alt']
        download_img(video_data['affiliate_image'], 'affiliate_images')
    except:
        video_data['affiliate_image'] = ''
        video_data['affiliate_image_desc'] = ''

    return video_data

'''finds url to all videos on damplips'''
def find_new_videos(existing_urls=()):
    new_videos = []
    N_PAGES = 3000
    for i in range(1, N_PAGES + 1):
        print('\r', f'Scraping page {i}/{N_PAGES}: {len(new_videos)} scraped', end='')
        url = f'http://www.damplips.com/tube/page/{i}'
        r = requests.get(url)
        soup = BeautifulSoup(r.content, 'html.parser')
        soup.select('.tube_item')
        for e in soup.select('.tube_item'):
            url = e.contents[1].attrs['href']
            if url not in existing_urls:
                new_videos.append(e.contents[1].attrs['href'])  # add url to list
            else:
                return new_videos # halt once an existing video is found
    return new_videos

def scape():
    video_data_list = []
    df = pd.read_csv('video_data.csv')
    new_videos = find_new_videos(list(df['url']))
    for i, url in enumerate(new_videos):
        time.sleep(random.random() / 2)
        print('\r', f'Scraping url #{i}/{len(new_videos)}: {url}', end='')
        try:
            video_data_list.append(scrape_video_data(url))
        except Exception as e:
            print(f'\nError encountered on video {url}: {e}')

    new_df = pd.DataFrame.from_dict(video_data_list)
    new_df['date'] = pd.to_datetime(new_df['date'], format='%B %d, %Y')
    df = pd.concat(df, new_df)
    df.to_csv('raw_video_data.csv')
    print('\ndone')



  # INDEXING
# reindex all the videos by whitespace-padded pairs and non-whitespace-padded triplets that occur from 85% to 15% of the time across all documents.
# Encode index in the binary csv index.csv where each column corresponds to a video and each row corresponds to a pair or triplet of characters. We can then & all rows appearing in the query then decode into a list of videos
# VECTORIZING
# rerun tf-idf
