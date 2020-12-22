import praw, emoji, random, time, atexit, traceback
from replycount import ReplyCount
from collections import deque

"""
Return random emoji from list.
"""
def random_emoji():
    emojis = []
    emojis.append(emoji.emojize("Hello :thumbs_up:"))
    emojis.append(emoji.emojize("Howdy :red_heart:"))
    emojis.append(emoji.emojize("No :middle_finger:"))
    return emojis[random.randint(0, len(emojis)-1)]


"""
Reply to a comment if thread has less replies than the limit.

:param message: comment to reply to, instance of PRAW message class.
:param replies: dictionary with reply counts
"""
def comment_reply(message, reply_dict, oldest_replies, MAX_REPLIES):
    parent = message.parent_id

    # Initialize reply counter for new threads
    if parent not in reply_dict:
        timestamp = int(time.time())
        reply_dict[parent] = ReplyCount(1, timestamp)
        oldest_replies.append((parent, timestamp))
        message.reply(random_emoji())
    
    # Increment for existing threads under the reply limit
    elif parent in reply_dict and reply_dict[parent].count <= MAX_REPLIES:
        timestamp = int(time.time())
        reply_dict[parent].increment(timestamp)
        oldest_replies.append((parent, timestamp))
        message.reply(random_emoji())

    print("printing new reply dict")
    for reply in reply_dict:
        print("id " + reply + " count " + str(reply_dict[reply].count) + " age " + str(reply_dict[reply].age))
    print("printing new reply deque")
    for reply in oldest_replies:
        print("id " + str(reply[0]) + " age " + str(reply[1]))

"""
Process an incoming message, replying if appropriate

:param message: message to process, instance of PRAW message class.  Can be 
either a direct message or comment.
:param replies: dictionary of threads with the number of times replied in
each thread.
"""
def process_message(message, reply_dict, oldest_replies, MAX_REPLIES):
    # Don't reply to mods or employees
    if message.author.is_employee or message.author.is_mod:
        return None

    # Don't reply to bots
    if "bot" in message.author.name:
        return None

    # Reply to top-level comments
    if message.was_comment and message.parent_id.startswith("t3"):
        comment_reply(message, reply_dict, oldest_replies, MAX_REPLIES)
        message.mark_read()

    # Reply to messages
    else:
        message.reply("I don't message here, but email me!")
        message.mark_read()


"""
Logs reply data to file, run at exit

:param oldest_replies: deque of replies sorted from oldest to newest.  Each
entry has the form (id, age)
:param replies: dictionary of replies keyed by thread id
"""
def log(reply_dict, oldest_replies):
    # Log all entries in oldest_replies
    log_file = open("replies_log.txt", "w")
    for log in oldest_replies:
        id = log[0]
        age = log[1]

        # Don't write out-of-date logs, they will have a duplicate later in deque
        if age == reply_dict[id].age:
            line = id + " " + str(reply_dict[id].count) + " " + str(reply_dict[id].age) + "\n"
            log_file.write(line)
    
    log_file.close()

"""
Real-time cleanup function to prune any outdated replies from data structures.

:param oldest_replies: deque of replies sorted from oldest to newest.  Each
entry has the form (id, age)
:param reply_dict: dictionary of replies keyed by thread id
"""
def cleanup(oldest_replies, reply_dict):
    # Remove all replies older than a week
    while len(oldest_replies) > 0 and time.time() - oldest_replies[0][1] > 604800:

        # Get reply data and pop from queue
        id = oldest_replies[0][0]
        age = oldest_replies[0][1]
        oldest_replies.popleft()

        # If there's no newer reply in thread, remove from dict
        if reply_dict[id].age == age:
            reply_dict.pop(id)

"""
Main function, responds to any unread messages then replies to any new
incoming messages in a stream.
"""
def main():

    # Maximum number of comments to leave in a thread
    MAX_REPLIES = 2

    # Read in replies from file
    reply_dict = {}
    oldest_replies = deque()
    try:
        replies_log = open("replies_log.txt", "r")
        for line in replies_log:

            # Parse line from file
            parsed = line[:-1].split()
            id = parsed[0]
            count = ReplyCount(int(parsed[1]), int(parsed[2]))

            # Disregard old logs, add newer logs to reply dict
            if int(time.time()) - count.age < 604800:
                reply_dict[id] = count
                oldest_replies.append((id, count.age))

        replies_log.close()

    # Log file not found, leave replies empty
    except:
        print("error during parsing")
        traceback.print_exc()

    # Initialize reddit client (authorization info needs to be added)
    reddit = praw.Reddit()

    # Register logging function for program exit
    atexit.register(log, reply_dict, oldest_replies)

    # Catch up on any missed messages
    for message in reddit.inbox.unread():
        process_message(message, reply_dict, oldest_replies, MAX_REPLIES)

    # Process new messages as they come in
    for message in reddit.inbox.stream():
        process_message(message, reply_dict, oldest_replies, MAX_REPLIES)
        cleanup(oldest_replies, reply_dict)


if __name__ == "__main__":
    main()