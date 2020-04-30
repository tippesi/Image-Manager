import tkinter as tk
import re
import tkinter.filedialog
import tkinter.simpledialog
import os
import shutil
import random
import math
import PIL.Image as PILImage
import PIL.ImageTk as PILImageTk

class Image():
    def __init__(self, filename):
        image = PILImage.open(filename)

        self.filename = filename

        self.generate_thumbnail(image)

    def generate_thumbnail(self, image):
        img = image.copy()
        img.thumbnail((128, 128))

        self.thumbnail = PILImageTk.PhotoImage(img)

class Application(tk.Frame):
    def __init__(self, master=None):
        self.images = []
        self.matcher = re.compile("^.*\.(png|PNG|jpg|jpeg|JPG|JPEG)$")

        super().__init__(master)
        self.grid(sticky='news')

        self.master = master        
        self.create_widgets()

    def create_widgets(self):
        self.infolabel = tk.Label(self)
        self.infolabel.grid(row=0, column=0, sticky="W", pady = 2)

        self.controlframe = tk.Frame(self)
        self.controlframe.grid(row=1, column=0, sticky="W", pady = 2)

        self.file_import = tk.Button(self.controlframe)
        self.file_import["text"] = "Import Files"
        self.file_import["command"] = self.import_images
        self.file_import.grid(row = 1, column = 0, sticky = "W", padx = 2)

        self.folder_import = tk.Button(self.controlframe)
        self.folder_import["text"] = "Import Folder"
        self.folder_import["command"] = self.import_folder
        self.folder_import.grid(row = 1, column = 1, padx = 2)

        self.diashow_export = tk.Button(self.controlframe)
        self.diashow_export["text"] = "Export diashow"
        self.diashow_export["command"] = self.export_diashow
        self.diashow_export.grid(row = 1, column = 2, padx = 2)

        self.images_clear = tk.Button(self.controlframe)
        self.images_clear["text"] = "Clear images"
        self.images_clear["command"] = self.clear_images
        self.images_clear.grid(row = 1, column = 3, padx = 2)

        self.update_imagegrid(5, 9)
        self.update_infolabel()

    def import_images(self):
        filenames = tk.filedialog.askopenfilenames()

        if filenames == None:
            return

        for filename in filenames:
            if self.is_image(filename):
                self.images.append(Image(filename))

        self.update_imagegrid(5, 9)
        self.update_infolabel()

    def import_folder(self):
        folder = tk.filedialog.askdirectory()

        if folder == None:
            return

        files = []
        for (dirpath, _, filenames) in os.walk(folder):
            for filename in filenames:
                files.append(os.path.join(dirpath, filename))

        errors = []

        for filename in files:
            if self.is_image(filename):
                try:
                    img = Image(filename)
                    self.images.append(img)
                except:
                    errors.append(filename)

        if len(errors):
            tk.messagebox.showerror("Error loading", str(len(errors)) +
                " items failed to load")

        self.update_imagegrid(5, 9)
        self.update_infolabel()

    def export_diashow(self):
        images = self.images

        num = tk.simpledialog.askinteger("Random Diashow", "Number of images")

        if num == None:
            return

        if num > len(images):
            num = len(images)

        folder = tk.filedialog.askdirectory()

        if folder == None:
            return

        for i in range(0, num):
            rnd = random.randint(0, len(images) - 1)

            path =  folder + "/" + os.path.basename(images[rnd].filename)

            shutil.copyfile(images[rnd].filename, path)

            self.images.pop(rnd)

    def clear_images(self):
        self.images.clear()

        self.update_imagegrid(5, 9)
        self.update_infolabel()
        
    def update_imagegrid(self, rows, columns):

        self.imagegrid_frame = tk.Frame(self)
        self.imagegrid_frame.grid(row=2, column=0, pady=(5, 0), sticky='nw')
        self.imagegrid_frame.grid_rowconfigure(0, weight=1)
        self.imagegrid_frame.grid_columnconfigure(0, weight=1)
        # Set grid_propagate to False to allow 5-by-5 buttons resizing later
        self.imagegrid_frame.grid_propagate(False)

        # Add a canvas in that frame
        self.imagegrid_canvas = tk.Canvas(self.imagegrid_frame)
        self.imagegrid_canvas.grid(row=0, column=0, sticky="news")

        # Link a scrollbar to the canvas
        self.imagegrid_vsb = tk.Scrollbar(self.imagegrid_frame, orient="vertical", command=self.imagegrid_canvas.yview)
        self.imagegrid_vsb.grid(row=0, column=1, sticky='ns')
        self.imagegrid_canvas.configure(yscrollcommand=self.imagegrid_vsb.set)

        # Create a frame to contain the buttons
        self.imagegrid_frame_buttons = tk.Frame(self.imagegrid_canvas, bg="blue")
        self.imagegrid_canvas.create_window((0, 0), window=self.imagegrid_frame_buttons, anchor='nw')

        totalLabels = len(self.images)

        # Add 9-by-5 buttons to the frame
        self.imagegrid_labels = [tk.Label() for j in range(0, totalLabels)]
        for i in range(0, totalLabels):
            row = int(i / columns)
            column = int(i % columns)
            try:
                self.imagegrid_labels[i] = tk.Label(self.imagegrid_frame_buttons, 
                    image=self.images[i].thumbnail)
            except:
                self.imagegrid_labels[i] = tk.Label(self.imagegrid_frame_buttons, 
                    text="Error")
            self.imagegrid_labels[i].grid(row=row, column=column, sticky='news')

        # Update buttons frames idle tasks to let tkinter calculate buttons sizes
        self.imagegrid_frame_buttons.update_idletasks()

        padding = 5
        width = (128 + padding) * columns
        height = (128 + padding) * rows

        # Resize the canvas frame to show exactly 5-by-5 buttons and the scrollbar
        self.imagegrid_frame.config(width=width + self.imagegrid_vsb.winfo_width(),
                            height=height)

        # Set the canvas scrolling region
        self.imagegrid_canvas.config(scrollregion=self.imagegrid_canvas.bbox("all"))

    def update_infolabel(self):
        text = ""

        if len(self.images) == 0:
            text = "No images loaded"
        else:
            text = str(len(self.images)) + " images loaded"

        self.infolabel["text"] = text

    def is_image(self, filename):
        matches = self.matcher.match(filename)

        if matches != None:
            return True
        return False

if __name__ == "__main__":
    # execute only if run as a script
    root = tk.Tk()
    root.grid_rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)
    root.title("Image Manager")
    app = Application(master=root)
    root.mainloop()