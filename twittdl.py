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
from dist.config import IMG_URL, VID_URL

# Read the URLs from the text files
with open('img.txt', 'r') as f:
    img_urls = f.read().splitlines()

with open('vid.txt', 'r') as f:
    vid_urls = f.read().splitlines()

# Read the User-Agents from the text file
with open('UA.txt', 'r') as f:
    user_agents = f.read().splitlines()

# Create a directory to store the downloaded media
directory = input('Enter a name for folder: ')
if not os.path.exists(directory):
    os.makedirs(directory)

# Create a session
session = requests.Session()

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
            # Update the User-Agent when the proxy changes
            session.headers.update({
                'User-Agent': user_agents[proxy_usage_count[proxy] % len(user_agents)],
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
        img_url = IMG_URL.format(tweet_id=tweet_id)
        retry = True
        while retry:
            response_img = make_request_with_retries(img_url, verify=True)
            img_data = response_img.json()
            try:
                image_urls = img_data['images']
                retry = False
            except KeyError:
                print(f'Error: No images found for tweet {tweet_id}. Retrying with a new proxy...')
                continue

        # Modify the image URLs to get higher resolution images
        new_image_urls = []
        for url in image_urls:
            new_url = url.replace('.jpg', '?format=png&name=4096x4096')
            new_image_urls.append(new_url)

        # Download the images
        for i, url in enumerate(new_image_urls):
            filename = f'{directory}/{tweet_id}_{i}.png'
            if os.path.exists(filename):
                print(f'Skipping image download: {filename} (already exists)')
                continue
            response = make_request_with_retries(url)
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f'Downloaded image: {filename}')

    # Download videos from the URLs in vid.txt
    for tweet_url in vid_urls:
        tweet_id = re.findall(r'/status/(\d+)', tweet_url)[0]
        vid_url = VID_URL.format(tweet_id=tweet_id)
        response_vid = make_request_with_retries(vid_url)
        vid_data = response_vid.json()

        # Get the video URL
        video_url = vid_data['video']['url']

        # Download the video
        filename = f'{directory}/{tweet_id}.mp4'
        if os.path.exists(filename):
            print(f'Skipping video download: {filename} (already exists)')
            continue
        response = make_request_with_retries(video_url)
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f'Downloaded video: {filename}')
except KeyboardInterrupt:
    print('Exiting Now...')
    try:
        shutil.rmtree('__pycache__')
    except FileNotFoundError:
        pass
    sys.exit(0)