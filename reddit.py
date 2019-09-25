from  selenium import webdriver
import redis
import csv
from contextlib import closing
from bs4 import  BeautifulSoup
from  selenium.common.exceptions import NoSuchElementException
driver = webdriver.Chrome()
redis_cache = redis.StrictRedis()


def reddit_scraper():
    driver.get("https://www.reddit.com/r/gameofthrones/")
    html = driver.page_source
    driver.implicitly_wait(2)
    reddit = driver.find_element_by_xpath('//*[@id="SHORTCUT_FOCUSABLE_DIV"]/div/div[1]/div/div/a')
    reddit.click()
    next = driver.find_element_by_xpath('//*[@id="siteTable"]/div[55]/span/span')
    next.click()
    with open("./reddit_posts.csv","w",encoding='utf-8') as file:
        writer = csv.writer(file)
        post, upv, time_ago, comments = "","","",""
        while True:
            try:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                markup = driver.page_source
                soup = BeautifulSoup(markup,"html.parser")
                titles = soup.find_all("p",{"class":"title"})
                upvotes = soup.find_all("div",{"class":"score unvoted"})
                num_comments = soup.find_all("ul",{"class":"flat-list buttons"})
                for number in num_comments:
                    try:
                        comments = number.find("li",{"class":"first"}).find("a").text
                    except AttributeError:
                        comments = ""
                for upvote in upvotes:
                    upv = upvote.text
                time_elapsed = soup.find_all("p",{"class":"tagline "})
                for time in time_elapsed:
                    try:
                        time_ago = time.find('time')["title"]
                    except TypeError:
                        time_ago = ""
                for title in titles:
                    post = title.text
                    url = "https://www.reddit.com/" + title.find("a")["href"]
                    if '/r/gameofthrones' in url:
                        redis_cache.rpush("title", url)
                    writer.writerow([
                        post,
                        upv,
                        time_ago,
                        comments
                    ])
                next = driver.find_element_by_xpath('//*[@id="siteTable"]/div[51]/span/span[3]')
                next.click()

            except NoSuchElementException as e:
                print(str(e))
                break
        driver.quit()


if __name__=="__main__":
    reddit_scraper()
