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


def output(buf):
    buf = remove_tail(buf)
    buf = remove_head(buf)
    if buf:
        buf[-1].word = to_base_form(buf[-1])
        print(buf)


def split(buf):
    output(buf)


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


def main():
    for line in open("test/simplelines1.txt"):
        line = line.strip()
        print(f"\n> {line}")
        tokens = tokenize(line)
        # print(tokens)
        buf = []
        buflen = 0

        for t in tokens:
            # print(t, t.feature)
            if str(t) in "、。「」()！":
                output(buf)
                buflen = 0
                buf = []

            else:
                buf.append(t)
                buflen += len(str(t))
                # if buflen > 100:
                #     split(buf)
                #     buflen = 0
                #     buf = []

        output(buf)


T1 = """

"""
_TEST_T1 = """
>>> as_input(T1)
>>> main()
result
"""


def _test():
    import doctest
    doctest.testmod()
    g = globals()
    for k in sorted(g):
        if k.startswith("TEST_"):
            print(k)
            doctest.run_docstring_examples(g[k], g, name=k)


if __name__ == "__main__":
    import sys
    input = sys.stdin.buffer.readline
    read = sys.stdin.buffer.read
    if sys.argv[-1] == "-t":
        _test()
        sys.exit()
    main()
