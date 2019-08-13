#!/usr/bin/env python3

import json
import os
import sys
import re

def load_channel_history(basedir, channelname):
    messages = []
    for root, dirs, files in os.walk(basedir):
        for fname in [fname for fname in files if fname.endswith(".json")]:
            f = json.load(open(os.path.join(root,fname)))
            messages.extend(f)
    return messages


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Sift, sort and find in slack exports')
    parser.add_argument('rootdir',
                    help='root directory of the slack export')
    parser.add_argument('text',
                    help='the text to search for in the message text')
    parser.add_argument('--who', action='store_true',
                    help='Instead of returning the message, return the userid who said it, or all who added reaction')
    parser.add_argument('--reactions', action='store_true',
                    help='search reactions')
    args = parser.parse_args()
    rootdir = args.rootdir
    messages = load_channel_history(rootdir, "security")
    found = []
    r = re.compile(f".*{args.text}.*")
    for message in messages:
        if args.reactions:
            if 'reactions' in message:
                for reaction in message.get('reactions'):
                    if r.match(reaction['name']):
                        found.append(message)
        else:
            if message.get('type', '') == 'message' and r.match(message.get('text','')):
                found.append(message)
    if args.reactions:
        if args.who:
            for msg in found:
                for reaction in msg.get('reactions'):
                    if r.match(reaction['name']):
                        for user in reaction['users']:
                            print(user)
        else:
            for msg in found:
                print(json.dumps(found, indent=2))

    else:
        if args.who:
            for msg in found:
                print(msg.get('user',''))
        else:
            print(json.dumps(found, indent=2))