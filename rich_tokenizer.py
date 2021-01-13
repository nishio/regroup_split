"""
rich tokernizer
split to tokens with rich informarion

>>> concat_tokens(tokenize("Hello world"))
'Hello world'
"""
import MeCab
mecab = MeCab.Tagger()
mecab.parse('')  # 文字列がGCされるのを防ぐ


def digest(word):
    return word.strip().lower()


def to_base_form(node):
    base_form = node.feature.split(",")[-3]
    if base_form == "*":
        if hasattr(node, "word"):
            return node.word
        return node.surface
    return base_form


class RichWord:
    def __init__(self, word, index, doc_id="", feature="", digested=None):
        self.word = word
        self.index = index
        self.doc_id = doc_id
        self.feature = feature
        self.is_stop = False
        if digested:
            self.digest = digested
        else:
            self.digest = digest(word)

    def __repr__(self):
        return self.word

    def __str__(self):
        return self.word

    def __len__(self):
        return len(self.word)

    def __eq__(self, rhs):
        if not rhs:
            return False
        return self.word == rhs.word

    def __hash__(self):
        return hash(self.digest)


def tokenize(s, doc_id=""):
    """
    >>> tokenize("情報の共有")
    [情報, の, 共有]
    >>> concat_tokens(tokenize("This is a pen"))
    'This is a pen'
    >>> concat_tokens(tokenize("あああ is a pen"))
    'あああ is a pen'
    """
    tokens = []
    node = mecab.parseToNode(s)
    node = node.next  # skip BOS
    i = 0
    start = 0
    while node:
        word = node.surface
        # keep whitespace before token
        wslength = node.rlength - node.length
        ws = s[start:start+wslength]
        word = ws + word
        digested = digest(to_base_form(node))
        t = RichWord(word, i, doc_id, node.feature, digested)
        tokens.append(t)

        i += 1
        start += wslength + len(node.surface)
        node = node.next
    tokens = tokens[:-1]  # remove BOS/EOS
    return tokens


def concat_tokens(xs, sep=""):
    return sep.join(map(str, xs)).strip()


def _test():
    import doctest
    doctest.testmod()


if __name__ == "__main__":
    print("testing...")
    _test()
