import redis
import csv
import requests
import multiprocessing
from bs4 import  BeautifulSoup
redis_cache = redis.StrictRedis()
headers = requests.utils.default_headers()
f = open("./reddit_comments.csv", 'w+', encoding='utf-8')
writer = csv.writer(f)


def comment_scraper(url):
    headers = {
        "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36"
    }
    response = requests.get(url,headers=headers)
    markup = response.text
    soup = BeautifulSoup(markup, "html.parser")
    titles = soup.find_all("p", {"class": "title"})

    for title in titles:
        post = title.text.strip()
        print(post)
    post = ""

    comments_div = soup.find_all("div",{"class":"usertext-body may-blank-within md-container "})
    del comments_div[0]
    for comment in comments_div:
        print(comment.text)
        writer.writerow([
            post,
            comment.text.strip()
        ])


    return


if __name__ == "__main__":
    data = redis_cache.lrange("title",0,1000)
    final = list()
    if data:
        for element in data:
            element = element.decode()
            final.append(element)

    for row in final:
        comment_scraper(row)
    f.close()

