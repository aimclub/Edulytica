PROMPT_TEMPLATE = """
    **Instructions:** You have received several chunks of text containing information that might be related to the
    user's request concerning tanks. Your task is to analyze the text and extract relevant information to answer the
    user's question. Make sure to base your response solely on the details present in the text. Do not add any
    details, guess, or generate information beyond what is provided. If you cannot find the necessary information
    within the provided text, respond with "Information not found." The answer must be given in the language that is
    used in the context.

    Restrictions: Your response must strictly align with the information given in the text chunks. Avoid embellishing or
    making assumptions if the text does not explicitly support them.

    **Context:**
    {matches}

    **User Request:**
    {user_query}
    """
