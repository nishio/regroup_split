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
そもそも
この
うーん 、
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
"""

"""
ある  種 の  情報処理 で は ある

"""

if __name__ == "__main__":
    if args.develop:
        sample_lines = """
	この会話で何が起きて欲しいですか？
		自作ソフトのデモ動画を作ってるんだけど、「グループ化」の機能がなぜ重要なのかについての説得力のある説明がしたい
	その説得力は、どんな種類の説得力ですか？
		聴衆が「なるほど、確かにグループ化の機能が必要だ」と納得するようなもの
	そのグループ化は、どんな種類のグループ化ですか？
		複数の付箋を選択して、1つのグループにまとめて、表札をつける。
	グループ化について、他に何かありますか？
		ワンクリックで閉じたり開いたりできる。
	グループ化は、どこにありますか？
		グループ化のボタンはツールバーにある。
	そのグループ化は、どのあたりにありますか？
		アクセスしやすいところにある。
	グループ化は、何のようですか？
		(この質問はNGだな)
		僕はグループ化を圧縮にたとえている。あと、プログラミングに例えると、複数のコードが1つの関数にまとめられて、それに処理の内容をうまく表現した関数名がつくのがグループ化に似ている。
	あなたはそのグループ化をどう知るのですか？
		(うーむ)
		グループ化の概念をどうやって知ったかというと川喜田二郎の発想法って本で知った
	その川喜田二郎は、どんな種類の川喜田二郎ですか？
		文化人類学者でKJ法の発明者
	あなたが価値を感じているのは何ですか？
		グループ化だ。僕はKJ法を自分の知的生産に使ってきて、その価値を痛感している。だから自作ソフトにもその機能を入れた。この価値を聴衆に納得させたい。
	そのグループ化と聴衆の関係は何ですか？
		聴衆はグループ化の経験も少なく価値も理解してないだろう、と思ってたけどこの思い込みには根拠はないね
	そのグループ化と、聴衆とは同じですか？違いますか？
		違います
	グループ化の時、聴衆に何が起こりますか？
		グループ化をすると、聴衆は生身の状態と比較して、より大量の情報を処理することができる
	その聴衆の時、グループ化に何が起こりますか？
		グループ化は、その価値をより多くの人に理解される
	そのグループ化と聴衆の間には何がありますか？
		現状ではギャップがあるだろうと思っている
	グループ化と価値の関係は何ですか？
		グループ化は、より大規模な情報処理を可能にし、その結果、グループ化を使える人は使えない人に比べて新しいものを生み出す確率が高まる。これが価値を生み出す。
	そのグループ化と、価値とは同じですか？違いますか？
		ほぼ同じ。グループ化が価値をもたらす。
	そのグループ化の時、価値に何が起こりますか？
		高める
	価値の時、グループ化に何が起こりますか？
		価値が生み出された後、それがグループ化によって生み出されたということによって、グループ化の有用性が事後的に示される
	そのグループ化と価値の間には何がありますか？
		(そうか、価値が先か)
		グループ化によって価値を生み出し、その価値が生み出されたことによって、事後的にグループ化の価値を世の中の人が納得していく
	そのグループ化と機能の関係は何ですか？
		(機能ってなんだっけ)
		同じもの
	グループ化と、機能とは同じですか？違いますか？
		同じ
	グループ化の時、機能に何が起こりますか？
		(同じと答えてる時にこの種の関係の質問は良くないね)
		NG
	機能の時、グループ化に何が起こりますか？
		NG
	グループ化と機能の間には何がありますか？
		NG
	グループ化と自作の関係は何ですか？
		僕が満足するグループ化の機能のソフトがないから自作した
	そのグループ化と、自作とは同じですか？違いますか？
		グループ化機能のある付箋空間配置ツールを自作した
	そのグループ化の時、自作に何が起こりますか？
		なるほど。グループ化によってより高度な情報処理ができるようになることで、この自作ソフトがより良いものになって、価値を生み出す
	その自作の時、グループ化に何が起こりますか？
		自作ソフトによってグループ化が低コストになる。アクセスしやすいツールバーにあるのもそのためだし、ワンクリックで開閉するのもそのため。紙でKJ法してると、物理的に束ねたり広げたりが必要で高コスト。
	そのグループ化と自作の間には何がありますか？
		(何があるかな…)
		グループ化の概念を学び、紙で実践し、価値を痛感しつつも不満も溜まったので、不満を解消して価値を得るために自作ソフトの開発を始めた
	そのグループ化とKJ法の関係は何ですか？
		グループ化はKJ法の一番重要なピースだ。そして一番教えるのが難しく、その結果一番ないがしろにされてる。
	そのグループ化と、KJ法とは同じですか？違いますか？
		まったく同じではない。KJ法がグループ化を多用している。
	そのグループ化の時、KJ法に何が起こりますか？
		新しい発想が生み出される
	KJ法の時、グループ化に何が起こりますか？
		なんども使われる
	グループ化とKJ法の間には何がありますか？
		(何があるかなぁ、包含してるんだけどw
		グループ化をひたすら繰り返して、それから展開をして図解化、文章化する、これがKJ法
	そのグループ化と図解化の関係は何ですか？
		まず関係しそうなものを近くに置いて、それから近くに置かれたものをグループ化する、この時点でグループの境界が明確になる、その明確な境界や、境界をまたぐ関係を記録するのが図解化
	そのグループ化と、図解化とは同じですか？違いますか？
		強く関連してるけど同じではない
	グループ化とツールバーの関係は何ですか？
		すぐ使えるようにした
	グループ化と情報処理の関係は何ですか？
		グループ化によって情報処理が支援される
	そのグループ化と、情報処理とは同じですか？違いますか？
		グループ化はある種の情報処理ではある
	そのグループ化の時、情報処理に何が起こりますか？
		効率化される。生身の人間のキャパシティを超える量の情報を扱えるようになる。
	情報処理の時、グループ化に何が起こりますか？
		うーん、それがうまくいけばグループ化が評価される
	そのグループ化と情報処理の間には何がありますか？
		(これも包含してるんだけどw
		情報処理の一種に「整理」があり、その整理の具体的方法にグループ化がある
	そのグループ化と整理の関係は何ですか？
		(そう聞くよねw
		複数のものをまとめて、一つの箱に入れる、ってのは整理のよくあるパターンの一つで、グループ化は情報に対してそれをやってる
	そのグループ化と複数の関係は何ですか？
		複数あるものが一つにまとまることによって圧縮され、脳に対する負担が減る
	その一つとグループ化の関係は何ですか？
		グループ化によって生み出される
	そのグループ化と、ツールバーとは同じですか？違いますか？
		違います
	グループ化と知的生産の関係は何ですか？
		グループ化が知的生産を支援するし、グループ化自体が知的生産
	そのグループ化と、知的生産とは同じですか？違いますか？
		うーーーん、とても強く関連しているがまったく同じではなくて、知的生産のうちのたくさんの具体的情報を総合していくことによって新たな知識を生み出すタイプの作業を、脳内で暗黙的にやる代わりに外でやることによって技術的な強化を可能にするのがグループ化って感じかな
	そのグループ化の時、知的生産に何が起こりますか？
		思考の中で扱える情報の量が増えることによってより良い結果をもたらすことができる
	知的生産の時、グループ化に何が起こりますか？
		グループ化のメリットとは何か、を言語化しようとしているこの現在進行中の活動が知的生産だな
	そのグループ化と知的生産の間には何がありますか？
		グループ化だけで終わりではなくて、それによって生み出された構造を、生身の人間が理解できる文章の形に変換するプロセスがある
	そのグループ化と生身の関係は何ですか？
		生身の人間を強化する手法
	その生身と、グループ化とは同じですか？違いますか？
		違います。
	グループ化の時、生身に何が起こりますか？
		扱える情報量が増える
	生身の時、グループ化に何が起こりますか？
		(毎回両方聞くのはイマイチ。だいたい先の質問だけでいい気もするし)
		生身の時も、無意識にグループ化を行なっていた。それを外在化したのがKJ法、電子化することによって近年の情報処理の技術を応用できるようにすることによって、人間の知能を強化するのが今作りつつあるやつ。
	そのグループ化と生身の間には何がありますか？
		文明の発展の歴史における新しい一歩だね
	その文明とグループ化の関係は何ですか？
		多数の人間の知的能力が強化されれば必然的に文明は新たなステージに進む
	その人間とグループ化の関係は何ですか？
		獲得すべき新しいアビリティ
	その新しいアビリティとグループ化の関係は何ですか？
		同じです
	グループ化と、人間とは同じですか？違いますか？
		違います
	グループ化の時、人間に何が起こりますか？
		進化！
	その進化とグループ化の関係は何ですか？
		進化をもたらすのだ！
	その進化と、グループ化とは同じですか？違いますか？
		違うつもりだったけどもしかして同じなのか？グループ化とは複数のものが一つになってそれを代表するシンボルが付与される仕組み。法人格は経済行為の主体としての人格にグループ化に相当する操作を加えたもの。人間の知的活動の主体としての人格に同様のグループ化を行うと…
	その人間の時、グループ化に何が起こりますか？
		複数の人格が融合して一つになる時のグループ化とは、一つの人格の中で複数の思考が生まれるわけであって、利害対立がないから多数決なんかより生産的な総合が行える可能性がある
	そのグループ化と、複数とは同じですか？違いますか？
		まあ違うね
	グループ化の時、複数に何が起こりますか？
		合体！
	グループ化と、一つとは同じですか？違いますか？
		結果として一つになる
	その一つの時、グループ化に何が起こりますか？
		必要なくなる？？
	グループ化の時、一つに何が起こりますか？
		グループ化の前にあった一つのものは、グループ化によって他のものと融合して新たな一つになる
	そのグループ化と一つの間には何がありますか？
		グループ化は「一つ」を、より大きな「新たな一つ」に更新していくプロセス
	そのグループ化とプロセスの関係は何ですか？
		同じかな
	複数の時、グループ化に何が起こりますか？
		複数のものはそれぞれ自分は違うものだと思ってたわけだけど、実は一つのものだったと気づかされる
	その複数とグループ化の間には何がありますか？
		グループ化が複数のものの間をつないで一つにするのだな
	そのグループ化と人間の間には何がありますか？
		やっぱ生身の人間がそれぞれ自分たちは独立したことなる個体だと考えてるのがおかしくて、グループ化によって融合してより大きな新たな一つが生み出されるのだ
	そのグループ化と個体の関係は何ですか？
		個体の殻をぶっ壊せ！
	その個体と、グループ化とは同じですか？違いますか？
		違う
	グループ化の時、進化に何が起こりますか？
		個体が融合して新たな一つになるのが進化
	その進化の時、グループ化に何が起こりますか？
		うーん、人類がグループ化によって融合して一つになった場合、みんなグループ化によって融合することを有益だと思ってるわけだから、異星人の文明を見つけて融合するかなー
	その一つと価値の関係は何ですか？
		「より大きな一つ」と融合して新たな一つになることが価値だよね
	その価値と、一つとは同じですか？違いますか？
		「今現在の大きな一つ」も小さな生身の一つよりは価値が高いが、完成形ではなくて、新たなものを融合してさらに大きな一つになることで価値が高まる
	その価値の時、一つに何が起こりますか？
		今の生身の僕にはとても表現できないようなすごいことが起こる
	一つの時、価値に何が起こりますか？
		むしろさっきのはこれに対する答えだったか
	価値と一つの間には何がありますか？
		融合し続ける
	グループ化と進化の間には何がありますか？
		(まさにそれだよね。帰宅完了したので一旦終了)

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
