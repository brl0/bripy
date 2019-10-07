"""bllb NLTK helpers."""


from nltk import pos_tag, regexp_tokenize, word_tokenize
from nltk.collocations import BigramAssocMeasures, BigramCollocationFinder
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import wordpunct_tokenize
from typing import List


from bripy.bllb.bllb_logging import logger, DBG
from bripy.bllb.bllb_str import *


def remove_nltk_stopwords(s: str, punc: bool = True) -> List[str]:
    """Remove stop words and punctuation and return list of tokens."""
    nltk_stopword_set = set(stopwords.words("english"))
    # remove it if you need punctuation
    if punc:
        nltk_stopword_set.update(
            [
                ".",
                ",",
                '"',
                "'",
                "?",
                "!",
                ":",
                ";",
                "(",
                ")",
                "[",
                "]",
                "{",
                "}",
            ]
        )
    return [
        word
        for word in word_tokenize(s)
        if word.casefold() not in nltk_stopword_set
    ]


def get_wordnet_pos(word: str) -> str:
    """Map POS tag to first character lemmatize() accepts"""
    tag = pos_tag([word])[0][1][0].upper()
    tag_dict = {
        "J": wordnet.ADJ,
        "N": wordnet.NOUN,
        "V": wordnet.VERB,
        "R": wordnet.ADV,
    }
    return tag_dict.get(tag, wordnet.NOUN)


def lemmatize_word(word: str) -> str:
    """Lemmatize Single Word with the appropriate POS tag."""
    lemmatizer = WordNetLemmatizer()
    return lemmatizer.lemmatize(word, get_wordnet_pos(word))


def get_wordnet_lemma(word):
    lemma = wordnet.morphy(word)
    if lemma is None:
        return word
    else:
        return lemma


def iget_wordnet_lemmas(iterable):
    """get_lemmas for list (iterable) of lists of words"""
    return list(map(lambda l: list(map(get_wordnet_lemma, l)), iterable))


def lemmatize_sent(sentence: str) -> List[str]:
    """Lemmatize a Sentence with the appropriate POS tag."""
    lemmatizer = WordNetLemmatizer()
    return [
        lemmatizer.lemmatize(w, get_wordnet_pos(w))
        for w in word_tokenize(sentence)
    ]


def reg_tok(s: str, pattern: str = r"'\w+|\$[\d\.]+|\S+'") -> List[str]:
    """Tokenize based on regular expression."""
    return regexp_tokenize(s, pattern, gaps=False)


def nltk_tok(s):
    return regexp_tokenize(s, make_token_pattern(2), gaps=False)


def porter_stem(doc: str) -> List[str]:
    stop_words = set(stopwords.words("english"))
    # remove it if you need punctuation
    stop_words.update(
        [".", ",", '"', "'", "?", "!", ":", ";", "(", ")", "[", "]", "{", "}"]
    )
    porter = PorterStemmer()
    return [
        porter.stem(i.lower())
        for i in wordpunct_tokenize(doc)
        if i.lower() not in stop_words
    ]


def bigrams(corpus):
    bigram_measures = BigramAssocMeasures()
    finder = BigramCollocationFinder.from_words(corpus)
    # only bigrams that appear 3+ times
    finder.apply_freq_filter(3)
    # return the 5 n-grams with the highest PMI
    return finder.nbest(bigram_measures.pmi, 5)


def verb_count(text):
    token_text = word_tokenize(text)
    tagged_text = pos_tag(token_text)
    counter = 0
    for _, t in tagged_text:
        t = t[:2]
        if t in ["VB"]:
            counter += 1
    return counter


def noun_count(text):
    token_text = word_tokenize(text)
    tagged_text = pos_tag(token_text)
    counter = 0
    for w, t in tagged_text:
        t = t[:2]
        if t in ["NN"]:
            counter += 1
    return counter
