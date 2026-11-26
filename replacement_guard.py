"""Choose whether to replace an already validated CPU workspace document."""


def allow_replace(dirty, has_document, confirm_dirty, confirm_clean):
    """Never bypass dirty state, even for an empty assembly draft."""
    if dirty:
        return bool(confirm_dirty())
    if has_document:
        return bool(confirm_clean())
    return True
