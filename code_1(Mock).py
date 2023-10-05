import speech_recognition as sr
import openai
from gtts import gTTS
import os
import tempfile
import random

# Set your OpenAI API key
api_key = "" 
# Create a recognizer instance
recognizer = sr.Recognizer()
# Initialize the OpenAI API client
openai.api_key = api_key

# Mock OBD-II functionality
MOCK_DTCS = ["P0300", "P0420", "P0171", "P0455", "P0401", "P0131"]
MOCK_DATA = {
    "RPM": "3000 RPM",
    "SPEED": "60 km/h",
    "THROTTLE_POS": "20%",
    "ENGINE_LOAD": "75%",
    "COOLANT_TEMP": "90°C"
}

def get_mock_dtcs():
    return random.sample(MOCK_DTCS, random.randint(0, len(MOCK_DTCS)))

def get_mock_real_time_data():
    keys = random.sample(list(MOCK_DATA.keys()), random.randint(0, len(MOCK_DATA)))
    return {key: MOCK_DATA[key] for key in keys}

def speak_audio(text):
    tts = gTTS(text=text, lang='en')
    with tempfile.NamedTemporaryFile(delete=True) as fp:
        tts.save(fp.name + ".mp3")
        os.system(f"mpg123 {fp.name}.mp3")

def recognize_voice():
    with sr.Microphone() as source:
        print("Listening for a command...")
        #Giving ears to the program, it differiantes between the voice and the background noise.
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source)
            user_input = recognizer.recognize_google(audio).lower()
            print(f"You said: {user_input}")
            return user_input
        except sr.WaitTimeoutError:
            print("No speech detected. Please speak.")
            return None
        except sr.UnknownValueError:
            print("Could not understand the audio. Please try again.")
            return None

def respond_to_user_command(user_command):
    if "scan my car for errors" in user_command:
        dtcs = get_mock_dtcs()
        if dtcs:
            return "The scan completed. Here are the Diagnostic Trouble Codes: " + ", ".join(dtcs)
        else:
            return "The scan completed with no errors found."

    if "get car data" in user_command:
        data = get_mock_real_time_data()
        if data:
            data_strings = [f"{key}: {value}" for key, value in data.items()]
            return "Here's some data from your car: " + ", ".join(data_strings)
        else:
            return "Couldn't retrieve any data at this time."

    # Handle other commands using OpenAI
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_command}
            ]
        )
        assistant_response = response['choices'][0]['message']['content']
        return assistant_response
    except Exception as e:
        print(f"Error: {e}")
        return "An error occurred while processing your request."

def output_response(assistant_response):
    print("\nHow would you like to receive the response?")
    print("1. Hear it")
    print("2. See it (print on screen)")
    choice = input("Please select an option (1/2): ")

    if choice == "1":
        speak_audio(assistant_response)
    elif choice == "2":
        print(f"\nAssistant: {assistant_response}")
    else:
        print("Invalid choice. Defaulting to print on screen.")
        print(f"\nAssistant: {assistant_response}")

def display_menu():
    print("\nTauseeq's Voice/Text Assistant")
    print("How would you like to provide your command?")
    print("1. Speak")
    print("2. Type")

def continue_or_exit():
    choice = input("Would you like to continue or exit? (Type 'Y/N' or 'exit'): ").lower()
    return choice == 'y'

def main():
    print("Tauseeq's Voice/Text Assistant is ready.")
    while True:
        display_menu()
        choice = input("Please select an option (1/2): ")

        if choice == "1":
            user_input = recognize_voice()
            if user_input:
                response = respond_to_user_command(user_input)
                output_response(response)
        elif choice == "2":
            user_input = input("\nPlease type your command: ")
            response = respond_to_user_command(user_input)
            output_response(response)
        else:
            print("Invalid choice. Please select a valid option (1/2).")

        if not continue_or_exit():
            print("Exiting Voice/Text Assistant. Goodbye!")
            break

if __name__ == "__main__":
    main()
