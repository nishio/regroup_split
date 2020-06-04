
from cabocha.analyzer import CaboChaAnalyzer
analyzer = CaboChaAnalyzer()
tree = analyzer.parse(
    "僕は短文の付箋を作ることとか、長文で書いてしまったものを短く刻むことに慣れてるのだけど、世の中の人は慣れてないから長文のまま入れてしまって「字が小さすぎて読めない付箋」を作っちゃうよね")
# for chunk in tree:
#     for token in chunk:
#         print(token)

start = 0
while start < tree.chunk_size:
    i = start
    result = [tree[i].surface]
    while True:
        if tree[i].next_link_id == i + 1:
            result.append(tree[i + 1].surface)
            i += 1
        else:
            break
    print(start, result, tree[i].next_link_id)
    start = i + 1
