import re
from typing import List, Tuple, Optional


def normalize_text(text: str) -> str:
    """نرمال‌سازی متن فارسی."""
    if not text:
        return ""

    # حذف اعراب
    text = re.sub(r'[\u064B-\u065F\u0670]', '', text)

    # یکسان‌سازی حروف عربی/فارسی
    text = text.replace('ي', 'ی').replace('ك', 'ک')
    text = text.replace('ۀ', 'ه').replace('ة', 'ه')
    text = text.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')

    # حذف علائم
    text = re.sub(r'[^\w\s]', ' ', text)

    # حذف فاصله‌های اضافی
    text = re.sub(r'\s+', ' ', text).strip()

    return text.lower()


def tokenize(text: str) -> List[str]:
    """تقسیم متن به کلمات."""
    normalized = normalize_text(text)
    return normalized.split()


def jaccard_similarity(text1: str, text2: str) -> float:
    """شباهت Jaccard بین دو متن."""
    tokens1 = set(tokenize(text1))
    tokens2 = set(tokenize(text2))

    if not tokens1 or not tokens2:
        return 0.0

    intersection = tokens1 & tokens2
    union = tokens1 | tokens2

    return len(intersection) / len(union)


def keyword_match_score(query: str, keywords: str) -> float:
    """امتیاز بر اساس کلیدواژه‌ها."""
    if not keywords:
        return 0.0

    query_tokens = set(tokenize(query))
    keyword_tokens = set(tokenize(keywords))

    if not query_tokens or not keyword_tokens:
        return 0.0

    matches = query_tokens & keyword_tokens
    return len(matches) / len(keyword_tokens) if keyword_tokens else 0.0


def find_best_faq(
    query: str,
    faqs: list,
    threshold: float = 0.15,
) -> Tuple[Optional[object], float]:
    """
    بهترین FAQ رو پیدا می‌کنه.
    Returns: (faq, similarity_score)
    """
    if not query or not faqs:
        return None, 0.0

    best_faq = None
    best_score = 0.0

    for faq in faqs:
        # امتیاز شباهت سوال
        q_similarity = jaccard_similarity(query, faq.question)

        # امتیاز کلیدواژه
        k_score = keyword_match_score(query, faq.keywords or "")

        # ترکیب (وزن‌دار)
        score = (q_similarity * 0.6) + (k_score * 0.4)

        # bonus برای اولویت
        if score > 0:
            score += (faq.priority or 0) * 0.01

        if score > best_score:
            best_score = score
            best_faq = faq

    if best_score < threshold:
        return None, best_score

    return best_faq, best_score