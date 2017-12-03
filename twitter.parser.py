from bs4 import BeautifulSoup
import requests
import datetime
import json
import asyncio
import aiohttp

def get_users_from_status(html_soup):
    users=html_soup.findAll("a", attrs={"class":"account-group js-account-group js-action-profile js-user-profile-link js-nav"})
    return list(set([user["href"] for user in users]))

def get_qa_data_from_status(html_soup):
    status=html_soup.find("p", attrs={"class":"TweetTextSize TweetTextSize--jumbo js-tweet-text tweet-text"})
    comments=html_soup.findAll("p", attrs={"data-aria-label-part":"0",
                   "class":"TweetTextSize js-tweet-text tweet-text"})
    return status.text, [comment.text for comment in comments]

def get_users_data_from_status(html_soup):
    users=html_soup.findAll("a", attrs={"class":"account-group js-account-group js-action-profile js-user-profile-link js-nav"})
    return list(set([user["href"] for user in users]))

def get_id_post_from_user(html_soup):
    id_posts=html_soup.findAll("a", {"class":"tweet-timestamp js-permalink js-nav js-tooltip"})
    return list(set([id_post["href"] for id_post in id_posts]))

async def main_method(user_list, qa_queue, num, max_users):
    while True:
        async with aiohttp.ClientSession() as session:
            print("start main_method # " + str(num))
            print("len(user_list) = " + str(len(user_list)))
            print("len(qa_queue) = " + str(len(qa_queue)))
            if len(user_list) == 0 : break
            user_current = user_list.pop()
            response = await session.get(HOST + user_current)
            data = await response.text()
            html_soup = BeautifulSoup(data, "lxml")
            post_list = get_id_post_from_user(html_soup)
            for post in post_list:
                response = await session.get(HOST + post)
                data = await response.text()
                html_soup = BeautifulSoup(data, "lxml")
                question, answer = get_qa_data_from_status(html_soup)
                qa_queue.append({"question" : question, "answer" : answer})
                users = get_users_data_from_status(html_soup)
                if len(user_list) < max_users:
                    user_list += users

async def save_json(dialog_queue, num_note_json):
    dict_data = {}
    n_mess = 0
    while True:
        print("start save_json")
        if len(dialog_queue) >= num_note_json:
            print("n_mess : %d" % n_mess)
            for i in range(num_note_json):
                note = dialog_queue.pop()
                dict_data["data_" + str(i)] = note

            with open("tweets_new/data_" + str(datetime.datetime.now()).replace(" ", "_") + ".json", 'w') as outfile:
                json.dump(dict_data, outfile, ensure_ascii=False)
            n_mess += 1
        else:
            await asyncio.sleep(100.0)



user_list = []
qa_list = []
HOST = "https://twitter.com"
num_note_json = 100
max_users = 500

user_list += ["/meduzaproject", "/Kaspersky_ru‏"]

futures = [main_method(user_list, qa_list, num, max_users) for num in range(2)]
futures += [save_json(qa_list, num_note_json)]
print(futures)
loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.wait(futures))