import os, io, json, asyncio
import openai

import src.ai_chat_history as ai_chat_history
from src.toolbox import TOOLBOX

# i have to import those functions here so that the globals() function of the ai chat can find them
from src.tools.todo_app import todo_app_api
from src.tools.house_energy import get_energy_house_data, set_or_get_wallbox_mode, get_wallbox_status, get_dryer_machine_status, get_washing_machine_status, get_energy_prices

# OpenAI Client und API Key setzen
client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def transcribe_audio(audio_file_data):
    """Transkribiert eine Audiodatei mit OpenAI Whisper auf Deutsch."""

    audio_file = io.BytesIO(audio_file_data)
    audio_file.name = "audio.ogg"
    audio_file.seek(0)
    transcript = await client.audio.transcriptions.create(model="whisper-1", file=audio_file, language="de")
    return transcript.text


async def generate_chat_response(prompt, tools=TOOLBOX):
    """Generiert eine Antwort auf eine Textnachricht mit dem OpenAI Modell."""

    ai_chat_history.CHAT_HISTORY.append({"role": "user", "content": prompt})

    while True:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=ai_chat_history.CHAT_HISTORY,
            tools=tools
        )
        ai_chat_history.CHAT_HISTORY.append(response.choices[0].message)

        # if no tool is needed, break and return response
        if response.choices[0].message.tool_calls is None:
            break

        for tc in response.choices[0].message.tool_calls:
            if tc.id:  # New tool call detected here
                tool_call_id = tc.id
                tool_call_name = tc.function.name
            tool_call_accumulator = tc.function.arguments if tc.function.arguments else ""
        
            # When the accumulated JSON string seems complete then:
            try:
                func_args = json.loads(tool_call_accumulator)

                print(f"Function name: {tool_call_name}")
                print(f"Function arguments: {func_args}")
                # Call the corresponding function that we defined and matches what is in the available functions
                if asyncio.iscoroutinefunction(globals()[tool_call_name]):
                    func_response = await globals()[tool_call_name](**func_args)
                else:
                    func_response = globals()[tool_call_name](**func_args)
                print("Function response: " + str(func_response))
                # Append the function response directly to messages
                ai_chat_history.CHAT_HISTORY.append({
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "name": tool_call_name,
                    "content": str(func_response),
                })
                tool_call_accumulator = ""  # Reset for the next tool call
                tool_call_name = None
                tool_call_id = None
            except json.JSONDecodeError:
                # Incomplete JSON; continue accumulating
                pass

    return response.choices[0].message.content
