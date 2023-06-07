import openai
import tempfile
import os

# Set the OpenAI API key
openai.api_key = 'YOUR API KEY '

# Load the audio file
audio_file_path = r"File Path"
with open(audio_file_path, "rb") as audio_file:
    audio_content = audio_file.read()

# Create a temporary file with .mp3 extension
temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
temp_file.write(audio_content)
temp_file.close()

# Transcribe the audio
with open(temp_file.name, "rb") as temp_audio_file:
    transcript = openai.Audio.transcribe("whisper-1", file=temp_audio_file)

print (transcript)
# Get questions from user input
questions = []
num_questions = int(input("Enter the number of questions: "))
for i in range(num_questions):
    question = input(f"Enter question #{i+1}: ")
    questions.append(question)

# Generate responses for each question
for question in questions:
    # Prompt for GPT-3.5
    gpt_input = f"Question: {question}\nTranscript: {transcript['text']}"

    # Use GPT-3.5 to process the prompt
    gpt_response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=gpt_input,
        max_tokens=100,
    )

    # Extract the generated text from GPT-3.5 response
    gpt_output = gpt_response['choices'][0]['text']

    # Print the question and the generated answer
    print("Question:", question)
    print("GPT-3.5 Answer:", gpt_output)
    print()

# Clean up the temporary file
os.unlink(temp_file.name)