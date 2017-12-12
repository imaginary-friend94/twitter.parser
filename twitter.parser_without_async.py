from bs4 import BeautifulSoup
import requests
import datetime
import json
import pickle
import os
import time

class Bot():
    def __init__(self, id_chat, token, url):
        self.id_chat = id_chat
        self.token = token
        self.url = url

    def plot(self, X, y, caption=""):
        plt.figure()
        plt.plot(X, y)
        plt.savefig("d.png")
        data = {'chat_id': self.id_chat, 'caption': caption}
        multiple_files = [('photo', ('d.png', open('d.png', 'rb'), 'image/png'))]
        requests.post(self.url + self.token + '/sendPhoto', files=multiple_files, data=data)

    def sendMessage(self, mess):
        data = {'chat_id': 212076743, 'text': mess}
        requests.post(self.url + self.token + '/sendMessage', data=data)

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

def main_method(user_list, qa_queue, max_users, user_old):
    print("start : main_method")
    print("len(user_list) = " + str(len(user_list)))
    print("len(qa_queue) = " + str(len(qa_queue)))
    if len(user_list) == 0 : exit(-1)
    user_current = user_list.pop()
    user_old.add(user_current)
    with open('names_twitter.pickle', 'wb') as f:
        pickle.dump(user_old, f)
    response = requests.get(HOST + user_current)
    data = response.text
    html_soup = BeautifulSoup(data, "html.parser")
    post_list = get_id_post_from_user(html_soup)
    for post in post_list:
        response = requests.get(HOST + post)
        data = response.text
        html_soup = BeautifulSoup(data, "html.parser")
        question, answer = get_qa_data_from_status(html_soup)
        if answer != []:
            qa_queue.append({"question" : question, "answer" : answer})
        users = get_users_data_from_status(html_soup)
        if len(user_list) < max_users:
            for user in users:
                if not user in user_old:
                    user_list.append(user)

def save_json(dialog_queue, num_note_json):
    dict_data = {}
    n_mess = 0
    print("start save_json")
    if len(dialog_queue) >= num_note_json:
        print("n_mess : %d" % n_mess)
        for i in range(num_note_json):
            note = dialog_queue.pop()
            dict_data["data_" + str(i)] = note

        with open("twitter_new/data_" + str(datetime.datetime.now()).replace(" ", "_") + ".json", 'w') as outfile:
            json.dump(dict_data, outfile, ensure_ascii=False)
        n_mess += 1

user_list = []
qa_list = []
HOST = "https://twitter.com"
num_note_json = 100
max_users = 500
every_iter = 60 * 60

user_list += ["/omruruch", "/Kaspersky_ru‏", "/fuckingsun"]
print(os.listdir(os.getcwd()))
if "names_twitter.pickle" in os.listdir(os.getcwd()):
    with open('names_twitter.pickle', 'rb') as f:
        user_old = pickle.load(f)
else:
    user_old = set()

time_old = time.time()
URL = 'https://api.telegram.org/bot'
TOKEN = '165945149:AAEoZmeVW_s8XM4QVLiZ5TgGhBhE8a_AEpc'
bot = Bot(212076743, TOKEN, URL)
bot.sendMessage("start")

while True:
    if time.time() - time_old > every_iter:
        time_old = time.time()
        bot.sendMessage("file num # {}".format(len(os.listdir("twitter_new/"))))
    try:
        main_method(user_list, qa_list, max_users, user_old)
        save_json(qa_list, num_note_json)
    except AttributeError:
        pass
