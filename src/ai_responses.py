import os, io, json, asyncio, logging
import openai

from src.toolbox import TOOLBOX

# i have to import those functions here so that the globals() function of the ai chat can find them
from src.tools.todo_app import get_overdue_todos, create_todo, get_categories, get_todos_by_category, update_todo, get_open_todos
from src.tools.house_energy import get_energy_house_data, set_wallbox_mode, get_wallbox_status, get_dryer_machine_status, get_washing_machine_status, get_energy_prices
from src.tools.trash_app import get_tomorrows_trash, get_todays_trash, get_next_trash
from src.tools.weather_app import get_weather_week, get_weather_today
from src.tools.dwd_app import get_current_warnings
from src.tools.car_app import get_car_status


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


# OpenAI Client und API Key setzen
client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# model = "gpt-4o"
model = "gpt-4o-mini"


async def transcribe_audio(audio_file_data):
    """Transkribiert eine Audiodatei mit OpenAI Whisper auf Deutsch."""

    audio_file = io.BytesIO(audio_file_data)
    audio_file.name = "audio.ogg"
    audio_file.seek(0)
    transcript = await client.audio.transcriptions.create(model="whisper-1", file=audio_file, language="de")
    return transcript.text


async def generate_chat_response(prompt, user_data, tools=TOOLBOX):
    """Generiert eine Antwort auf eine Textnachricht mit dem OpenAI Modell."""

    user_id = user_data["user_id"]
    chat_history = user_data["chat_history"]

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
                
                try: 
                    # Call the corresponding function that we defined and matches what is in the available functions
                    if asyncio.iscoroutinefunction(globals()[tool_call_name]):
                        func_response = await globals()[tool_call_name](**func_args)
                    else:
                        func_response = globals()[tool_call_name](**func_args)
                except Exception as e:
                    logging.error(f"Failed to call function: {tool_call_name} with error: {e}")
                    func_response = str("An Exception occurred while calling the function.")
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
