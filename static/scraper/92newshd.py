import numpy as np
# beautiful soup is api that is used for crawling
from bs4 import BeautifulSoup
# pandas is for datamanipulation
import pandas as pd
# ssl is used for connection
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

from IPython.core.display import Image
from datetime import datetime, timedelta
import urllib.error, urllib.request, urllib.parse
import requests
import csv
from urllib.request import Request, urlopen

# url used for getting the news, example of 92 news is given
base_url_sports = "https://92newshd.tv/category/sports"
base_url = "https://92newshd.tv/news-by-date/{}-{}-{}"
# Start date of news for scrapping
search_date = datetime(2022, 12, 1)
# end date for news scrapping
end_date = datetime(2022, 12, 10)
# specifying number of days
one_day = timedelta(days=1)
courses_list = []
# getting news between dates
while search_date < end_date:
    url = base_url.format(search_date.year, search_date.month, search_date.day)
    print(url)
    page = requests.get(url)
    # api used for scrapping
    soup = BeautifulSoup(page.text, 'html.parser')
    # moving date and creating list of all elements to grab
    search_date += one_day
    date = []
    title = []
    href = []
    image_url = []
    news_contents = []
    # Reading the content (it is divided in paragraphs) # Unifying the paragraphs
    date1 = soup.find_all('div', attrs={'class': "published_time"})
    title1 = soup.find_all('div', attrs={'class': "title"})
    links = soup.find_all('a', attrs={'class': "post_link"})
    img_url = soup.find_all('img', class_='post_img thumb')
    # loop to get all elements first date
    for element in date1:
        print(element.text)
        date.append(element.text)
    # loop to get all element title
    for tex in title1:
        print(tex.text)
        title.append(tex.text)
    # loop to get all links
    for a_link in links:
        link1 = 'https://92newshd.tv' + a_link.get('href')
        href.append(link1)
        print(link1)
        article = requests.get(link1)
        article_content = article.content
        soup_article = BeautifulSoup(article_content, 'html.parser')
        body = soup_article.find_all('div', attrs={'class': "content_detail"})
        x = body[0].find_all('p')
        paragraph = []
        list_paragraphs = []
        final_article = []
        for p in np.arange(0, len(x)):
            paragraph = x[p].get_text()
            list_paragraphs.append(paragraph)
        final_article = " ".join(list_paragraphs)
        news_contents.append(final_article)
    print(news_contents)
    for i_url in img_url:
        image = 'https://92newshd.tv/' + i_url['data-src']
        image_url.append(image)
        print(image_url)
    # printing the content of all the news and saving it in the dataframe
    df = pd.DataFrame(list(zip(date, title, href, image_url, news_contents)),
                      columns=['Date', 'Title', 'News_Url', 'Image_Url', 'News_Content'])
    df.to_csv('92_News.csv', mode='a', index=False, header=True)
    # print(df.head(10))
    # df.to_csv("output1.csv", index=False)
print("Completed!")
