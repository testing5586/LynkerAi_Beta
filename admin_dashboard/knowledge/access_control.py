def allow_access(ai_role: str, knowledge_type: str) -> bool:
    # Primary AI sees summaries only
    if ai_role == "primary":
        return knowledge_type in ["pattern", "rule"]

    # Child AI sees patterns + case summaries, never raw identity data
    if ai_role == "child":
        return knowledge_type in ["pattern"]

    # No other roles permitted
    return False
