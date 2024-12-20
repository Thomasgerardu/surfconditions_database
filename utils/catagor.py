import os
from tkinter import Tk, Label, Canvas
from PIL import Image, ImageTk
import shutil

class ImageCategorizer:
    def __init__(self, master, image_folder, keep_folder, delete_folder):
        self.master = master
        self.image_folder = image_folder
        self.keep_folder = keep_folder
        self.delete_folder = delete_folder
        self.image_files = [f for f in os.listdir(image_folder) if f.lower().endswith(('png', 'jpg', 'jpeg'))]
        self.current_index = 0

        # Create folders if they don't exist
        if not os.path.exists(keep_folder):
            os.makedirs(keep_folder)
        if not os.path.exists(delete_folder):
            os.makedirs(delete_folder)

        # Set up the canvas and labels
        self.canvas = Canvas(master, width=800, height=600)
        self.canvas.pack()
        self.label = Label(master, text="")
        self.label.pack()

        # Load and display the first image
        self.display_image()

        # Bind arrow keys
        master.bind("<Right>", self.next_image)  # Next image
        master.bind("<Up>", self.keep_image)    # Move to Keep folder
        master.bind("<Down>", self.delete_image)  # Move to Delete folder

    def display_image(self):
        """Display the current image."""
        if self.current_index < len(self.image_files):
            image_path = os.path.join(self.image_folder, self.image_files[self.current_index])
            image = Image.open(image_path)
            image = image.resize((800, 600), Image.Resampling.LANCZOS)
            self.tk_image = ImageTk.PhotoImage(image)
            self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)
            self.label.config(text=f"Image {self.current_index + 1} of {len(self.image_files)}")
        else:
            self.label.config(text="No more images.")
            self.canvas.delete("all")

    def next_image(self, event=None):
        """Move to the next image."""
        print("Right arrow pressed - Skipping to next image")  # Debugging
        if self.current_index < len(self.image_files) - 1:
            self.current_index += 1
            self.display_image()
        else:
            self.label.config(text="No more images.")

    def keep_image(self, event=None):
        """Move the current image to the Keep folder."""
        print("Up arrow pressed - Moving image to Keep folder")  # Debugging
        if self.current_index < len(self.image_files):
            src = os.path.join(self.image_folder, self.image_files[self.current_index])
            dst = os.path.join(self.keep_folder, self.image_files[self.current_index])
            shutil.move(src, dst)
            self.next_image()

    def delete_image(self, event=None):
        """Move the current image to the Delete folder."""
        print("Down arrow pressed - Moving image to Delete folder")  # Debugging
        if self.current_index < len(self.image_files):
            src = os.path.join(self.image_folder, self.image_files[self.current_index])
            dst = os.path.join(self.delete_folder, self.image_files[self.current_index])
            shutil.move(src, dst)
            self.next_image()

if __name__ == "__main__":
    root = Tk()
    root.title("Image Categorizer")

    # Hardcoded folder paths
    image_folder = r"C:\Github\surfconditions_database\pics_with_surfers"
    # image_folder = r"C:\Github\surfconditions_database\heartbeach_good"
    # image_folder = r"C:\Github\surfconditions_database\data_aloha"
    keep_folder = os.path.join(image_folder, "Keep")
    delete_folder = os.path.join(image_folder, "Delete")

    app = ImageCategorizer(root, image_folder, keep_folder, delete_folder)
    root.mainloop()