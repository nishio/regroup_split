#!/usr/bin/env python3
import sys
import re

MATTERMOST_IGNORES = """
q""".strip().split("\n")


def twitter_to_scrapbox(data):
    result = ""
    data = re.sub(r".* profile image	", "", data)
    data = re.sub(r"午(前|後)\d+:\d+.*\n", "", data)
    data = re.sub(r"nisbot\nBOT\n", "[nisbot.icon]", data)
    data = re.sub(r"\nnishio\n", "\n[nishio.icon]", data)
    data = re.sub(r"\n今日\n", "\n", data)

    for line in data.split("\n"):
        line = line.strip()
        if not line:
            continue
        if line in MATTERMOST_IGNORES:
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
