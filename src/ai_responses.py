import os, io, json, asyncio, logging
import openai

from src.toolbox.toolbox import TOOLBOX

import src.tools


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


# OpenAI Client und API Key setzen
client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# model = "gpt-4o"
model = "gpt-4o-mini"


async def generate_chat_response(prompt, user_data, toolbox=TOOLBOX):
    """Generiert eine Antwort auf eine Textnachricht mit dem OpenAI Modell."""

    user_id = user_data["user_id"]
    chat_history = user_data["chat_history"]

    # TODO: hier könnte tool filtering stattfinden
    tools = []
    for (_, tool, _) in toolbox:
        tools.append(tool)

    chat_history.append({"role": "user", "content": prompt})

    while True:
        response = await client.chat.completions.create(
            model=model,
            messages=chat_history,
            tools=tools
        )
        chat_history.append(response.choices[0].message)

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

                logging.info(f"Function name: {tool_call_name}")
                logging.info(f"Function arguments before resetting user_id: {func_args}")
                if "user_id" in func_args.keys():
                    func_args["user_id"] = user_id
                logging.info(f"Function arguments after setting user_id: {func_args}")

                try: # find in toolbox the function that matches the tool_call_name and execute it
                    func = next((func for (fname, _, func) in toolbox if fname == tool_call_name), None)
                    if asyncio.iscoroutinefunction(func):
                        func_response = await func(**func_args)
                    else:
                        func_response = func(**func_args)

                except Exception as e:
                    logging.error(f"Failed to call function: {tool_call_name} with error: {e}")
                    func_response = str("An Exception occurred while calling the function.")
                finally:
                    logging.info("Function response: " + str(func_response))
                    # Append the function response directly to messages
                    chat_history.append({
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


async def transcribe_audio(audio_file_data):
    """Transkribiert eine Audiodatei mit OpenAI Whisper auf Deutsch."""

    audio_file = io.BytesIO(audio_file_data)
    audio_file.name = "audio.ogg"
    audio_file.seek(0)
    transcript = await client.audio.transcriptions.create(model="whisper-1", file=audio_file, language="de")
    return transcript.text
