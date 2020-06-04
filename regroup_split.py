#!/usr/bin/env python3
import argparse
import sys
import re
from cabocha.analyzer import CaboChaAnalyzer
analyzer = CaboChaAnalyzer()

parser = argparse.ArgumentParser()
parser.add_argument('--test', '-t', action="store_true")
parser.add_argument('--develop', '-d', action="store_true")
parser.add_argument('--verbose', '-v', action="store_true",
                    help="show verbose output in testing")
args = parser.parse_args()


def cabocha_split(s):
    ret = []
    tree = analyzer.parse(s)
    start = 0

    def to_connect(i):
        t = tree[i]
        return (
            # next node is adjacent
            t.next_link_id == i + 1
            and
            # this node dont have closing brace
            "」" not in t.surface
            and "、" not in t.surface
            and "。" not in t.surface
        )
    while start < tree.chunk_size:
        i = start
        buf = [tree[i]]
        while True:
            if to_connect(i):
                i += 1
                buf.append(tree[i])
            else:
                break
        # print(start, buf, tree[i].next_link_id)
        ret.append(buf)
        start = i + 1

    return ret


def trim_tail(block):
    while block:
        last_chunk = block[-1]
        tokens = trim_last_chunk(last_chunk)
        if tokens:
            break
        block = block[:-1]
    if not block:
        if args.develop:
            print("all removed\n")
        return []
    block[-1].tokens = tokens
    return block


def trim_head(block):
    while block:
        fist_chunk = block[0]
        tokens = trim_first_chunk(fist_chunk)
        if tokens:
            break
        block = block[1:]
    if not block:
        if args.develop:
            print("all removed\n")
        return []
    block[0].tokens = tokens
    return block


def main():
    data = sys.stdin.read()
    if not data.endswith("\n"):
        data += "\n"

    for line in data.split("\n"):
        print(line)
        for block in split_and_trim(line):
            s = "".join(x.surface for x in block)
            print(s)
        print()


def split_and_trim(line):
    result = []
    for block in cabocha_split(line):
        block = trim_tail(block)
        block = trim_head(block)
        if block:
            result.append(block)
    return result


def test():
    testdata = open("test/regroup_split.txt")
    state = "WAIT_INPUT"
    items = []
    for line in testdata:
        line = line.strip()
        if line.startswith("#"):
            continue
        if not line:
            if items:
                print(
                    f"for {input_data}:\n  did not get all answer, {items}")
            state = "WAIT_INPUT"
            continue
        if state == "WAIT_INPUT":
            input_data = line
            items = ["".join(x.surface for x in block)
                     for block in split_and_trim(line)]
            if args.verbose:
                print(input_data)
                for x in items:
                    print(x)
                print()
            state = "WAIT_EXPECTED"
        else:
            if items and items[0] == line:
                # OK
                items.pop(0)
            elif not items:
                # NG
                print(
                    f"for {input_data}:\n  got unexpected: {line}")

            else:
                # NG
                print(
                    f"for {input_data}:\n  expected: {line}, got: {items[0]}")
                items = []


def trim_last_chunk(chunk):
    if args.develop:
        print(chunk.tokens)
    tokens = chunk.tokens
    is_matched = False
    longest_match = 0
    for phr in LAST_TOKENS_TO_REMOVE:
        phr = phr.split()
        i = -1
        for p in reversed(phr):
            # print(i, p)
            if -i == len(tokens) + 1:
                break
            if tokens[i].surface != p:
                break
            i -= 1
        else:
            if args.develop:
                print(phr, i, "match!")
            is_matched = True
            if i < longest_match:
                longest_match = i
    if is_matched:
        tokens = tokens[:longest_match+1]
        if args.develop:
            print(tokens)
    return tokens


def trim_first_chunk(chunk):
    if args.develop:
        print(chunk.tokens)
    tokens = chunk.tokens
    is_matched = False
    longest_match = -1
    for phr in FIRST_TOKENS_TO_REMOVE:
        phr = phr.split()
        i = 0
        for p in phr:
            # print(i, p)
            if i == len(tokens):
                break
            if tokens[i].surface != p:
                break
            i += 1
        else:
            if args.develop:
                print(phr, "match!")
            is_matched = True
            if i > longest_match:
                longest_match = i
    if is_matched:
        tokens = tokens[longest_match:]
        if args.develop:
            print(tokens)
    return tokens


# if the join of last tokens in a chunk is in this list, remove it
LAST_TOKENS_TO_REMOVE = """
、
し た ん だ けど 、
でも って 、
こと によって 、
の 、
件 に関して は 、
も 、
。
行なっ て い た 。
だっ た 。
な の だ な 。
やつ 。
が
」 が
こと が
の が
この
する
よう に する
って
！ 」 って
と で
と
、 と
の だ な 、 と
こと と
という
だ 」 という
に
」 に
こと に
こと によって
件 に関して
こと 」 の
なぁ 」 の
は
の は
を
と
思っ た
だ
考え て い た
な のに
で あっ て
な の だ
な のに
だ
だ と
な のに 、
な の は
し て い た 。
し て い た の だ な
し て い た の だ
する 。
こと とか 、
という 意味 で は
って 思う の 、
の だ けど 、
から
」 を
」 は
よ ね
な の だ な
で
かも
で は
の か ？
けど
ので
""".strip().splitlines()

FIRST_TOKENS_TO_REMOVE = """
「
別に
「 おっ
その
それ を
本質 的 な
そういう
これ は
これ
それ
本質 的
本質 的 な
本質 的 に
これ が
それ は
そうすると
あ
そこ の
""".strip().splitlines()

# memo for REPLACE, not implemented yet
"""
ある わけ じゃ なく て > ない
やる の で は なく > やらない
良 さ そう > 良い
"""
"""
必要なのでは？ 必要？
こだわってきた こだわり
がついてなかった なし
ことによって解決される と解決
入れてしまって 入れてしまう
てもいいかも る？
があるわけじゃなくて、 ない
良さそう 良い
"""


"""
自分の思考のバイアスを改めて痛感したんだけど、ゲーム時間制限条例が作られた結果、実際にゲーム時間が減少していることがデータで示された、と聞いて最初におもったのは「おっ、ゲームの影響を知ることができる大規模社会実験だ」というポジティブな気持ちだった。
「自分以外の一部の人間が権利を剥奪されること」のマイナスと「文明が知識を手に入れること」のプラスとで後者を大きく見積もりがちなのだな。
でもって、この件に関して権利を剥奪された側の高校生が自治体を訴えたニュースを見ると「いいぞいいぞ！」って思うの、別に高校生の権利が回復されることに興味があるわけじゃなくて、高校生による提訴って「実験」が行われたこととその「実験結果」に興味があるのだな、と思った
    逆に言えば「部分的再描画できるようにしたいなぁ」の件に関しては、今僕がやるのではなくRecoilチームの成果が出てきてから乗り換えるのが良さそう
"""


if __name__ == "__main__":
    if args.develop:
        sample_lines = """
Xという意味では
""".strip().splitlines()

        for line in sample_lines:
            for block in cabocha_split(line):
                print("  ".join(" ".join(x.surface for x in chunk)
                                for chunk in block))
                while block:
                    last_chunk = block[-1]
                    tokens = trim_last_chunk(last_chunk)
                    if tokens:
                        break
                    block = block[:-1]
                if not block:
                    print("all removed\n")
                    continue
                block[-1].tokens = tokens

                while block:
                    fist_chunk = block[0]
                    tokens = trim_first_chunk(fist_chunk)
                    if tokens:
                        break
                    block = block[1:]
                if not block:
                    print("all removed\n")
                    continue
                block[0].tokens = tokens

                print(
                    "".join(x.surface for x in block)
                )
                print()
    elif args.test:
        test()
    else:
        main()
