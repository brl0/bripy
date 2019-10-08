"""bllb NLP helpers."""

from collections import Counter
from itertools import islice, tee
from json import loads
from typing import Iterable, List, Set, Tuple
from urllib.request import urlopen

from bripy.bllb.bllb_iter import reduce_iconcat
from bripy.bllb.bllb_str import *


def get_en_stopwords() -> Set[str]:
    """Stopwords from 'https://github.com/6/stopwords-json'."""
    u = \
        "https://raw.githubusercontent.com/6/stopwords-json/master/dist/en.json"
    with urlopen(u) as file:
        return set(loads(file.read()))


def get_spacy_stopwords() -> Set[str]:
    """Get English stopwords from Spacy module."""
    from spacy.lang.en.stop_words import STOP_WORDS

    return set(STOP_WORDS)


def get_nltk_stopwords() -> Set[str]:
    """Get stopwords from NLTK."""
    from nltk.corpus import stopwords

    return set(stopwords)


def get_all_stopwords() -> Set[str]:
    """Get all known stopword sets."""
    return get_en_stopwords() | get_spacy_stopwords() | get_nltk_stopwords()


class spacy_lemmatizer:
    """Initialize spacy 'en' model, keep only tagger for lemmatization."""

    import spacy

    nlp = spacy.load("en", disable=["parser", "ner"])

    def get_lemmas(self, s: str) -> List[str]:
        """Parse the sentence using the loaded 'en' model object `nlp`.

        Extract the lemma for each token and join.
        """
        doc = self.nlp(s)
        return [token.lemma_ for token in doc]


class snowball:
    """Snowball stemmer."""

    from snowballstemmer import EnglishStemmer

    snow = EnglishStemmer()
    stem = snow.stemWord


def ngram_generator(iterable, n: int) -> List[Tuple[str]]:
    """Generate ngrams."""
    return [
        *zip(*((islice(seq, i, None)
                for i, seq in enumerate(tee(iterable, n)))))
    ]


def word_lists_counter(word_lists: Iterable[Iterable[str]]):
    """Count words in a list of words."""
    word_list = reduce_iconcat(l for l in word_lists)
    c = Counter(word_list)
    return c.most_common()


def get_tokens(doc):  # Functional doc tokenizer
    # doc.split()
    return tok(pre(doc, camelCase=True))  # <--Replace tokenizer here


def get_vocab(docs):
    """Return counter dict of words and counts in docs iterable"""
    vocab = collections.Counter()
    for doc in docs:  # Looping, statefulness of Counter seems non-functional
        vocab.update(
            get_tokens(doc))  # Counter update accumulates without return
    print('vocab size: ', len(vocab))
    return vocab
