"""
Shared validation for frontmatter metadata across sync scripts.
Centralizes checks that should warn (but not block) syncs.
"""

def validate_metadata(frontmatter_obj, item_name, item_type="assignment"):
    """
    Validates frontmatter metadata and returns a list of warnings.

    Checks are non-blocking warnings that get printed during sync.
    Add new checks as tuples of (condition, message) to keep it clean.

    Args:
        frontmatter_obj: The frontmatter object with metadata
        item_name: The name of the assignment/discussion for reporting
        item_type: "assignment" or "discussion" for context

    Returns:
        List of warning messages (empty list if no warnings)
    """
    warnings = []

    # Check 1: If peer_reviews is enabled, peer_review_count should be >= 2
    if frontmatter_obj.get('peer_reviews', False):
        peer_review_count = frontmatter_obj.get('peer_review_count', 1)
        if peer_review_count < 2:
            warnings.append(
                f"peer_reviews is enabled but peer_review_count is {peer_review_count}. "
                f"Did you mean to set it to 2?"
            )

    return warnings
