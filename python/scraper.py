from bs4 import BeautifulSoup
import requests
import pandas as pd
import csv
import time
import random
import string

def download_img(url, location):
    filename = url[url.find('.com') + 5:].replace('/', '_')
    img_data = requests.get(url).content
    with open(f'./{location}/{filename}', 'wb') as handler:
        handler.write(img_data)

def scrape_urls():
    videos = {}
    N_PAGES = 297
    for i in range(1, N_PAGES + 1):
        print('\r', f'Scraping page {i}/{N_PAGES}: {len(videos)} scraped', end='')
        url = f'http://www.damplips.com/tube/page/{i}'
        r = requests.get(url)
        soup = BeautifulSoup(r.content, 'html.parser')
        soup.select('.tube_item')
        for e in soup.select('.tube_item'):
            href = e.contents[1].attrs['href']
            title = e.contents[1].contents[1].attrs['alt']
            thumbnail = e.contents[1].contents[1].attrs['src']
            videos[href] = [title, thumbnail]

    pd.DataFrame.from_dict(videos, orient='index', columns=['Title', 'Thumbnail']).to_csv('videos.csv')
    print('done')

def scrape_video_data(url, video_data_list):
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

    video_data_list.append(video_data)

# df = pd.read_csv('video_data.csv')
# print(df.head())
# new_df = df[[]]

def scape():
    df = pd.read_csv('videos.csv')

    video_data_list = []
    for i, url in enumerate(list(df['url'])):
        time.sleep(random.random() / 2)
        print('\r', f'Scraping url #{i}/{len(df)}: {url}', end='')
        try:
            scrape_video_data(url, video_data_list)
        except Exception as e:
            print(f'\nError encountered on video {url}: {e}')

    df = pd.DataFrame.from_dict(video_data_list)
    df['date'] = pd.to_datetime(df['date'], format='%B %d, %Y')
    df.to_csv('raw_video_data.csv')
    print('\ndone')


# counter = 0
# for url, thumbnail in zip(list(df['Unnamed: 0']), list(df['Thumbnail'])):
#     counter += 1
#     print('\r', f'Scraping img #{counter}/{len(df)}: {url}', end='')
#     id = url[26:-1]
