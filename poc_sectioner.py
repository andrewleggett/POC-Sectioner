import customtkinter as ctk
import tkinter as tk
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("POC Sectioner")
        self.geometry("600x600")

        instructions_text = (
            "Enter Section IDs and UserIDs below.\n\n"
            "Once you click Submit, a window will appear and you will have to log in to Pearson Online Classroom and complete the 2FA authentication.\n\n"
            "NB: This tool will not work if you do not have sectioning rights on your POC account."
        )

        self.instructions = ctk.CTkLabel(self, text=instructions_text, wraplength=550)
        self.instructions.pack(pady=10)

        self.frame = ctk.CTkScrollableFrame(self, width=550, height=400)
        self.frame.pack(pady=10)

        self.input_pairs = []
        self.add_input_pair()

        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.pack(pady=10, padx=10, fill="x")

        self.add_button = ctk.CTkButton(self.button_frame, text="+", command=self.add_input_pair, width=30, height=30)
        self.add_button.grid(row=0, column=0, padx=5)

        self.remove_button = ctk.CTkButton(self.button_frame, text="-", command=self.remove_input_pair, width=30, height=30)
        self.remove_button.grid(row=0, column=1, padx=5)

        # Adding empty columns to create space
        self.button_frame.grid_columnconfigure(2, weight=1)

        self.submit_button = ctk.CTkButton(self.button_frame, text="Submit", command=self.submit)
        self.submit_button.grid(row=0, column=3, padx=5, sticky="e")

    def add_input_pair(self):
        pair_frame = ctk.CTkFrame(self.frame)
        pair_frame.pack(pady=5, fill="x")

        section_id_label = ctk.CTkLabel(pair_frame, text="Section ID:")
        section_id_label.pack(side="left", padx=5)

        section_id_entry = ctk.CTkEntry(pair_frame, width=100)
        section_id_entry.pack(side="left", padx=5)

        user_ids_label = ctk.CTkLabel(pair_frame, text="User IDs:")
        user_ids_label.pack(side="left", padx=5)

        user_ids_entry = ctk.CTkTextbox(pair_frame, height=4, width=300)
        user_ids_entry.pack(side="left", padx=5)

        self.input_pairs.append((section_id_entry, user_ids_entry))

    def remove_input_pair(self):
        if len(self.input_pairs) > 1:
            pair_frame = self.input_pairs.pop()
            pair_frame[0].master.pack_forget()
            pair_frame[0].master.destroy()

    def submit(self):
        for section_id_entry, user_ids_entry in self.input_pairs:
            section_id = section_id_entry.get()
            user_ids = user_ids_entry.get("1.0", "end-1c")

            if self.validate_section_id(section_id) and self.validate_user_ids(user_ids):
                self.process_section(section_id, user_ids)
            else:
                print(f"Invalid input for Section ID: {section_id} or User IDs: {user_ids}")

    def validate_section_id(self, section_id):
        return section_id.isdigit() and len(section_id) > 4

    def validate_user_ids(self, user_ids):
        user_ids_list = user_ids.replace("\n", ",").split(",")
        return all(user_id.isdigit() for user_id in user_ids_list)

    def process_section(self, section_id, user_ids):
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        url = f"https://www.connexus.com/lmu/sections/webusers.aspx?idSection={section_id}"
        driver.get(url)

        # Add your Selenium automation code here
        # For example, you might want to interact with the webpage using driver.find_element(By.ID, "element_id")

        driver.quit()

if __name__ == "__main__":
    app = App()
    app.mainloop()
