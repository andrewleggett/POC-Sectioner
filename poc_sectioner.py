import ctypes
import customtkinter as ctk
import tkinter as tk
import requests
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import sys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import Select

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Hide the console window
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

        self.title("POC Sectioner")
        self.geometry("600x700")

        self.current_version = "1.0.2"  # Set your current version here

        instructions_text = (
            "Enter Section IDs and UserIDs below.\n\n"
            "Once you click Submit, a window will appear and you will have to log in to Pearson Online Classroom and complete the 2FA authentication.\n\n"
            "NB: This tool will not work if you do not have sectioning rights on your POC account.\n\n"
            "If you encounter any bugs or issues, please contact Andrew Leggett (andrew.leggett@200r.uk)\n"
            "There has been a bug reported where sections with more than 400 students don't save the last page of students. If you have a section with more than 400 students, please reach out to me - I need sections to test fixes on!\n"
            "You can also bypass the issue by entering the section multiple times, and splitting the students between them so that no one entry has more than 400 students."
        )

        self.instructions = ctk.CTkLabel(self, text=instructions_text, wraplength=550)
        self.instructions.pack(pady=10)

        self.frame = ctk.CTkScrollableFrame(self, width=550, height=400)
        self.frame.pack(pady=10)

        self.input_pairs = []
        self.add_input_pair()

        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.pack(pady=10, padx=10, fill="x")

        self.add_remove_label = ctk.CTkLabel(self.button_frame, text="Add or remove additional sections:")
        self.add_remove_label.grid(row=0, column=0, padx=5, sticky="w")

        self.add_button = ctk.CTkButton(self.button_frame, text="+", command=self.add_input_pair, width=30, height=30)
        self.add_button.grid(row=0, column=1, padx=5)

        self.remove_button = ctk.CTkButton(self.button_frame, text="-", command=self.remove_input_pair, width=30, height=30)
        self.remove_button.grid(row=0, column=2, padx=5)

        # Adding empty columns to create space
        self.button_frame.grid_columnconfigure(3, weight=1)

        self.submit_button = ctk.CTkButton(self.button_frame, text="Submit", command=self.submit)
        self.submit_button.grid(row=0, column=4, padx=5, sticky="e")

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
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

        # Navigate to the login page and perform login and 2FA authentication
        login_url = "https://www.connexus.com/"  # Replace with the actual login URL
        driver.get(login_url)

        # Wait until there is a class portalletTitle on the page with the text "Curriculum Management"
        try:
            WebDriverWait(driver, 900).until(EC.presence_of_element_located((By.CLASS_NAME, 'portalletTitle')))
        except TimeoutException:
            print("Timeout occurred. Returning to login URL.")
            driver.get(login_url)
            return

        for section_id_entry, user_ids_entry in self.input_pairs:
            section_id = section_id_entry.get()
            user_ids = user_ids_entry.get("1.0", "end-1c")

            self.process_section(driver, section_id, user_ids)

        driver.quit()

    def process_section(self, driver, section_id, user_ids):
        url = f"https://www.connexus.com/lmu/sections/webusers.aspx?idSection={section_id}"
        driver.get(url)

        # Wait until the input element with ID 'users_search' is present
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'users_search')))
        except TimeoutException:
            print("Timeout occurred. Returning to login URL.")
            driver.get("https://www.connexus.com/")
            return

        # Insert the UserIDs into the input element
        user_ids_input = driver.find_element(By.ID, 'users_search')
        user_ids_input.clear()
        user_ids_input.send_keys(user_ids.replace("\n", ","))

        # Check for Variation 1
        try:
            all_users_radio = driver.find_element(By.ID, 'users_allUsersAtLocation')
            if not all_users_radio.is_selected():
                all_users_radio.click()

            members_only_checkbox = driver.find_element(By.ID, 'users_membersOnly')
            if members_only_checkbox.is_selected():
                members_only_checkbox.click()
        except:
            # Variation 2
            section_filter_radio = driver.find_element(By.ID, 'users_sectionFilter_2')
            if not section_filter_radio.is_selected():
                section_filter_radio.click()

        # Click the search button
        search_button = driver.find_element(By.ID, 'users_searchButton')
        search_button.click()

        # Wait until the page has finished loading
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'users_search')))
        except TimeoutException:
            print("Timeout occurred. Returning to login URL.")
            driver.get("https://www.connexus.com/")
            return

        # Get the number of users in the section
        num_users_text = driver.find_element(By.ID, 'users_grid_ctl01_lblNumRecords').text
        if '(' in num_users_text:
            total_users = int(num_users_text.split('(')[1].split(' ')[0])
        else:
            total_users = 0  # Assume less than 200 users if no parentheses

        # Process users in pages
        page_number = 1
        while True:
            # Set the selected index of all select elements on the page that contain a value that is exactly "Student"
            select_elements = driver.find_elements(By.XPATH, "//select[option[text()='Student']]")
            for select_element in select_elements:
                select = Select(select_element)
                select.select_by_visible_text('Student')

            # Click the save button
            save_button = driver.find_element(By.ID, 'saveButton')
            save_button.click()

            # Wait until the page has finished loading
            try:
                WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.ID, 'users_grid_ctl01_historyImageLink')))
            except TimeoutException:
                print("Timeout occurred. Returning to login URL.")
                driver.get("https://www.connexus.com/")
                return

            # Check if we need to go to the next page
            if total_users <= 200:
                break

            # Find the next page link
            next_page_link = driver.find_element(By.XPATH, f"//td[@id='users_grid_ctl01_pagerHeaderCell']//a[text()='{page_number + 1}']")
            next_page_link.click()

            # Wait until the page has finished loading
            try:
                WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.ID, 'users_grid_ctl01_historyImageLink')))
            except TimeoutException:
                print("Timeout occurred. Returning to login URL.")
                driver.get("https://www.connexus.com/")
                return

            page_number += 1
            if page_number * 200 >= total_users:
                break

if __name__ == "__main__":
    app = App()
    app.mainloop()

#pyinstaller --onefile --icon=icons/icon128.ico --name=POC Sectioner poc_sectioner.py