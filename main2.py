import tkinter as tk
from tkinter import filedialog
import requests
import time
import os


def send_to_api(line): #functiont that collects all the data and sends it to the ooba API
    api_url = "http://127.0.0.1:5000/v1/chat/completions" #url for the api endpoint
    headers = {"Content-Type": "application/json"} #content header
    data = { #data field
        "messages": [{
            "role": "user", #tell the api that this script is a user
            "content": line #the prompt is just the code line
        }],
        "max_tokens": 30, #limit the number of tokens
        "temperature": 0.6, #keep the temperature low
        "mode": "chat", #chat mode
        "character": "CodeCom Mentor" #select the codecom character
    }

    response = requests.post(api_url, headers=headers, json=data, verify=False) #make the api call

    if response.status_code == 200: #200 is the success code
        response = response.json()['choices'][0]['message']['content'] #take the json the API returns and store the content
        no_newlines = response.replace('\n', ' ') #remove all the newline chars from the content
        final_comment = no_newlines.split('. ', 1)[0] #remove everything after the first period and space to avoid bad responses
        return final_comment #return the comment
    else:
        print("Error with API")
        return ""


def choose_file():  #function to pick a file
    global selected_file
    selected_file = filedialog.askopenfilename(filetypes=[("Java Files", "*.java")]) #open a file picking window
    if selected_file:
        file_label.config(text="File selected: " + selected_file)


def generate_comments():  #comment creating function
    with open(selected_file, 'r') as file: #open the java file in read mode
        lines = file.readlines() #read in the lines

    filtered_lines = [] #create an empty list to store the filtered lines of code
    for line in lines: #run through the lines
        line_no_spaces = line.strip() ##strip the whitespaces
        if not line_no_spaces or "public static void main(String[] args)" in line_no_spaces or "class " in line_no_spaces or line_no_spaces in ['{', '}']:
            filtered_lines.append(line) #add the lines that pass the filter to the new_lines
            continue

        api_response = send_to_api(line_no_spaces) #send the clean line to the API
        if api_response: #if the API did respond
            filtered_lines.append(line.rstrip('\n') + " // " + api_response + '\n') #remove all the newlines from the code so the comment is placed beside the code
        else: #if it didn't respond
            filtered_lines.append(line) #just send back the original line of code.
        time.sleep(10) #hold for 10 seconds as to not overwhelm the API


    with open(selected_file, 'w') as file: #open the original java file in write mode
        file.writelines(filtered_lines) #put all the now commented original lines in the original java file
        os.system('afplay /System/Library/Sounds/Glass.aiff') #play a system sound to let the user know it's done


#GUI bits
root = tk.Tk()
root.title("Java Comment Generator")
root.geometry("500x250")

selected_file = None

file_label = tk.Label(root, text="No file picked")
file_label.pack(pady=10)

select_button = tk.Button(root, text="Pick Java File", command=choose_file) #select file button
select_button.pack(pady=10)

comment_button = tk.Button(root, text="Start Commenting", command=generate_comments) #generate comments button
comment_button.pack(pady=10)

root.mainloop()
