# -*- coding: utf-8 -*-
from selenium import webdriver
from tqdm import tqdm
from glob import glob
import time
import pandas as pd
import numpy as np
import os
import tweepy
from skimage import io
import hashlib
import datetime
import logging
from dotenv import load_dotenv

# require you-get tweepy
load_dotenv()
logging.basicConfig(level=logging.INFO, format='- %(levelname)s --- %(message)s')
logging.info("---------------------------------------------------------------")
logging.info("now is {}".format(datetime.datetime.now()))
logging.info("Starting to crawling...")

USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
BROWERSTACK_USERNAME = os.getenv("BROWERSTACK_USERNAME")
BROWERSTACK_PASSWORD = os.getenv("BROWERSTACK_PASSWORD")
CHALLENGE_NUMBER = os.getenv("CHALLENGE_NUMBER")
TWITTER_OAUTH_KEY = os.getenv("TWITTER_OAUTH_KEY")
TWITTER_OAUTH_VALUE = os.getenv("TWITTER_OAUTH_VALUE")
TWITTER_TOKEN_KEY = os.getenv("TWITTER_TOKEN_KEY")
TWITTER_TOKEN_VALUE = os.getenv("TWITTER_TOKEN_VALUE")

def get_hash(url):
    try:
        data = io.imread(url)
        hash_result = hashlib.sha256(data).hexdigest()
    except:
        hash_result = ""
    return hash_result


def login(driver):
    driver.get("https://twitter.com/login")
    elem = driver.find_element_by_xpath('//input[@class="js-username-field email-input js-initial-focus"]')
    elem.send_keys(USERNAME)
    time.sleep(2)
    elem = driver.find_element_by_xpath('//input[@class="js-password-field"]')
    elem.send_keys(PASSWORD)
    time.sleep(2)
    elem = driver.find_element_by_xpath('//*[@id="page-container"]/div/div[1]/form/div[2]/button')
    elem.click()
    time.sleep(2)
    try:
        elem = driver.find_element_by_id("challenge_response")
        elem.send_keys(CHALLENGE_NUMBER)
        elem = driver.find_element_by_id("email_challenge_submit")
        elem.click()
        logging.info("Challenge!")
    except:
        logging.info("No challenge!")


def check():
    auth = tweepy.OAuthHandler(TWITTER_OAUTH_KEY, TWITTER_OAUTH_VALUE)
    auth.set_access_token(TWITTER_TOKEN_KEY, TWITTER_TOKEN_VALUE)

    api = tweepy.API(auth)

    user = api.get_user(USERNAME)
    friend_list = [friend.screen_name for friend in user.friends(count=100)]

    url_all = []
    number_all = []
    pic_all = []
    for friend in tqdm(friend_list, desc="Find following status."):
        try:
            timeline = api.user_timeline(id=friend, count=200)
            for timeone in timeline:
                if timeone._json.get('retweeted_status'):
                    retweeted_time = timeone.retweeted_status._json
                    like_number = retweeted_time.get("favorite_count")
                else:
                    like_number = timeone.favorite_count

                video_link = timeone.entities.get("media", [{"expanded_url": ""}])[0].get("expanded_url")
                pic_link = timeone.entities.get("media", [{"media_url": ""}])[0].get("media_url")
                url_all.append(video_link)
                number_all.append(like_number)
                pic_all.append(pic_link)
        except tweepy.TweepError:
            logging.debug("Account {} is not authorized.".format(friend))

    info = pd.DataFrame({"url": url_all, "number": number_all, "pic": pic_all})
    info_select = info.loc[(info["url"] != "") & (info["number"] > 1000) & (info["pic"] != "")].copy()
    info_select_video = info_select.loc[["video" in x for x in info_select["url"]]].copy()
    info_select_video = info_select_video.groupby("url").max().reset_index()
    info_select_video["url"] = info_select_video["url"].apply(lambda x: x.split("video")[0])

    return info_select_video

def reblog(file_path, driver):
    driver.get("https://twitter.com/compose/tweet")

    time.sleep(2)

    elem = driver.find_element_by_xpath('//div[div[@aria-label="Add photos or video"]]/input')

    elem.send_keys(os.path.abspath(file_path))

    elem = driver.find_element_by_xpath(
        '//div[@aria-label="Tweet text"]'
    )
    name = eval(os.getenv("NAME"))
    desc = eval(os.getenv("DESC"))
    name_one = np.random.choice(name)
    desc_one = np.random.choice(desc)
    elem.send_keys("{}，我{}吗？\n\n\n--from Account: {}, Status: {}.".format(
        name_one, desc_one, file_path.split(" ")[0], file_path.split(" ")[-1].replace("[", "").replace("].mp4", "")))

    time.sleep(2)

    elem = driver.find_element_by_xpath('//div[@data-testid="tweetButton"]')
    # elem = driver.find_element_by_xpath('//div[@role="button"]')
    elem.click()

    for times in range(60 * 2):
        current_url = driver.current_url
        if current_url == "https://twitter.com/home":
            os.remove(file_path)
            logging.info("成功转发")
            break
        if times == 119:
            logging.info("失败转发")
        #         elif elem.text == "无法处理你的媒体文件。":
        #             print("文件损坏！",file_path)
        #             os.remove(file_path)
        #             break
        time.sleep(1)

    # driver.current_url
    if glob(file_path):
        os.remove(file_path)

    time.sleep(np.random.choice(range(3, 10)))

    return file_path


def main():
    good_url_data = check()
    logging.info("Get {} URLS...".format(good_url_data.shape[0]))

    old_url = np.load("old_url.npy")
    new_url_data = good_url_data.loc[[x not in old_url for x in good_url_data["url"]]].copy()
    new_old_url = np.concatenate([old_url, new_url_data['url'].tolist()])
    np.save("old_url.npy", new_old_url)

    logging.info("Get {} useful URLS...".format(new_url_data.shape[0]))
    time.sleep(1)

    new_url_data["hash"] = new_url_data["pic"].apply(get_hash)
    new_url_data = new_url_data.groupby("hash").max().reset_index()

    old_hash = np.load("hash_list.npy")
    new_url_data = new_url_data.loc[[x not in old_hash for x in new_url_data["hash"]]]
    new_old_hash = np.concatenate([old_hash, new_url_data['hash'].tolist()])
    np.save("hash_list.npy", new_old_hash)

    logging.info("Get {} unique useful URLS...".format(new_url_data.shape[0]))

    time.sleep(1)

    new_url = new_url_data["url"].tolist()

    logging.info("Get URL...")
    for x in tqdm(new_url, desc="Download Videos."):
        os.system("/root/anaconda3/bin/you-get {}".format(x))

    ###
    # driver = webdriver.Remote(
    #     "http://{}:{}@hub.browserstack.com:80/wd/hub".format(BROWERSTACK_USERNAME, BROWERSTACK_PASSWORD))
    driver = webdriver.Chrome("/Users/frank/Documents/chromedriver")
    driver.set_window_size(600, 600)

    time.sleep(1)

    mp4_files = glob("*.mp4")
    if len(mp4_files) == 0:
        logging.info("No file to reblog...")
    else:
        login(driver)
        logging.info("Logining...")

        for file_path in tqdm(mp4_files,desc="Reblog file."):
            logging.info("Blog file is {}".format(file_path))
            if os.path.getsize(file_path) / (1024 * 1024) < 25:
                file_name = reblog(file_path, driver)
                if glob(file_path):
                    os.remove(file_path)
            else:
                os.remove(file_path)
                logging.info("File is too Big!")

        mp4_files = glob("/root/selenium_twitter/*.mp4")
        [os.remove(x) for x in mp4_files]

    driver.close()
    logging.info("DONE!!!")
    logging.info("---------------------------------------------------------------")


if __name__ == "__main__":
    main()