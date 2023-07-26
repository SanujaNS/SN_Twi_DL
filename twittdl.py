#!/usr/local/bin/python3
# coding: utf-8

# Twitter_DL - twittdl.py
# 07/26/2023 16:52
#

__author__ = "SanujaNS <sanuja.senaviratne@gmail.com>"

import os
import signal
import sys
import shutil
import re
import requests
from proxies import Proxies
from requests.exceptions import Timeout

# Read the URLs from the text files
with open('img.txt', 'r') as f:
    img_urls = f.read().splitlines()

with open('vid.txt', 'r') as f:
    vid_urls = f.read().splitlines()

# Create a directory to store the downloaded media
directory = input('Enter a name for folder: ')
if not os.path.exists(directory):
    os.makedirs(directory)

# Create a session
session = requests.Session()

# Set up the headers for the session
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Authorization': 'JWT null',
    'Origin': 'https://www.brandbird.app',
    'Connection': 'keep-alive',
    'Referer': 'https://www.brandbird.app/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site'
})

# Load the SOCKS5 proxies from the Proxies class
proxies = Proxies()
proxy_list = proxies.load_proxy_list()

# Initialize the proxy usage count dictionary
proxy_usage_count = {}

# Set up a function to make requests with retries
def make_request_with_retries(url, timeout=5, retries=3, verify=True, proxy_usage_limit=25):
    for i in range(retries):
        for proxy in proxy_list:
            if proxy not in proxy_usage_count:
                proxy_usage_count[proxy] = 0
            if proxy_usage_count[proxy] >= proxy_usage_limit:
                continue
            session.proxies.update({
                "http": f"socks5://{proxy}"
            })
            print(f'Using proxy: {proxy} (count: {proxy_usage_count[proxy]})')
            try:
                response = session.get(url, timeout=timeout, verify=verify)
                proxy_usage_count[proxy] += 1
                return response
            except Timeout:
                print(f'Timeout occurred with proxy {proxy}. Trying next proxy.')
            except Exception as e:
                print(f'An error occurred with proxy {proxy}: {e}')
        print(f'Retry {i+1} failed. Retrying...')
    raise Exception(f'Failed to make request after {retries} retries.')

try:
    # Download images from the URLs in img.txt
    for tweet_url in img_urls:
        tweet_id = re.findall(r'/status/(\d+)', tweet_url)[0]
        img_url = f'https://api.brandbird.app/twitter/public/tweets/{tweet_id}/images'
        response_img = make_request_with_retries(img_url, verify=True)
        img_data = response_img.json()
        image_urls = img_data['images']
        
        # Modify the image URLs to get higher resolution images
        new_image_urls = []
        for url in image_urls:
            new_url = url.replace('.jpg', '?format=png&name=4096x4096')
            new_image_urls.append(new_url)
        
        # Download the images
        for i, url in enumerate(new_image_urls):
            response = make_request_with_retries(url)
            filename = f'{directory}/{tweet_id}_{i}.png'
            with open(f'{directory}/{tweet_id}_{i}.png', 'wb') as f:
                f.write(response.content)
            print(f'Downloaded image: {filename}')

    # Download videos from the URLs in vid.txt
    for tweet_url in vid_urls:
        tweet_id = re.findall(r'/status/(\d+)', tweet_url)[0]
        vid_url = f'https://api.brandbird.app/twitter/public/tweets/{tweet_id}/video'
        response_vid = make_request_with_retries(vid_url)
        vid_data = response_vid.json()
        
        # Get the video URL
        video_url = vid_data['video']['url']
        
        # Download the video
        response = make_request_with_retries(video_url)
        filename = f'{directory}/{tweet_id}.mp4'
        with open(f'{directory}/{tweet_id}.mp4', 'wb') as f:
            f.write(response.content)
        print(f'Downloaded video: {filename}')
except KeyboardInterrupt:
    print('Exiting Now...')
    try:
        shutil.rmtree('__pycache__')
    except FileNotFoundError:
        pass
    sys.exit(0)