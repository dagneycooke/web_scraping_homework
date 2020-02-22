# import all the things
import pandas as pd
from bs4 import BeautifulSoup
import requests
import os
from splinter import Browser
import time


def init_browser():
    executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
    return Browser('chrome', **executable_path, headless=False)

def scrape():
    mars_info = {}
    # *******************************************************
    # get most recent article title and text
    # *******************************************************

    #connect to chromedriver

    browser = init_browser()

    browser.visit('https://mars.nasa.gov/news/')

    # pause to give chromedriver time to connect
    time.sleep(3) # shouts to Heain for helping me fix this issue!

    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    # find all content titles on page
    title_block = soup.find_all('div', class_='content_title')

    # get the most recent title
    news_title = title_block[0].find('a').get_text()

    # find all paragraphs on the page
    paragraph_block = soup.find_all('div', class_='article_teaser_body')

    news_p = paragraph_block[0].get_text()

    browser.quit()

    # *******************************************************
    # get current space image
    # *******************************************************

    browser = init_browser()

    browser.visit('https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars')

    time.sleep(3)

    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    # find a frame with full size jpg image link
    header_image = soup.find_all('a',class_='button fancybox')

    leading_url = 'https://www.jpl.nasa.gov'
    # pull out jpeg image link
    featured_image_url = leading_url + header_image[0]['data-fancybox-href']

    browser.quit()

    # *******************************************************
    # get weather info from twitter
    # *******************************************************

    browser = init_browser()

    browser.visit('https://twitter.com/marswxreport?lang=en')

    time.sleep(3)

    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    # identify correct span class
    tweet_local = soup.find_all('span',class_='css-901oao css-16my406 r-1qd0xha r-ad9z0x r-bcqeeo r-qvutc0')

    # loop through list until you find the text within the first tweet, and then exit the loop
    for span in tweet_local:
        test = span.get_text()
        if "InSight sol" in test: # all weather tweets start with this text
            mars_weather = test
            break # exit loop once you find the weather text
            
    browser.quit()

    # *******************************************************
    # get mars facts in table
    # *******************************************************

    url = 'https://space-facts.com/mars/'

    # read tables in from website
    tables = pd.read_html(url)

    # grab the first table
    mars_facts = tables[0]

    # rename the columns
    mars_facts.columns = ["","value"]

    mars_facts.set_index("",inplace=True)

    mars_facts_html = mars_facts.to_html()

    # *******************************************************
    # get hemisphere images
    # *******************************************************

    browser = init_browser()

    browser.visit('https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars')

    time.sleep(3)

    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    hemispheres = soup.find_all('div', class_='item')

    hem_list = []

    # loop through links

    for hem in hemispheres:
        
        hem_dict = {}
        
        # find link
        name = hem.find('h3').text

        # go to link
        browser.click_link_by_partial_text(name)
        
        time.sleep(3)

        html = browser.html
        soup = BeautifulSoup(html, 'html.parser')
        
        # find image and create full link
        image_thing = soup.find_all('img',class_="wide-image")
        hem_link = "https://astrogeology.usgs.gov" + image_thing[0]['src']
        
        # find hemisphere name
        page_title = soup.find_all('h2',class_="title")
        hem_title = page_title[0].get_text()
        
        # create dictionary of name + title
        hem_dict = {'title':hem_title,'img_url':hem_link}
        
        # append to list
        hem_list.append(hem_dict)

        # return to main page
        browser.back()
    
    browser.quit()

    # save all info into a new dictionary
    mars_info = {"news_title":news_title,
                "news_text":news_p,
                "featured_image":featured_image_url,
                "weather_info":mars_weather,
                "mars_facts":mars_facts_html,
                "hemisphere_info":hem_list,
                }
    
    return mars_info

