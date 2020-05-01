import tkinter as tk
import tkinter.ttk as ttk
import re
import tkinter.filedialog
import tkinter.simpledialog
import os
import shutil
import random
import math
import PIL.Image as PILImage
import PIL.ImageTk as PILImageTk
from PIL.ExifTags import TAGS

class Image():
    def __init__(self, filename):
        image = PILImage.open(filename)

        self.exif_data = {}
        info = image._getexif()

        if info:
            for tag, value in info.items():
                decoded = TAGS.get(tag)
                self.exif_data[decoded] = value

            self.dateString = self.exif_data["DateTimeOriginal"]
            self.manufacturer = self.exif_data["Make"]
            self.model = self.exif_data["Model"]

        self.filename = filename

        self.generate_thumbnail(image)

    def __lt__(self, other):
        return self.dateString < other.dateString

    def generate_thumbnail(self, image):
        img = image.copy()
        img.thumbnail((128, 128))

        self.thumbnail = PILImageTk.PhotoImage(img)

    def load(self):
        img = PILImage.open(self.filename)
        img.thumbnail((840, 840))
        self.image = PILImageTk.PhotoImage(img)

class ProgressBar(tk.Toplevel):
    def __init__(self, parent, title=None):
        super().__init__(parent)

        self.body(parent)
        self.transient(parent)

        self.protocol("WM_DELETE_WINDOW", lambda: None)
        self.title(title)

    def body(self, master):
        self.label = ttk.Label(self, text="Importing files")
        self.label.grid(row=0, column=0)
        self.progress = ttk.Progressbar(self, orient="horizontal",
            mode="determinate", length=200)
        self.progress.grid(row=1, column=0)

        self.set_maximum(100)
        self.update(0)

        self.update_idletasks()

    def set_maximum(self, maximum):
        self.progress["maximum"] = maximum

    def update(self, progress, text="Importing files"):
        self.label["text"] = text
        self.progress["value"] = progress
        self.progress.update()

class Application(ttk.Frame):
    def __init__(self, master=None):
        self.images = []
        self.matcher = re.compile("^.*\.(jpg|jpeg|JPG|JPEG)$")

        self.gridColumns = 9
        self.gridRows = 5

        super().__init__(master)
        self.grid(sticky='news')

        self.master = master        
        self.create_widgets()

    def create_widgets(self):
        self.infolabel = ttk.Label(self)
        self.infolabel.grid(row=0, column=0, sticky="W", pady = 2)

        self.controlframe = ttk.Frame(self)
        self.controlframe.grid(row=1, column=0, sticky="W", pady = 2)

        self.file_import = ttk.Button(self.controlframe)
        self.file_import["text"] = "Import Files"
        self.file_import["command"] = self.import_images
        self.file_import.grid(row = 1, column = 0, sticky = "W", padx = 2)

        self.folder_import = ttk.Button(self.controlframe)
        self.folder_import["text"] = "Import Folder"
        self.folder_import["command"] = self.import_folder
        self.folder_import.grid(row = 1, column = 1, padx = 2)

        self.diashow_export = ttk.Button(self.controlframe)
        self.diashow_export["text"] = "Export diashow"
        self.diashow_export["command"] = self.export_diashow
        self.diashow_export.grid(row = 1, column = 2, padx = 2)

        self.images_clear = ttk.Button(self.controlframe)
        self.images_clear["text"] = "Clear images"
        self.images_clear["command"] = self.clear_images
        self.images_clear.grid(row = 1, column = 3, padx = 2)

        self.imagegrid_frame = ttk.Frame(self)

        self.update_imagegrid()
        self.update_infolabel()

    def import_images(self):
        filenames = tk.filedialog.askopenfilenames()

        if filenames == None:
            return

        errors = []

        progress = ProgressBar(self, title="Importing files")

        count = 0

        for filename in filenames:
            if self.is_image(filename):
                try:
                    img = Image(filename)
                    self.images.append(img)
                except:
                    errors.append(filename)                   

                count += 1
                progress.update(count, "Importing file " + str(count)
                    + " of " + str(len(filenames)))

        progress.destroy()

        if len(errors):
            tk.messagebox.showerror("Error loading", str(len(errors)) +
                " items failed to load")

        self.update_imagegrid()
        self.update_infolabel()

    def import_folder(self):
        folder = tk.filedialog.askdirectory()

        if folder == None:
            return

        progress = ProgressBar(self, title="Importing files")

        count = 0

        files = []
        for (dirpath, _, filenames) in os.walk(folder):
            for filename in filenames:
                if self.is_image(filename):
                    files.append(os.path.join(dirpath, filename))
                    count += 1
                    progress.update(0, "Found " + str(count) + " files")


        errors = []

        progress.set_maximum(len(files))

        count = 0

        for filename in files:            
            try:
                img = Image(filename)
                self.images.append(img)
            except:
                errors.append(filename)

            count += 1
            progress.update(count, "Importing file " + str(count)
                + " of " + str(len(files)))

        progress.destroy()

        if len(errors):
            tk.messagebox.showerror("Error loading", str(len(errors)) +
                " items failed to load")

        self.update_imagegrid()
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

        self.update_imagegrid()
        self.update_infolabel()
        
    def update_imagegrid(self):
        self.images.sort()

        self.imagegrid_frame.destroy()

        self.imagegrid_frame = ttk.Frame(self)
        self.imagegrid_frame.grid(row=2, column=0, pady=(5, 0), sticky='nw')
        self.imagegrid_frame.grid_rowconfigure(0, weight=1)
        self.imagegrid_frame.grid_columnconfigure(0, weight=1)
        # Set grid_propagate to False to allow 5-by-5 buttons resizing later
        self.imagegrid_frame.grid_propagate(False)

        # Add a canvas in that frame
        self.imagegrid_canvas = tk.Canvas(self.imagegrid_frame)
        self.imagegrid_canvas.grid(row=0, column=0, sticky="news")

        # Link a scrollbar to the canvas
        self.imagegrid_vsb = ttk.Scrollbar(self.imagegrid_frame, orient="vertical", command=self.imagegrid_canvas.yview)
        self.imagegrid_vsb.grid(row=0, column=1, sticky='ns')
        self.imagegrid_canvas.configure(yscrollcommand=self.imagegrid_vsb.set)

        # Create a frame to contain the buttons
        self.imagegrid_frame_buttons = ttk.Frame(self.imagegrid_canvas)
        self.imagegrid_canvas.create_window((0, 0), window=self.imagegrid_frame_buttons, anchor='nw')

        totalLabels = len(self.images)

        # Add 9-by-5 buttons to the frame
        self.imagegrid_labels = [ttk.Label() for j in range(0, totalLabels)]
        for i in range(0, totalLabels):
            row = int(i / self.gridColumns)
            column = int(i % self.gridColumns)
            try:
                self.imagegrid_labels[i] = ttk.Label(self.imagegrid_frame_buttons, 
                    image=self.images[i].thumbnail)
            except:
                self.imagegrid_labels[i] = ttk.Label(self.imagegrid_frame_buttons, 
                    text="Error")
            self.imagegrid_labels[i].grid(row=row, column=column, sticky='news', padx=2, pady=2)
            self.imagegrid_labels[i].bind("<Button-1>", lambda x, i=i: self.image_label_clicked(i))

        # Update buttons frames idle tasks to let tkinter calculate buttons sizes
        self.imagegrid_frame_buttons.update_idletasks()

        padding = 2*4
        width = (128 + padding) * self.gridColumns
        height = (128 + padding) * self.gridRows

        # Resize the canvas frame to show exactly 5-by-5 buttons and the scrollbar
        self.imagegrid_frame.config(width=width + self.imagegrid_vsb.winfo_width(),
                            height=height)

        # Set the canvas scrolling region
        self.imagegrid_canvas.config(scrollregion=self.imagegrid_canvas.bbox("all"))

    def image_label_clicked(self, index):
        self.imageIndex = index
        self.show_image()

    def update_infolabel(self):
        text = ""

        if len(self.images) == 0:
            text = "No images loaded"
        else:
            text = str(len(self.images)) + " images loaded"

        self.infolabel["text"] = text

    def show_image(self):
        self.imagegrid_frame.grid_remove()

        self.images[self.imageIndex].load()
        self.image_label = ttk.Label(self, image=self.images[self.imageIndex].image)
        self.image_label.grid(row=3, column=0, pady=(5, 0), sticky='nw')

        self.image_close = ttk.Button(self, text="Close", command=self.close_image)
        self.image_close.grid(row=4, column=1, pady=(5, 0), sticky='nw')

        self.image_info_label = ttk.Label(self, text="Image " + str(self.imageIndex) + 
            " of " + str(len(self.images)) + "\nDevice " + self.images[self.imageIndex].manufacturer +
            " " + self.images[self.imageIndex].model)
        self.image_info_label.grid(row=3, column=1, sticky="W", pady = 2)

    def close_image(self):
        self.image_label.destroy()
        self.image_close.destroy()
        self.image_info_label.destroy()

        self.imagegrid_frame.grid()

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