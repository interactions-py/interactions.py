import re
import interactions.models as models

__all__ = ("mentions",)


def mentions(
    text: str,
    query: "str | re.Pattern[str] | models.BaseUser | models.BaseChannel | models.Role",
    *,
    tag_as_mention: bool = False,
) -> bool:
    """
    Checks whether a query is present in a text.

    Args:
        text: The text to search in
        query: The query to search for
        tag_as_mention: Should `BaseUser.tag` be checked *(only if query is an instance of BaseUser)*

    Returns:
        Whether the query could be found in the text
    """
    if isinstance(query, str):
        return query in text
    if isinstance(query, re.Pattern):
        return query.match(text) is not None
    if isinstance(query, models.BaseUser):
        # mentions with <@!ID> aren't detected without the replacement
        return (query.mention in text.replace("@!", "@")) or (query.tag in text if tag_as_mention else False)
    if isinstance(query, (models.BaseChannel, models.Role)):
        return query.mention in text
    return False
