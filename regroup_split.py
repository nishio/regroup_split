from rich_tokenizer import tokenize, concat_tokens, RichWord, to_base_form
from collections import defaultdict
_HEAD_TOKENS_TO_REMOVE = open(
    "HEAD_TOKENS_TO_REMOVE.txt").read().strip().splitlines()

HEAD_TOKENS_TO_REMOVE = defaultdict(list)
for line in _HEAD_TOKENS_TO_REMOVE:
    ts = line.split()
    HEAD_TOKENS_TO_REMOVE[len(ts)].append(ts)

_TAIL_TOKENS_TO_REMOVE = open(
    "TAIL_TOKENS_TO_REMOVE.txt").read().strip().splitlines()

# print(*sorted(set(_TAIL_TOKENS_TO_REMOVE)), sep="\n")
TAIL_TOKENS_TO_REMOVE = defaultdict(list)
for line in _TAIL_TOKENS_TO_REMOVE:
    ts = line.split()
    TAIL_TOKENS_TO_REMOVE[len(ts)].append(ts)

REPLACE = """
の か ？ : ？
"""


def remove_head(tokens):
    """
    >>> remove_head(tokenize("あー"))
    []
    >>> remove_head(tokenize("そうか"))
    []
    """
    words = [t.word for t in tokens]

    to_repeat = True
    while to_repeat:
        to_repeat = False
        for k in reversed(HEAD_TOKENS_TO_REMOVE.keys()):
            if k > len(tokens):
                continue
            ts = words[:k]
            for ss in HEAD_TOKENS_TO_REMOVE[k]:
                if ts == ss:
                    tokens = tokens[k:]
                    words = words[k:]
                    to_repeat = True
                    break
            else:
                continue
            break
    return tokens


def remove_tail(tokens):
    """
    >>> remove_tail(tokenize("人は人は"))
    [人, は, 人]
    """
    words = [t.word for t in tokens]

    to_repeat = True
    while to_repeat:
        to_repeat = False
        for k in reversed(TAIL_TOKENS_TO_REMOVE.keys()):
            if k > len(tokens):
                continue
            ts = words[-k:]
            for ss in TAIL_TOKENS_TO_REMOVE[k]:
                if ts == ss:
                    tokens = tokens[:-k]
                    words = words[:-k]
                    to_repeat = True
                    break
            else:
                continue
            break
    return tokens


def clean(tokens):
    ret = remove_tail(tokens)
    ret = remove_head(ret)
    if ret:
        ret[-1].word = to_base_form(ret[-1])
    return ret


def is_too_long(tokens, limit=20):
    return sum(len(x) for x in tokens) > limit


def split1(tokens):
    tokens = clean(tokens)
    if not tokens:
        return []
    # if not is_too_long(tokens):
    #     return [tokens]

    ret = []
    buf = []
    for t in tokens:
        if t.word in "、。「」()！[]":
            ret.extend(split2(buf))
            buf = []
        else:
            buf.append(t)
    ret.extend(split2(buf))
    return ret


def split2(tokens):
    tokens = clean(tokens)
    if not tokens:
        return []
    if not is_too_long(tokens):
        return [tokens]

    ret = []
    buf = []
    for t in tokens:
        if t.feature.startswith("助詞,接続助詞") or t.word == "たら":
            ret.extend(split3(buf))
            buf = []
        else:
            buf.append(t)
    ret.extend(split3(buf))
    return ret


def split3(tokens):
    tokens = clean(tokens)
    if not tokens:
        return []
    if not is_too_long(tokens):
        return [tokens]

    ret = []
    buf = []
    for t in tokens:
        if t.feature.startswith("助詞,係助詞"):
            ret.extend(split4(buf))
            buf = []
        else:
            buf.append(t)
    ret.extend(split4(buf))
    return ret


def split4(tokens):
    tokens = clean(tokens)
    if not tokens:
        return []
    if not is_too_long(tokens):
        return [tokens]

    ret = []
    buf = []
    for t in tokens:
        if t.feature.startswith("助詞,格助詞"):
            ret.extend(split5(buf))
            buf = []
        else:
            buf.append(t)
    ret.extend(split5(buf))
    return ret


def split5(tokens):
    tokens = clean(tokens)
    if not tokens:
        return []
    if not is_too_long(tokens):
        return [tokens]

    print("too long", tokens)
    return [tokens]


def main():
    for line in open("test/simplelines1.txt"):
        line = line.strip()
        print(f"\n> {line}")
        tokens = tokenize(line)
        print(">", concat_tokens(tokens, " "))
        for ts in split1(tokens):
            print(concat_tokens(ts))


def initiate_regression_test():
    import json
    result = []
    for line in open("test/simplelines1.txt"):
        line = line.strip()
        tokens = tokenize(line)
        obj = {
            "input": line,
            "splits": [
                concat_tokens(ts) for ts in split1(tokens)],
            "comment": ""
        }
        result.append(obj)
    json.dump(
        result,
        open("test/regression_test.json", "w"),
        ensure_ascii=False,
        indent=2
    )


def regression_test():
    import json
    result = json.load(open("test/regression_test.json"))
    for i, line in enumerate(open("test/simplelines1.txt")):
        line = line.strip()
        tokens = tokenize(line)
        splits = [
            concat_tokens(ts) for ts in split1(tokens)]

        expected = result[i]["splits"]
        if expected != splits:
            print(">", line)
            print("expected:", expected)
            print("actual:", splits)


def _test():
    import doctest
    doctest.testmod()
    g = globals()
    for k in sorted(g):
        if k.startswith("TEST_"):
            print(k)
            doctest.run_docstring_examples(g[k], g, name=k)

    regression_test()


if __name__ == "__main__":
    import sys
    input = sys.stdin.buffer.readline
    read = sys.stdin.buffer.read
    if sys.argv[-1] == "-t":
        _test()
        sys.exit()
    main()
