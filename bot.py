import praw
import time

reddit = praw.Reddit(client_id = "LSYmE7bzxo9D3g", 
                    client_secret="eP13Rrvk-KeVbr3WO_YqOojary8lbA",
                    user_agent="windows:autoreply:v0.1 (by u/autoreplybottest",
                    username="autoreplybottest",
                    password="Spring1969")

while True:
    for message in reddit.inbox.unread():
        message.reply("hey bitch")
        message.mark_read()
        time.sleep(2)