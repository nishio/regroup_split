#!/usr/bin/env python3
import sys
import re

data = sys.stdin.read()
if not data.endswith("\n"):
    data += "\n"


TWITTER_IGNORES = """
ツイートする
新しいツイートを表示
会話
引用ツイート
""".strip().split("\n")


def twitter_to_scrapbox(data):
    result = ""
    data = re.sub(r"ツイートアクティビティを表示[\s\d]+リツイート[\s\d]+いいねの数", "", data)
    data = re.sub(r"午後\d+:\d+ · \d+年\d+月\d+日·Twitter for iPhone", "", data)
    data = re.sub(r"· \d+月\d日", "", data)
    data = re.sub(r".+\n(@.+)\n\s*·.*\n\d.+\n", r"\1", data)
    data = re.sub(r".+\n(@.+)\n", r"\1", data)
    data = re.sub(r"返信先: \n@.+\nさん", "", data)

    for line in data.split("\n"):
        line = line.strip()
        if not line:
            continue
        if line in TWITTER_IGNORES:
            continue
        result += line + "\n"

