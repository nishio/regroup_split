#!/usr/bin/env python3
import sys
import re

FACEBOOK_IGNORES = """
いいね！
コメント
シェアする
コメント
編集または削除
コメントを削除または非表示にします
返信する…
コメントする…
非表示または報告
""".strip().split("\n")


def facebook_to_scrapbox(data):
    result = ""
    data = re.sub(r"\d+月\d+日 \d+:\d+ ·\s*\n", "", data)
    data = re.sub(r"\d+分前 ·\s*\n", "", data)
    data = re.sub(r"\d+時間前 ·\s*\n", "", data)
    data = re.sub(r"\d.*他\d+人\n", "", data)
    data = re.sub(r"コメント\d+件\n", "", data)
    data = re.sub(r"\d+\n", "", data)
    data = re.sub(r"· 返信する · .*\n", "", data)

    prev_line = "DUMMY"
    for line in data.split("\n"):
        line = line.strip()
        if not line:
            continue
        if line in FACEBOOK_IGNORES:
            continue
        if line.startswith(prev_line):
            # Facebook repeats author name. Remove it.
            line = line[len(prev_line) + 1:]
        result += line + "\n"
        prev_line = line
    return result


def main():
    data = sys.stdin.read()
    if not data.endswith("\n"):
        data += "\n"
    print(facebook_to_scrapbox(data))


if __name__ == "__main__":
    main()
