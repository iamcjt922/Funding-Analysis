import tkinter as tk 
from tkinter import filedialog
from PyPDF2 import PdfReader
import re
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar

class App:
    def __init__(self, root):
        self.root = root
        self.root.geometry('300x200')
        self.root.title("Credit Report Scraper")

        self.upload_button = tk.Button(root, text="Upload Credit Report", command=self.upload)
        self.upload_button.pack(pady=20)

        self.result_label = tk.Label(root, text="")
        self.result_label.pack(pady=10)

    def upload(self):
        filename = filedialog.askopenfilename(initialdir="/", title="Select File",
                                              filetypes=(("pdf files", "*.pdf"), ("all files", "*.*")))

        if filename:
            self.scrape_pdf(filename)

    def scrape_pdf(self, filename):
        vantage_score = None
        transunion_score = None
        equifax_score = None
        experian_score = None

        for page_layout in extract_pages(filename):
            for element in page_layout:
                if isinstance(element, LTTextContainer):
                    text = element.get_text().strip()
                    if text.startswith("Vantage Score 3.0"):
                        vantage_score = self.extract_score_from_grid(page_layout, element.index + 1)
                        transunion_score = self.extract_score_from_grid(page_layout, element.index + 2)
                        equifax_score = self.extract_score_from_grid(page_layout, element.index + 3)
                        experian_score = self.extract_score_from_grid(page_layout, element.index + 4)
                        break

        if vantage_score:
            self.result_label['text'] = f"Vantage Score: {vantage_score}\n" \
                                         f"Transunion Score: {transunion_score}\n" \
                                         f"Equifax Score: {equifax_score}\n" \
                                         f"Experian Score: {experian_score}"
        else:
            self.result_label['text'] = "Could not find Vantage Score 3.0 in the credit report."

    def extract_score_from_grid(self, page_layout, index):
        score = ""
        for element in page_layout:
            if isinstance(element, LTTextContainer) and element.index == index:
                score = element.get_text().strip()
                break
        return score

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
