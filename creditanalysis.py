import tkinter as tk 
from tkinter import filedialog
from PyPDF2 import PdfReader
import re
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer

class App:
    def __init__(self, root):
        self.root = root
        self.root.geometry('300x200')
        self.root.title("Credit Report Scraper")

        # create a button for the upload of the PDF
        self.upload_button = tk.Button(root, text="Upload Credit Report", command=self.upload)
        self.upload_button.pack(pady=20)

        # label that displays the result of the credit report analysis
        self.result_label = tk.Label(root, text="")
        self.result_label.pack(pady=20)

    def upload(self):
        filename = filedialog.askopenfilename(initialdir="/", title="Select File",
                                              filetypes=(("pdf files", "*.pdf"), ("all files", "*.*")))

        if filename:
            self.scrape_pdf(filename)

    def scrape_pdf(self, filename):
        vantage_score = None
        for page_layout in extract_pages(filename):
            for element in page_layout:
                if isinstance(element, LTTextContainer):
                    for text_line in element:
                        for character in text_line:
                            if isinstance(character, LTChar) and character.get_text() == "Vantage Score 3.0":
                                next_box = text_line.get_bbox().x1 + 1  # Adjust this value as needed
                                vantage_score = self.extract_score_from_box(page_layout, next_box)
                                break

        if vantage_score:
            if self.check_vantage_score(vantage_score) and self.check_late_payments(text):
                self.result_label['text'] = "This is a great funding candidate!"
                self.reason_label['text'] = "Reason: High credit score and few late payments."
            else:
                self.result_label['text'] = "This candidate will more than likely not be approved"
                self.reason_label['text'] = "Reason: Low credit score or too many late payments."
        else:
            print("Could not find Vantage Score 3.0 in text.")

    def extract_score_from_box(self, page_layout, x_max):
        score = ""
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                for text_line in element:
                    for character in text_line:
                        if isinstance(character, LTChar) and character.get_bbox().x0 > x_max:
                            score += character.get_text()
        return score

    @staticmethod
    def check_credit(text):
        # Credit Check Algorithm 
        match = re.search(r"Credit Score: (\d+)", text)
        if match:
            return int(match.group(1)) > 700
        else:
            return False

    @staticmethod
    def check_vantage_score(text):
        match = re.search(r"Vantage Score 3.0:\s*(\d{3})", text)
        if match:
            return int(match.group(1)) > 700
        else:
            return False

    @staticmethod
    def check_late_payments(text):
        # Late payments algorithm
        return len(re.findall(r"Late Payment", text)) <= 2

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()


#check if scores are being scraped properly
print(text)
