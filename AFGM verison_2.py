import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import openai
import tempfile
import os
import PyPDF2
import threading

# Set the OpenAI API key
openai.api_key = 'Your API KEY'

transcript = None
document_text = None

def transcribe_audio():
    # Load the audio file
    audio_file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3")])
    if not audio_file_path:
        return

    with open(audio_file_path, "rb") as audio_file:
        audio_content = audio_file.read()

    # Create a temporary file with .mp3 extension
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    temp_file.write(audio_content)
    temp_file.close()

    # Transcribe the audio
    with open(temp_file.name, "rb") as temp_audio_file:
        global transcript
        transcript = openai.Audio.transcribe("whisper-1", file=temp_audio_file)

    # Clean up the temporary file
    os.unlink(temp_file.name)

    return transcript

def transcribe_pdf():
    # Select the PDF file
    pdf_file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    if not pdf_file_path:
        return

    # Read the PDF document
    with open(pdf_file_path, "rb") as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        num_pages = len(pdf_reader.pages)
        global document_text
        document_text = ""

        # Extract the text from each page
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            document_text += page_text

    return document_text

def generate_answer(question, transcript=None, document_text=None):
    # Generate response for the question
    if transcript is not None:
        gpt_input = f"Question: {question}\nTranscript: {transcript['text']}"
    elif document_text is not None:
        gpt_input = f"Question: {question}\nDocument: {document_text}"
    else:
        gpt_input = question

    # Use GPT-3.5 to process the prompt
    gpt_response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=gpt_input,
        max_tokens=100,
    )

    # Extract the generated text from GPT-3.5 response
    gpt_output = gpt_response['choices'][0]['text']

    return gpt_output

def handle_submit():
    question = entry.get()
    if not question:
        messagebox.showwarning("Error", "Please enter a question.")
        return

    # Change the button to a dot to indicate thinking
    arrow_button.config(text="●", state=tk.DISABLED)

    def generate_answer_thread():
        global transcript
        global document_text
        nonlocal question

        answer = generate_answer(question, transcript=transcript, document_text=document_text)

        # Update the conversation text widget with the question and answer
        conversation_text.insert(tk.END, f"Question: {question}\nAnswer: {answer}\n\n")
        entry.delete(0, tk.END)

        # Change the button back to arrow and enable it
        arrow_button.config(text="➜", state=tk.NORMAL)

    # Start a thread to generate the answer
    threading.Thread(target=generate_answer_thread).start()

def submit_question(event=None):
    handle_submit()

# Create the main window
window = tk.Tk()
window.title("Tech Chat Bot")
window.geometry("800x600")

# Set the background image
background_image = Image.open("techbackground.jpg")
background_photo = ImageTk.PhotoImage(background_image)
background_label = tk.Label(window, image=background_photo)
background_label.place(relwidth=1, relheight=1)

# Create the conversation text widget
conversation_text = tk.Text(window, bg="#303030", fg="white", wrap=tk.WORD, font=("Arial", 12))
conversation_text.pack(padx=20, pady=20)

# Create the question entry widget
entry_frame = tk.Frame(window, bg="#303030")
entry_frame.pack(padx=20, pady=(10, 0), fill=tk.X)

entry = tk.Entry(entry_frame, bg="white", fg="black", font=("Arial", 12))
entry.pack(side=tk.LEFT, padx=(0, 5))

# Create the arrow button
arrow_button = tk.Button(
    entry_frame,
    text="➜",
    bg="#303030",
    fg="white",
    font=("Arial", 12, "bold"),
    relief=tk.FLAT,
    activebackground="#303030",
    command=handle_submit
)
arrow_button.pack(side=tk.RIGHT, padx=(0, 3))

# Bind the <Return> key event to submit the question
window.bind("<Return>", submit_question)

# Create the convert PDF and convert audio buttons
button_frame = tk.Frame(window, bg="#303030")
button_frame.pack(pady=(10, 0))

convert_pdf_button = tk.Button(
    button_frame,
    text="Convert PDF",
    bg="#303030",
    fg="white",
    font=("Arial", 12, "bold"),
    relief=tk.FLAT,
    activebackground="#303030",
    activeforeground="white",
    command=transcribe_pdf
)
convert_pdf_button.pack(side=tk.LEFT, padx=(0, 10))

convert_audio_button = tk.Button(
    button_frame,
    text="Convert Audio",
    bg="#303030",
    fg="white",
    font=("Arial", 12, "bold"),
    relief=tk.FLAT,
    activebackground="#303030",
    activeforeground="white",
    command=transcribe_audio
)
convert_audio_button.pack(side=tk.LEFT)

# Start the main event loop
window.mainloop()
