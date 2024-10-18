import src.ai_prompts as ai_prompts

def reset_history():
    return [
        {"role": "system", "content": ai_prompts.sysprompt},
    ]

CHAT_HISTORY = reset_history()
