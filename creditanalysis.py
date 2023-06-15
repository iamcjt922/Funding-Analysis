from PIL import Image, ImageTk, ImageDraw
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

        # You can change this to have your own company logo or logo file, by default mine is.
        # It isn't necessary but it would be greatly appreciated if you keep the credits :)
        logo_image = Image.open("images/logo.png")
        logo_image = logo_image.resize((128, 128), Image.ANTIALIAS)

        # This just creates a circular mask for the logo, you can change it.
        mask = Image.new("L", (128, 128), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, 128, 128), fill=255)

        # Applies the mask
        logo_image = Image.composite(logo_image, Image.new("RGBA", (128, 128)), mask)
        self.logo_image = ImageTk.PhotoImage(logo_image)

        self.logo_label = tk.Label(self, image=self.logo_image)
        self.logo_label.pack(pady=20)

        self.copyrighlabel = tk.Label(self, text="© 2023 Christian Tejada. All rights reserved.")
        self.copyrighlabel.pack(pady=10)

        self.continue_button = tk.Button(self, text="Continue", command=self.close_splash)
        self.continue_button.pack(pady=10)

    def close_splash(self):
        self.destroy()
        self.parent.deiconify()  # Show the main window

#Defines the class of the app
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

#scrape method used for finding out the scores
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
            if int(vantage_score) >= 700 and all(score.isdigit() and int(score) >= 700 for score in [transunion_score, equifax_score, experian_score]):
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
