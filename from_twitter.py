#!/usr/bin/env python3
import sys
import re

TWITTER_IGNORES = """
ツイートする
新しいツイートを表示
会話
引用ツイート
""".strip().split("\n")


def twitter_to_scrapbox(data):
    result = ""
    data = re.sub(r"ツイートアクティビティを表示[\s\d]+リツイート[\s\d]+いいねの数", "", data)
    data = re.sub(r"午(前|後)\d+:\d+ · \d+年\d+月\d+日·.*", "", data)
    data = re.sub(r"· \d+月\d日", "", data)
    data = re.sub(r".+\n(@.+)\n\s*·.*\n\d.+\n", r"\1\n", data)
    data = re.sub(r"返信先: \n@.+\nさん", "", data)
    #data = re.sub(r"\n(@.+)\n", r"\1\n", data)

    for line in data.split("\n"):
        print("line", repr(line))
        line = line.strip()
        if not line:
            continue
        if line in TWITTER_IGNORES:
            continue
        result += line + "\n"
    return result


def main():
    data = sys.stdin.read()
    if not data.endswith("\n"):
        data += "\n"
    print(twitter_to_scrapbox(data))


if __name__ == "__main__":
    main()
