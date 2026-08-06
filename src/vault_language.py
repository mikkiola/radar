ENGLISH_ASSESSMENT_HEADING = "## What Changes in the Ecosystem"
ENGLISH_PATTERN_SUMMARY_HEADING = "## Summary"


def is_english_body(content):
    """Определить язык тела vault-файла по каноническому заголовку."""
    return (
        ENGLISH_ASSESSMENT_HEADING in content
        or ENGLISH_PATTERN_SUMMARY_HEADING in content
    )
