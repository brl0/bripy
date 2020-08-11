"""bllb NLP helpers."""

from collections import Counter
from itertools import islice, tee
from json import loads
from typing import Iterable, List, Optional, Set, Tuple
from urllib.request import urlopen

from bripy.bllb.iter import reduce_iconcat
from bripy.bllb.str import *

LANGUAGE = "english"

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


def get_sumy_stopwords(language: str = LANGUAGE) -> Set[str]:
    from sumy.utils import get_stop_words

    return set(get_stop_words(LANGUAGE))


def get_all_stopwords() -> Set[str]:
    """Get all known stopword sets."""
    return get_en_stopwords() | \
            get_spacy_stopwords() | \
            get_nltk_stopwords() | \
            get_sumy_stopwords()


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


def get_sumy(
            sentences_count: int = 10,
            body: str = "",
            url: Optional[str] = None
    ) -> str:
    from sumy.nlp.tokenizers import Tokenizer
    from sumy.summarizers.lsa import LsaSummarizer as Summarizer
    from sumy.nlp.stemmers import Stemmer
    from sumy.utils import get_stop_words

    if url is None:
        from sumy.parsers.plaintext import PlaintextParser as Parser
        item = (body)
    else:
        from sumy.parsers.html import HtmlParser as Parser
        item = (body, url)
        DBG(f'Sumy HTML, url: {url}')

    tokenizer = Tokenizer(LANGUAGE)
    parser = Parser.from_string(*item, tokenizer)
    stemmer = Stemmer(LANGUAGE)
    summarizer = Summarizer(stemmer)
    summarizer.stop_words = get_stop_words(LANGUAGE)
    summary = summarizer(parser.document, sentences_count)
    summary = [str(sentence) for sentence in summary]
    summary = ' '.join(summary)
    return summary

def get_sumy_stopwords(language: str = LANGUAGE) -> Iterable[str]:
    from sumy.utils import get_stop_words

    stop_words = get_stop_words(LANGUAGE)
    return stop_words
