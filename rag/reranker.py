import os
import re
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def rerank(query, contexts):
    if not contexts:
        return []

    context_str = "\n\n".join(
        [f"[{i}] {c}" for i, c in enumerate(contexts)]
    )

    prompt = f"""
    You are a legal assistant specializing in Vietnamese Traffic Law.
    
    Query: {query}

    Contexts:
    {context_str}

    Task:
    Select the TOP 3 most relevant context indices that directly answer the query.
    
    Rules:
    - Only return indices separated by commas (e.g., 0,2,4).
    - If fewer than 3 are relevant, return only those.
    - Strictly no explanation or additional text.
    """

    try:
        res = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=1  
        )
        
        output = res.choices[0].message.content.strip()
        
        indices = [int(i) for i in re.findall(r'\d+', output)]
        
        valid_indices = [i for i in indices if i < len(contexts)]
        
        if valid_indices:
            return [contexts[i] for i in valid_indices[:3]]
        else:
            return contexts[:3]
    
    except Exception as e:
        print(f"Rerank failed: {e} → fallback to top 3")
        return contexts[:3]