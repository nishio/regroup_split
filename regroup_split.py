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
            and "？" not in t.surface
            and "！" not in t.surface
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
」 に対する
として
という こと だ と
ん だ けど 、
」 の
は 、
だ 」 と
する よう な  もの
と 、
と  いう と
だ 。
に も
だろ う 、 と
だろ う
に は
ね
思っ て いる
だろ う
によって
に  なる 。
ため だ し 、
の も
ため 。
の で 、
ため に
や 、
で は ある
よう に なる 。
の
思う ので 、
な ん じゃ ない か と
に 、
が 、
か な
すれ ば 、
ね 。
し て 、
だろ う 。
けど 、
とか 、
ので 、
ー 、
… 。
けど … 。
…
わけ な の だ が …
わけ な の だ が
な ので
な ん だ けど 、
と
思う
)
し 、
とき も
ところ だっ た
あっ て
よう に なる の だ
な
もの だっ た 。
な の だ が 、
の だ 。
な 訳 だ 。
で 、
こと に  なる 。
こと に  なる 。
する
思う が 、
ある 。
いう なら
いう なら 、
言う なら
」
だ けども 。
いい です ね
で ある
だ ね 。
な 。
し たり
し たり 、
とかし て 、
ある 。
わけ だ から 。
感じ
よ ね 。
なん だろ う 。
、 そして
そして
」 という
の を
だ ね
""".strip().splitlines()

FIRST_TOKENS_TO_REMOVE = """
そして
たとえば
確か に 、
あえて
なん なら
だいたい
一方 で
こっち
(
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
そもそも
この
うーん 、
あー
なるほど
うーん
( この
""".strip().splitlines()

# memo for REPLACE, not implemented yet
"""
ある わけ じゃ なく て > ない
やる の で は なく > やらない
良 さ そう > 良い
あっ て > ある
い て > いる
強く て > 強い
使っ て き て
比べ て > 比べ
難しく 、
なく て 、
でき て
"""
"""
し て
に し > にする
まとめ て
まとめ られ て
必要なのでは？ 必要？
こだわってきた こだわり
がついてなかった なし
ことによって解決される と解決
入れてしまって 入れてしまう
てもいいかも る？
があるわけじゃなくて、 ない
良さそう 良い
なっ ちゃっ てる けど 、
し たり  できる
"""

"""
ある  種 の  情報処理 で は ある

"""

if __name__ == "__main__":
    if args.develop:
        sample_lines = """
Regroupのために長文を分割する機能を実装したんだけど、これってこのチャットシステムとの連携に有益なんじゃないかと思うので、話して頭を整理したい
長文分割の機能とチャットシステムの言語化の機能に、何かつながりがありそうな気がしているが、それが何であるかをまだ言葉にできてなくて、それを言葉にすること
あー、なるほど、そういう意味ではチャットシステムが先にあって、チャットシステムの質問によって引き出された回答が長文分割で刻まれる
うーん、遊びではなくガチで業務上の有益さがあるチャットシステムかな
経済的な利益を発生させることができるといいよね
顧客に利益が発生すれば、その利益のいくらかを対価として受け取ることができて、開発が加速する
うーん、厳しい。確かに知りようがないね。顧客の継続利用に有料プランを用意して、それを使い続けてくれるなら払い続けるに足る利益が顧客に生まれてると推測できるだろう。
金銭的利益を最初はイメージしていたけど、もっと広く、顧客の満足感とか、知的な楽しさなどを含む概念
わからない、顧客の手元？
なんか顧客と利益の話になっちゃってるけど、今のところまだ商用プランは予定してないので、当面は僕と限られたベータテスターぐらい。あと、掘り下げたかった長文分割の話に戻って欲しい
ここでこの質問かー、長文分割についての掘り下げが足りないと思うけど…。長文分割機能に価値を感じてて、それを掘り下げにきたわけなのだが…
今はチャットの形なのでただの長文なんだけど、これが分割されて付箋になって画面に配置されていくと良いと思う
(スマホでは使いにくくなるけど)
チャットシステムからのフィードバックは今は質問の文字列の形でしかないのだけど、長文分割して付箋になって画面に配置されると、人間はそれを動かすことで頭の整理ができるし、チャットシステムが特定のキーワードに注目させるときも付箋をハイライトしたりできる
(なるほど、ここまでの連携はまだ考えてなかった)
(この同じですか違いますか質問はよくないので直そうと今日思いついたところだった)
このチャットシステムと長文分割の関係はどのようなものですか？チャットではない別の表示システムがあって、長文分割を通してそちらへデータを流せるようになるのだ
今までのチャットシステムはカウンセラーと口頭で話してるみたいなものだった。さっき思いついた連携を取り込んだ後は、ホワイトボードを使って議論を整理してくれるファシリテーターとかコンサルタントみたいな感じになる
今ローカルスクリプトとして動いてるけどweb APIになるべきだね
こっちはもっと大幅な変更が必要。チャットボットの形のままで良いのかも疑問。ホワイトボードシステムに組み込んだ方がいいかも？一方でスマホからの使いやすさって点では今の形がホワイトボードよりも良い
チャットシステム単体でも使いたいし、ホワイトボードと接続しても使いたいので、疎結合にして切り替えられるようにして、なんなら事後的に接続できる仕組みが必要だ
世の中の商業的なチャットシステムは、だいたい企業の側がデータをあらかじめ用意して、その企業の顧客がチャットシステムに質問し、回答を得る仕組みなのだが、このシステムはデータの用意が必要なくて、チャットシステムが質問をして、データが事後的に溜まるのだ。今の実装だと一回のセッションで消去されるけど、これが企業内でずっと蓄積し共有できるようになるとさらに面白いことが起こるかもしれない。つまりこれはグループウェアのビジネスモデルな訳だ。
顧客がいなければ僕一人がユーザーで、趣味でのんびり開発することになる。顧客がいると、より新機能追加よりも安定性を重視することになる。個人的には楽しくないと思うが、顧客がついて支払いがあるとプロジェクトが加速する側面もある。
違います。あえていうならチャットシステムを「人を含めた知的生産システム」と見た場合は顧客はチャットシステムの部品だけども。
使うことによって知的生産性が高まるといいですね
支払いによって開発が加速する
信頼関係？
違う。あえていうなら、利益はチャットシステムを成長させるための餌である
顧客のビジネスが加速されて顧客の得る利益が増えて欲しい
支払いで加速するだけじゃなくて「このアイデアはこのシステムを使って生み出されました」って事例を提供してもらえると良い
正のフィードバックだね。
正のフィードバックが成長の原動力
違う、あえて言うなら成長の加速度だ
確かに、成長はチャットシステムに必須なものではないな。どんどん機能追加するよりも、たとえばリファクタリングしたり、別のコードベースに移植したりとかして、成長ではなく長生きのためにリソースを使う選択肢もある。
僕が作ってます
チャットシステムを作って使うことによって僕の知的生産性が向上する
ある意味かなり近い。僕が習得したカウンセリングの技術をプログラムにして、また今度僕のコンサルティングの技術をプログラムにして、とやってくわけだから。僕のサブセットを電子化してる感じ
僕によって生まれて、成長するよね。
なんだろう。「もっと育ってくれる、そして僕を助けてくれる」という期待かな
僕の知的生産性が向上する
知的生産性が向上するとチャットシステムの機能も向上する
人間とチャットシステムを組み合わせた知的生産システムが知的生産してる
人間とチャットシステムの組み合わせが知的生産をするようになった上で、その力でシステムをどんどん改善していって、人間がだんだん弱っていくのをシステムが肩代わりした挙句に人間が死んだ時、何が残るのか…
融合だね
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
