#!/usr/bin/env python3

import json
import os
import sys
import re
from collections import defaultdict

def load_channel_history(basedir):
    messages = defaultdict(list)
    for root, dirs, files in os.walk(basedir):
        _, dirname = os.path.split(root)
        for fname in [fname for fname in files if fname.endswith(".json")]:
            f = json.load(open(os.path.join(root,fname)))
            messages[dirname].extend(f)
    return messages

def show_message_raw(msg):
    print(json.dumps(msg, indent=2))

def show_message_foimode(msg):
    print(f"Timestamp: {msg.get('ts')} Channel: {msg.get('channel', '')} User: {msg.get('user','')} Text:\n{msg.get('text','')}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Sift, sort and find in slack exports')
    parser.add_argument('rootdir',
                    help='root directory of the slack export')
    parser.add_argument('text',
                    help='the text to search for in the message text')
    parser.add_argument('--foimode', action='store_true',
                    help='Return each message that is found')
    parser.add_argument('--threaded', action='store_true',
                    help='Return the thread for each message that is found (not implemented)')
    parser.add_argument('--who', action='store_true',
                    help='Instead of returning the message, return the userid who said it, or all who added reaction')
    parser.add_argument('--reactions', action='store_true',
                    help='search reactions')
    args = parser.parse_args()

    print("Reading in slack data dump")
    channels = load_channel_history(args.rootdir)
    found = []
    msgdb = {}
    threaddb = defaultdict(list)
    seenthreads = set()
    show_message = show_message_raw
    if args.foimode:
        show_message = show_message_foimode
    r = re.compile(f".*{args.text}.*")

    print("Processing Messages")
    for chan,messages in channels.items():
        for message in messages:
            # Weirdly, slack doesn't reference the channel in the message itself
            message["channel"] = chan
            if args.reactions:
                if 'reactions' in message:
                    for reaction in message.get('reactions'):
                        if r.match(reaction['name']):
                            found.append(message)
            else:
                if message.get('type', '') == 'message' and r.match(message.get('text','')):
                    found.append(message)
                    if args.threaded and "thread_ts" in message:
                        seenthreads.add(message["thread_ts"])
            if args.threaded:
                # We need a message database to build threads from, so build lookup tables
                if "client_msg_id" in message:
                    msgdb[message["client_msg_id"]] = message
                if "thread_ts" in message:
                    threaddb[message["thread_ts"]].append(message)

    # Display results
    if args.reactions and args.who:
        for msg in found:
            for reaction in msg.get('reactions'):
                if r.match(reaction['name']):
                    for user in reaction['users']:
                        print(user)
    else:
        if args.threaded:
            for thread in seenthreads:
                print(f"\n\n=========\nThread {thread}")
                for msg in threaddb[thread]:
                    show_message(msg)
        else:
            for msg in found:
                show_message(msg)
