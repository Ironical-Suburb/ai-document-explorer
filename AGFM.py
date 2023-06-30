import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import pandas as pd
import PyPDF2
from PIL import Image
import openai

# Global variables
chat_sessions = [{"transcript": "", "folder_path": "", "file_types": []}]
current_session = 0
openai.api_key = 'SAMPLE API KEY'

def generate_answer(question, folder_path):
    transcript = chat_sessions[current_session]["transcript"]
    file_types = chat_sessions[current_session]["file_types"]

    # Read files from the folder and extract text
    document_texts = []
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path):
            document_text = extract_text_from_file(file_path)
            if document_text:
                document_texts.append(document_text)

    # Generate response using the extracted document texts
    transcript += f"User: {question}\n"
    for i, text in enumerate(document_texts):
        transcript += f"Document {i+1}:\n{text}\n"

    # Use GPT-3.5 to generate answer
    gpt_response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=transcript,
        max_tokens=100,
    )

    # Extract the generated text from GPT-3.5 response
    gpt_output = gpt_response.choices[0].text.strip()
    transcript += f"AI: {gpt_output}\n"

    return transcript

def generate_answer_thread(question, folder_path):
    transcript = generate_answer(question, folder_path)
    conversation_text.config(state=tk.NORMAL)
    conversation_text.insert(tk.END, transcript + "\n")
    conversation_text.config(state=tk.DISABLED)
    conversation_text.see(tk.END)

def submit_question(event=None):
    question = entry.get().strip()
    folder_path = chat_sessions[current_session]["folder_path"]
    
    if question and folder_path:
        generate_answer_thread(question, folder_path)
        entry.delete(0, tk.END)
    else:
        messagebox.showwarning("Invalid Input", "Please select a folder and enter a question.")


def handle_submit():
    submit_question()

def switch_session(event):
    global current_session
    selected_session = session_dropdown.current()
    if selected_session < len(chat_sessions):
        chat_session = chat_sessions[selected_session]
        transcript = chat_session["transcript"]
        conversation_text.config(state=tk.NORMAL)
        conversation_text.delete("1.0", tk.END)
        conversation_text.insert(tk.END, transcript)
        conversation_text.config(state=tk.DISABLED)
        conversation_text.see(tk.END)
        current_session = selected_session

def open_folder_dialog():
    folder_path = filedialog.askdirectory()
    if folder_path:
        chat_sessions[current_session]["folder_path"] = folder_path
        messagebox.showinfo("Success", "Folder selected successfully.")

def extract_text_from_file(file_path):
    _, file_extension = os.path.splitext(file_path)
    file_extension = file_extension.lower()

    if file_extension == ".pdf":
        return extract_text_from_pdf(file_path)
    elif file_extension == ".xlsx" or file_extension == ".xls":
        return extract_text_from_excel(file_path)
    elif file_extension == ".csv":
        return extract_text_from_csv(file_path)
    elif file_extension == ".jpg" or file_extension == ".jpeg" or file_extension == ".png":
        return extract_text_from_image(file_path)
    else:
        messagebox.showwarning("Unsupported File", "The selected file is not supported.")
        return None


def extract_text_from_pdf(file_path):
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page_number in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_number]
            text += page.extract_text()
        return text

def extract_text_from_excel(file_path):
    try:
        df = pd.read_excel(file_path)
        text = df.to_string(index=False)
        messagebox.showinfo("File Read", f"Excel file successfully read: {file_path}")
        return text
    except Exception as e:
        messagebox.showwarning("Excel Error", f"Failed to read Excel file:\n{str(e)}")
        return None

def extract_text_from_csv(file_path):
    try:
        df = pd.read_csv(file_path)
        text = df.to_string(index=False)
        messagebox.showinfo("File Read", f"CSV file successfully read: {file_path}")
        return text
    except Exception as e:
        messagebox.showwarning("CSV Error", f"Failed to read CSV file:\n{str(e)}")
        return None

def extract_text_from_image(file_path):
    try:
        image = Image.open(file_path)
        text = image.tobytes().decode('utf-8', 'ignore')
        messagebox.showinfo("File Read", f"Image file successfully read: {file_path}")
        return text
    except Exception as e:
        messagebox.showwarning("Image Error", f"Failed to process image:\n{str(e)}")
        return None

# Create the main window
window = tk.Tk()
window.title("AI Chat")

# Create the conversation text area
conversation_frame = ttk.Frame(window, padding="10")
conversation_frame.pack(fill=tk.BOTH, expand=True)

conversation_text = tk.Text(conversation_frame, wrap=tk.WORD, state=tk.DISABLED)
conversation_text.pack(fill=tk.BOTH, expand=True)

scrollbar = ttk.Scrollbar(conversation_frame, command=conversation_text.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
conversation_text.configure(yscrollcommand=scrollbar.set)

# Create the question entry field
entry_frame = ttk.Frame(window, padding="10")
entry_frame.pack(fill=tk.BOTH)

entry = ttk.Entry(entry_frame)
entry.bind("<Return>", submit_question)
entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

submit_button = ttk.Button(entry_frame, text="Submit", command=submit_question)
submit_button.pack(side=tk.LEFT)

# Create the file selection button
file_frame = ttk.Frame(window, padding="10")
file_frame.pack(fill=tk.BOTH)

folder_button = ttk.Button(file_frame, text="Open Folder", command=open_folder_dialog)
folder_button.pack(side=tk.LEFT)

# Create a dropdown for switching between chat sessions
session_frame = ttk.Frame(window, padding="10")
session_frame.pack(fill=tk.BOTH)

session_label = ttk.Label(session_frame, text="Chat Session:")
session_label.pack(side=tk.LEFT)

session_dropdown = ttk.Combobox(session_frame, values=list(range(len(chat_sessions))), state="readonly")
session_dropdown.current(0) 
session_dropdown.bind("<<ComboboxSelected>>", switch_session)
session_dropdown.pack(side=tk.LEFT)

# Start the main event loop
window.mainloop()
