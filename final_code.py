import speech_recognition as sr
import openai
from gtts import gTTS
import os
import tempfile
import obd

# Set your OpenAI API key
api_key = "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"
# Create a recognizer instance
recognizer = sr.Recognizer()
# Initialize the OpenAI API client
openai.api_key = api_key
# Create an OBD-II connection(Intializing the connection)
connection = obd.OBD()

#This Functions converts the output to audio and plays it.
def speak_audio(text):
    #tts intializes the text to speech engine powered by google.
    tts = gTTS(text=text, lang='en')
    # with is used for file handling, we create a temporary file as fp
    with tempfile.NamedTemporaryFile(delete=True) as fp:
        #tts function saves the mp3 file to the temporary mp3 file.
        tts.save(fp.name + ".mp3")
        # os.system is used to play the mp3 file.
        os.system(f"mpg123 {fp.name}.mp3")

#This function takes the voice input from the user and returns it.
def recognize_voice():
    # sr.Microphone instantiates the microphone as source.
    with sr.Microphone() as source:
        print("Listening for a command...")
        #Giving ears to the program, it differiantes between the voice and the background noise.
        recognizer.adjust_for_ambient_noise(source)
        #try and except is used to catch errors.
        try:
            #listen function takes the source as input and returns the audio.
            audio = recognizer.listen(source)
            #recognize_google function takes the audio as input and returns the text.
            user_input = recognizer.recognize_google(audio).lower()
            print(f"You said: {user_input}")
            return user_input
        #If the program is unable to recognize the voice, it will throw an error.
        except sr.WaitTimeoutError:
            print("No speech detected. Please speak.")
            return None
        #If the program is unable to understand the audio, it will throw an error.
        except sr.UnknownValueError:
            print("Could not understand the audio. Please try again.")
            return None
        
#This function takes the user input and returns the output from the OpenAI API.
def respond_to_user_command(user_command):
    #The ChatCompletion function returns the output from the OpenAI API and stores it in the response variable.
    response = openai.ChatCompletion.create(
        #This indicates that the underlying language model that should be used for the response generation
        model="gpt-4", 
        #This is a list of message objects that provides a conversation context for the model setting and input setting. 
        messages=[
            #Role Can be either 'system', 'user' (for the response generation).
            # Content sets behaviour of the model or system level directive for better reponses.
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_command}
        ]
    )
    #
    #The response variable contains multiple outputs from the OpenAI API in a file from which we select the first output.
    assistant_response = response['choices'][0]['message']['content']
    return assistant_response

#This function takes the input from the OpenAI API and asks how the user wants to receive the response.
def output_response(assistant_response):
    print("\nHow would you like to receive the response?")
    print("1. Hear it")
    print("2. See it (print on screen)")
    choice = input("Please select an option (1/2): ")

    #If the user wants to hear the response, speak_audio function is called.
    if choice == "1":
        speak_audio(assistant_response)
    #
    #If the user wants to see the response on the screen, it is printed.
    else:
        print(f"\nAssistant: {assistant_response}")

# OBD Functions for BMW and OBD II 

#This function returns dtc codes from the OBD II.
def get_dtc_codes():
    #obd.commands.DTC returns the dtc codes from the OBD II and stores it in the cmd variable.
    cmd = obd.commands.GET_DTC
    #The response variable stores the information retreived from the OBD system of the car.
    # Query is used to get the information by using the parameter of DTC codes earlier stored in cmd.
    response = connection.query(cmd) # if reponse value is null, it returns "No DTC codes found or else prints the DTC codes."
    return ", ".join(response.value) if response.value else "No DTC codes found."

#This function clears the dtc codes from the OBD II.
def clear_dtc_codes():
    cmd = obd.commands.CLEAR_DTC
    response = connection.query(cmd)
    return "DTC codes cleared successfully!" if response.is_null() else "Failed to clear DTC codes."

#This function returns the Engine RPM from the OBD II.
def get_engine_rpm():
    cmd = obd.commands.RPM
    response = connection.query(cmd)
    return f"Engine RPM: {response.value.magnitude} rpm"

#This function returns the Vehicle Speed from the OBD II.
def get_vehicle_speed():
    cmd = obd.commands.SPEED
    response = connection.query(cmd)
    return f"Vehicle Speed: {response.value.magnitude} km/h"

#This function returns the coolant temperature from the OBD II.
def get_coolant_temp():
    cmd = obd.commands.COOLANT_TEMP
    response = connection.query(cmd)
    return f"Coolant Temperature: {response.value.magnitude} °C"

#This function returns the Vehicle Identification Number (VIN) from the OBD II.
def get_vehicle_info():
    cmd = obd.commands.VIN
    response = connection.query(cmd)
    return f"Vehicle Identification Number (VIN): {response.value}"

#This function returns the emission-related fault codes from the OBD II.
def get_emission_readiness_status():
    cmd = obd.commands.GET_DTC
    response = connection.query(cmd)
    if response.is_null():
        return "No emission-related fault codes detected."
    return f"Emission-Related Fault Codes: {', '.join(response.value)}"

#This function returns the freeze frame data from the OBD II.
def get_freeze_frame_data():
    cmd = obd.commands.FREEZE_DTC
    response = connection.query(cmd)
    if response.is_null():
        return "No freeze frame data available."
    return f"Freeze Frame Data: {', '.join(response.value)}"

# This is the main function which calls all the other functions.
def main_menu():
    #This while loop is used to keep the program running until the user chooses to exit.
    while True:
        #This is the main menu which is displayed to the user.
        print("\nWelcome to Tauseeq's BMW AI!")
        print("1. Chat with GPT-4")
        print("2. Get DTC Codes")
        print("3. Clear DTC Codes")
        print("4. Get Engine RPM")
        print("5. Get Vehicle Speed")
        print("6. Get Coolant Temperature")
        print("7. Get Vehicle Information")
        print("8. Get Emission Readiness Status")
        print("9. Get Freeze Frame Data")
        print("10. Exit")

        #The choice variable stores the user input.
        choice = input("Please select an option: ")

        #Input is evaluated and the corresponding function is called.
        if choice == "1":
            user_input_method = input("Do you want to type or speak your command? (type/speak): ")
            if user_input_method == "speak":
                user_input = recognize_voice()
            else:
                user_input = input("Please type your command: ")
            
            response = respond_to_user_command(user_input)
            output_response(response)

        elif choice == "2":
            output_response(get_dtc_codes())
        elif choice == "3":
            output_response(clear_dtc_codes())
        elif choice == "4":
            output_response(get_engine_rpm())
        elif choice == "5":
            output_response(get_vehicle_speed())
        elif choice == "6":
            output_response(get_coolant_temp())
        elif choice == "7":
            output_response(get_vehicle_info())
        elif choice == "8":
            output_response(get_emission_readiness_status())
        elif choice == "9":
            output_response(get_freeze_frame_data())
        elif choice == "10":
            print("Exiting Tauseeq's BMW AI. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")
        
        #This is used to check if the user wants to return to the main menu or exit and doesnt let the program terminate.
        proceed = input("Do you want to return to main menu or exit? (menu/exit): ")
        if proceed == "exit":
            print("Exiting Tauseeq's BMW AI. Goodbye!")
            break

main_menu()
