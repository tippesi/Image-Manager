import tkinter as tk
import re
import tkinter.filedialog
import tkinter.simpledialog
import os
import shutil
import random
import PIL.Image as Image

class Application(tk.Frame):
    def __init__(self, master=None):
        self.images = []
        self.matcher = re.compile("^.*\.(png|PNG|jpg|jpeg|JPG|JPEG)$")

        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.infolabel = tk.Label()
        self.infolabel.pack()

        self.file_import = tk.Button(self)
        self.file_import["text"] = "Import Files"
        self.file_import["command"] = self.import_images
        self.file_import.pack()

        self.folder_import = tk.Button(self)
        self.folder_import["text"] = "Import Folder"
        self.folder_import["command"] = self.import_folder
        self.folder_import.pack()

        self.random_export = tk.Button(self)
        self.random_export["text"] = "Export random"
        self.random_export["command"] = self.export_random
        self.random_export.pack()

        self.update_infolabel()

    def import_images(self):
        filenames = tk.filedialog.askopenfilenames()

        if filenames == None:
            return

        for filename in filenames:
            if self.is_image(filename):
                self.images.append(filename)

        self.update_infolabel()

    def import_folder(self):
        folder = tk.filedialog.askdirectory()

        if folder == None:
            return

        files = []
        for (dirpath, _, filenames) in os.walk(folder):
            for filename in filenames:
                files.append(os.path.join(dirpath, filename))

        for filename in files:
            if self.is_image(filename):
                self.images.append(filename)

        self.update_infolabel()

    def export_random(self):
        images = self.images

        num = tk.simpledialog.askinteger("Random Export", "Number of images")

        if num == None:
            return

        if num > len(images):
            num = len(images)

        folder = tk.filedialog.askdirectory()

        if folder == None:
            return

        for i in range(0, num):
            rnd = random.randint(0, len(images) - 1)

            path =  folder + "/" + os.path.basename(images[rnd])

            shutil.copyfile(images[rnd], path)

            self.images.pop(rnd)

    def unload_images(self):
        self.images.clear()
        self.update_infolabel()

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
    root = tk.Tk("Image Manager")
    app = Application(master=root)
    app.mainloop()