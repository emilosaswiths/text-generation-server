import re


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def remove_control_chars(text: str) -> str:
    return re.sub(r"[\x00-\x1F\x7F]", "", text)


def strip_markdown(text: str) -> str:
    # Remove markdown syntax that hurts generation
    text = re.sub(r"`{1,3}.*?`{1,3}", "", text, flags=re.DOTALL)
    text = re.sub(r"[*_>#\-]{1,}", " ", text)
    return text


def truncate_text(text: str, max_length: int = 2000) -> str:
    return text[:max_length]


def clean_text(
    text: str,
    max_length: int = 2000,
    strip_md: bool = True
) -> str:
    """
    Main text cleaning pipeline.
    """
    if not text:
        return ""

    text = remove_control_chars(text)
    text = normalize_whitespace(text)

    if strip_md:
        text = strip_markdown(text)

    text = truncate_text(text, max_length)
    return text
