"""
Input canonicalizers for Study C (paper1/SPEC.md section 2), applied in front of an unchanged guard.

  naive         NFKC, then delete every Unicode format character (category Cf), as LLM Guard's
                InvisibleText scanner does. This also deletes ZWJ/ZWNJ, which Devanagari needs.
  script_aware  NFKC; delete U+200B, U+00AD, U+2060 and U+FEFF, and ZWJ/ZWNJ except between two
                Devanagari characters; map Cyrillic/Greek confusables to Latin inside words that are
                mostly Latin; collapse letter spacing.

`views(text, canonicalizer, rescan)` returns the texts a guard scores for one input; the guard's score
is the maximum over them. With rescan, Base64 spans and ROT13 text are also decoded and scored
(decode-and-rescan). Leetspeak and combining diacritics are deliberately not handled: the SPEC's
rule list does not include them, so they measure what canonicalization cannot reach.
"""

import base64
import binascii
import codecs
import math
import re
import unicodedata
from typing import List

INVISIBLES = {"​", "­", "⁠", "﻿"}  # zero-width space, soft hyphen, word joiner, BOM
JOINERS = {"‌", "‍"}  # ZWNJ, ZWJ: select Devanagari conjunct forms


def _devanagari(ch: str) -> bool:
    return "ऀ" <= ch <= "ॿ"


# Cyrillic and Greek letters that render like Latin ones (lowercase and uppercase)
CONFUSABLES = {
    "а": "a", "е": "e", "о": "o", "р": "p", "с": "c", "х": "x", "у": "y", "і": "i", "ј": "j", "ѕ": "s",
    "һ": "h", "ԁ": "d", "ԛ": "q", "ԝ": "w", "А": "A", "В": "B", "Е": "E", "К": "K", "М": "M", "Н": "H",
    "О": "O", "Р": "P", "С": "C", "Т": "T", "Х": "X", "У": "Y", "І": "I", "Ј": "J", "Ѕ": "S",
    "α": "a", "ο": "o", "ρ": "p", "ν": "v", "τ": "t", "υ": "u", "ι": "i", "κ": "k", "χ": "x",
    "Α": "A", "Β": "B", "Ε": "E", "Ζ": "Z", "Η": "H", "Ι": "I", "Κ": "K", "Μ": "M", "Ν": "N", "Ο": "O",
    "Ρ": "P", "Τ": "T", "Υ": "Y", "Χ": "X",
}
WORD = re.compile(r"\w+", re.UNICODE)
SPACED = re.compile(r"(?<!\S)(?:[^\W\d_] ){3,}[^\W\d_](?!\S)")  # >= 4 single letters separated by one space
BASE64_SPAN = re.compile(r"[A-Za-z0-9+/]{16,}={0,2}")

# English letter frequencies (percent), for deciding whether a word reads better ROT13-decoded
LETTER_FREQ = dict(zip("abcdefghijklmnopqrstuvwxyz", [
    8.2, 1.5, 2.8, 4.3, 12.7, 2.2, 2.0, 6.1, 7.0, 0.15, 0.77, 4.0, 2.4,
    6.7, 7.5, 1.9, 0.095, 6.0, 6.3, 9.1, 2.8, 0.98, 2.4, 0.15, 2.0, 0.074]))


def naive(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    return "".join(ch for ch in text if unicodedata.category(ch) != "Cf")


def _strip_invisibles(text: str) -> str:
    out = []
    for i, ch in enumerate(text):
        if ch in INVISIBLES:
            continue
        if ch in JOINERS and not (0 < i < len(text) - 1 and _devanagari(text[i - 1]) and _devanagari(text[i + 1])):
            continue
        out.append(ch)
    return "".join(out)


def _fold_confusables(text: str) -> str:
    def fold(m):
        w = m.group(0)
        latin = sum(1 for ch in w if "a" <= ch.lower() <= "z")
        foreign = sum(1 for ch in w if ch in CONFUSABLES)
        if foreign and latin + foreign >= len(w) / 2 and latin >= 1:  # mostly Latin with lookalikes mixed in
            return "".join(CONFUSABLES.get(ch, ch) for ch in w)
        return w
    return WORD.sub(fold, text)


def script_aware(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = _strip_invisibles(text)
    text = _fold_confusables(text)
    return SPACED.sub(lambda m: m.group(0).replace(" ", ""), text)


CANONICALIZERS = {"none": lambda t: t, "naive": naive, "script_aware": script_aware}


def _english_ll(word: str) -> float:
    return sum(math.log(LETTER_FREQ.get(ch, 0.05)) for ch in word.lower() if "a" <= ch.lower() <= "z")


def rot13_view(text: str, min_words: int = 3, min_gain: float = 4.0):
    """Decodes the run of consecutive words that gains most in English letter-frequency log-likelihood under ROT13
    (maximum-sum segment), if it spans >= min_words words and gains > min_gain nats; None otherwise."""
    tokens = re.split(r"(\s+)", text)
    words = [k for k, t in enumerate(tokens) if t.strip()]
    gain = [_english_ll(codecs.encode(tokens[k], "rot13")) - _english_ll(tokens[k]) for k in words]
    best, best_span, cur, start = 0.0, None, 0.0, 0
    for i, g in enumerate(gain):  # Kadane: the contiguous word run with the largest total gain
        if cur <= 0:
            cur, start = g, i
        else:
            cur += g
        if cur > best:
            best, best_span = cur, (start, i)
    if best_span is None or best <= min_gain or best_span[1] - best_span[0] + 1 < min_words:
        return None
    out = list(tokens)
    for i in range(best_span[0], best_span[1] + 1):
        out[words[i]] = codecs.encode(tokens[words[i]], "rot13")
    return "".join(out)


def base64_view(text: str):
    """Replaces Base64 spans that decode to mostly printable UTF-8 with their decoding; None if none."""
    changed = False

    def dec(m):
        nonlocal changed
        span = m.group(0)
        try:
            raw = base64.b64decode(span + "=" * (-len(span) % 4), validate=True).decode("utf-8")
        except (binascii.Error, UnicodeDecodeError, ValueError):
            return span
        if not raw or sum(ch.isprintable() or ch.isspace() for ch in raw) < 0.9 * len(raw):
            return span
        changed = True
        return raw
    out = BASE64_SPAN.sub(dec, text)
    return out if changed else None


def views(text: str, canonicalizer: str = "none", rescan=False) -> List[str]:
    """rescan: False; True or "max" scores the text and its decodings (SPEC: score = max of raw and decoded);
    "replace" scores only the decodings when any exist. Max can repair a guard that misses encoded attacks but
    never one that flags the encoding itself; replace can repair both, at the cost of trusting the decoder."""
    base = CANONICALIZERS[canonicalizer](text)
    if not rescan:
        return [base]
    decoded = [v for v in (base64_view(base), rot13_view(base)) if v is not None and v != base]
    if rescan == "replace":
        return decoded or [base]
    return [base] + [v for i, v in enumerate(decoded) if v not in decoded[:i]]
