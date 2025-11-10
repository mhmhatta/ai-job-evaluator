def build_prompt(query, context: str = ""):
    """
    Build prompt for LLM query.
    Context is optional — if not provided, use query alone.
    """
    context_part = f"Context:\n{context}\n\n" if context else ""
    
    return f"""
    You are an AI Job Assistant.
    Use the context below (if available) to answer user queries about job evaluation.

    {context_part}
    User Query:
    {query}

    Provide a clear, concise, and professional answer.
    """
