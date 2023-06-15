from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog
from PyPDF2 import PdfReader
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer


class SplashScreen(tk.Toplevel):
    def __init__(self, parent):
        tk.Toplevel.__init__(self, parent)
        self.parent = parent
        self.title("Splash Screen")
        self.minsize(720, 400)  # Set the minimum size of the splash screen

        # Load the logo image with transparency
        logo_image = Image.open("images/logo.png")
        self.logo_image = ImageTk.PhotoImage(logo_image)

        self.logo_label = tk.Label(self, image=self.logo_image)
        self.logo_label.pack(pady=20)

        self.copyrighlabel = tk.Label(self, text="© 2023 Christian Tejada. All rights reserved.")
        self.copyrighlabel.pack(pady=10)

        self.description_text = """
        Welcome to the Credit Report Scraper!
        
        This application allows you to upload a credit report in PDF format
        and extract important information from it, such as credit scores. It 
        is developed using some of the techniques I used when working for a
        major credit repair company that did funding also. The purpose was to
        create an internal application that could quickly scan PDF files and
        and let you know their funding worthiness. This is a very simplified 
        version to get you started using some PDF scraping techniques. 

        Disclaimer: Please keep in mind that I am not responsible for how you
        use this script. There are certain moral and legal obligations when
        accessing sensitive data. As always, proceed at your own risk.
        
        Please select a credit report file to upload:
        """

        self.description_box = tk.Text(self, height=4, wrap=tk.WORD)
        self.description_box.insert(tk.END, self.description_text)
        self.description_box.configure(state="disabled")
        self.description_box.pack(pady=10)

        self.continue_button = tk.Button(self, text="Continue", command=self.close_splash)
        self.continue_button.pack(pady=10)

    def close_splash(self):
        self.destroy()
        self.parent.deiconify()  # Show the main window


class App:
    def __init__(self, root):
        self.root = root
        self.root.geometry('720x400')
        self.root.title("Credit Report Scraper")

        self.splash_screen = SplashScreen(root)  # Create an instance of the splash screen

        self.upload_button = tk.Button(root, text="Upload Credit Report", command=self.upload)
        self.upload_button.pack(pady=20)

        self.result_label = tk.Label(root, text="")
        self.result_label.pack(pady=10)

    def upload(self):
        filename = filedialog.askopenfilename(initialdir="/", title="Select File",
                                              filetypes=(("pdf files", "*.pdf"), ("all files", "*.*")))

        if filename:
            self.scrape_pdf(filename)

    # Scrape method used for finding out the scores
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

        self.result_label['text'] = f"Vantage Score: {vantage_score}\n" \
                                     f"Transunion Score: {transunion_score}\n" \
                                     f"Equifax Score: {equifax_score}\n" \
                                     f"Experian Score: {experian_score}\n"

        if vantage_score:
            if int(vantage_score) >= 700 and all(score.isdigit() and int(score) >= 700 for score in
                                                [transunion_score, equifax_score, experian_score]):
                self.result_label['text'] += "This individual is a great candidate for funding."
            else:
                self.result_label['text'] += "This candidate does not fit all criteria. Please manually review."
        else:
            self.result_label['text'] += "Could not find Vantage Score 3.0 in the credit report."

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
