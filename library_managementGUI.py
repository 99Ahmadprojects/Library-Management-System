import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import re
import pickle
import os
from PIL import Image, ImageTk
import urllib.request

class LibraryManagementSystem:
    def __init__(self):
        self.load_data()
        # Calculate next_book_id dynamically
        self.next_book_id = self.calculate_next_book_id()
        self.current_user = None

    def calculate_next_book_id(self):
        if not self.books:  # If no books exist, start with ID 1
            return 1
        # Extract numeric part from book IDs and find the maximum
        max_id = max(int(book_id.split('-')[1]) for book_id in self.books.keys())
        return max_id + 1

    def is_valid_email(self, email):
        return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

    def register_user(self, email, password):
        if not self.is_valid_email(email):
            messagebox.showerror("Error", "Invalid email format.")
            return
        if email in self.users:
            messagebox.showerror("Error", "Email is already registered.")
            return
        self.users[email] = {"password": password, "profile": {}}
        self.save_data()
        messagebox.showinfo("Success", f"User registered successfully with email: {email}")

    def login_user(self, email, password):
        if not self.is_valid_email(email):
            messagebox.showerror("Error", "Invalid email format.")
            return False
        if email not in self.users:
            messagebox.showerror("Error", "Email is not registered.")
            return False
        if self.users[email]["password"] == password:
            self.current_user = email
            messagebox.showinfo("Success", "User logged in successfully!")
            return True
        else:
            messagebox.showerror("Error", "Incorrect password.")
            return False

    def add_book(self, title, author, copies, genre):
        if self.current_user != "admin@gmail.com":
            messagebox.showerror("Error", "Only admin can add books.")
            return
        book_id = f"Book-{self.next_book_id}"  # Generate new book ID
        self.books[book_id] = {
            "title": title,
            "author": author,
            "copies": int(copies),
            "genre": genre,
        }
        self.next_book_id += 1  # Increment for the next book
        self.save_data()
        messagebox.showinfo("Success", f"Book {book_id} added successfully!")

    def search_books(self, title, author):
        available_books = []
        for book_id, details in self.books.items():
            if details["title"].lower() == title.lower() or details["author"].lower() == author.lower():
                available_books.append(f"{book_id}: {details}")
        if not available_books:
            return "No books available for this search criteria."
        return "\n".join(available_books)

    def borrow_book(self, book_id, quantity):
        try:
            quantity = int(quantity)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid quantity.")
            return

        if book_id not in self.books:
            messagebox.showerror("Error", "Invalid book ID.")
            return

        available_copies = int(self.books[book_id]["copies"])

        if available_copies < quantity:
            messagebox.showerror("Error", "Not enough copies available.")
            return

        self.books[book_id]["copies"] = available_copies - quantity
        self.borrowings.append({"user_email": self.current_user, "book_id": book_id, "quantity": quantity})
        self.save_data()
        messagebox.showinfo("Success", f"Successfully borrowed {quantity} copies of {book_id}.")

    def return_book(self, book_id, quantity):
        try:
            quantity = int(quantity)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid quantity.")
            return

        for borrowing in self.borrowings:
            if borrowing["user_email"] == self.current_user and borrowing["book_id"] == book_id:
                if borrowing["quantity"] >= quantity:
                    self.books[book_id]["copies"] += quantity
                    borrowing["quantity"] -= quantity
                    if borrowing["quantity"] == 0:
                        self.borrowings.remove(borrowing)
                    self.save_data()
                    messagebox.showinfo("Success", f"Successfully returned {quantity} copies of {book_id}.")
                    return
        messagebox.showerror("Error", "Borrowing record not found or invalid quantity to return.")

    def generate_report(self):
        if self.current_user != "admin@gmail.com":
            messagebox.showerror("Error", "Only admin can generate borrowing reports.")
            return "Access Denied."

        report_lines = []
        for borrowing in self.borrowings:
            book_id = borrowing["book_id"]
            book_details = self.books.get(book_id)
            if book_details:
                title = book_details["title"]
                author = book_details["author"]
                genre = book_details["genre"]
                quantity = borrowing["quantity"]
                borrower = borrowing["user_email"]
                report_lines.append(f"Book ID: {book_id}, Title: {title}, Author: {author}, Genre: {genre}, Quantity Borrowed: {quantity}, Borrower: {borrower}")
        if not report_lines:
            return "No borrowings found."
        return "\n".join(report_lines)

    def save_data(self):
        with open("library_data.pkl", "wb") as file:
            pickle.dump({"users": self.users, "books": self.books, "borrowings": self.borrowings}, file)

    def load_data(self):
        if not os.path.exists("library_data.pkl"):
            self.users = {"admin@gmail.com": {"password": "12345", "profile": {}}}
            self.books = {}
            self.borrowings = []
            return
        try:
            with open("library_data.pkl", "rb") as file:
                data = pickle.load(file)
                self.users = data.get("users", {"admin@gmail.com": {"password": "12345", "profile": {}}})
                self.books = data.get("books", {})
                self.borrowings = data.get("borrowings", [])
        except EOFError:
            self.users = {"admin@gmail.com": {"password": "12345", "profile": {}}}
            self.books = {}
            self.borrowings = []

class LibraryManagementGUI:
    def __init__(self, root, system):
        self.root = root
        self.system = system
        self.root.title("Library Management System")
        self.root.geometry("800x600")
        self.load_background_image()
        self.setup_styles()
        self.main_menu(logged_in=False)
        self.root.bind("<Configure>", self.resize_background)

    def setup_styles(self):
        style = ttk.Style()
        style.configure("Rounded.TFrame", background="#f0f0f0", padding=10)
        style.configure("Large.TButton", font=("Helvetica", 14), padding=(5, 5))

    def load_background_image(self):
        url = "https://img.freepik.com/premium-photo/abstract-blur-library-blurred-book-shelves-hall-generative-ai_791316-6098.jpg?semt=ais_hybrid"
        image_path = "background.jpg"
        if not os.path.exists(image_path):
            try:
                urllib.request.urlretrieve(url, image_path)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load background image: {e}")
                self.bg_image = None
                return
        self.bg_image = Image.open(image_path)

    def resize_background(self, event=None):
        if hasattr(self, 'canvas') and self.canvas.winfo_exists() and self.bg_image:
            width = self.root.winfo_width()
            height = self.root.winfo_height()
            resized_bg = self.bg_image.resize((width, height), Image.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(resized_bg)
            self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")

    def setup_page_with_background(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.canvas = tk.Canvas(self.root, width=self.root.winfo_width(), height=self.root.winfo_height())
        self.canvas.pack(fill="both", expand=True)
        self.resize_background()

    def main_menu(self, logged_in):
        self.setup_page_with_background()
        frame = ttk.Frame(self.root, style="Rounded.TFrame")
        frame.place(relx=0.5, rely=0.5, anchor="center", width=500, height=450)
        ttk.Label(frame, text="Library Management System", font=("Times New Roman", 28)).pack(pady=40)
        if not logged_in:
            ttk.Button(frame, text="Register", command=self.register, style="Large.TButton").pack(pady=30)
            ttk.Button(frame, text="Login", command=self.login, style="Large.TButton").pack(pady=30)
        else:
            ttk.Button(frame, text="Search Books", command=self.search_books, style="Large.TButton").pack(pady=5)
            ttk.Button(frame, text="Borrow Book", command=self.borrow_book, style="Large.TButton").pack(pady=5)
            ttk.Button(frame, text="Return Book", command=self.return_book, style="Large.TButton").pack(pady=5)
            # Show "View Borrowing Report" only to admin
            if self.system.current_user == "admin@gmail.com":
                ttk.Button(frame, text="View Borrowing Report", command=self.view_report, style="Large.TButton").pack(pady=5)
            ttk.Button(frame, text="View All Books", command=self.view_all_books, style="Large.TButton").pack(pady=5)
            if self.system.current_user == "admin@gmail.com":
                ttk.Button(frame, text="Add Book (Admin)", command=self.add_book, style="Large.TButton").pack(pady=5)
            ttk.Button(frame, text="Logout", command=self.logout, style="Large.TButton").pack(pady=20)

    def register(self):
        self.setup_page_with_background()
        frame = ttk.Frame(self.root, width=400, height=350)
        frame.place(relx=0.5, rely=0.5, anchor="center")
        frame.pack_propagate(False)
        ttk.Label(frame, text="Register", font=("Times New Roman", 25)).pack(pady=5)
        ttk.Label(frame, text="Email:").pack(pady=(5, 2))
        email_entry = ttk.Entry(frame)
        email_entry.pack()
        ttk.Label(frame, text="Password:").pack(pady=(5, 2))
        password_entry = ttk.Entry(frame, show="*")
        password_entry.pack()
        show_password_var = tk.BooleanVar()
        show_password_checkbox = ttk.Checkbutton(frame, text="Show Password", variable=show_password_var,
            command=lambda: self.toggle_password_visibility(password_entry, show_password_var))
        show_password_checkbox.pack(pady=5)
        ttk.Button(frame, text="Register", command=lambda: self.register_user_action(email_entry.get(), password_entry.get())).pack(pady=10)
        ttk.Button(frame, text="Back", command=lambda: self.main_menu(logged_in=False)).pack(pady=5)

    def register_user_action(self, email, password):
        self.system.register_user(email, password)
        # After successful registration, go back to main menu
        self.main_menu(logged_in=False)

    def login(self):
        self.setup_page_with_background()
        frame = ttk.Frame(self.root, width=400, height=350)
        frame.place(relx=0.5, rely=0.5, anchor="center")
        frame.pack_propagate(False)
        ttk.Label(frame, text="Login", font=("Times New Roman", 25)).pack(pady=5)
        ttk.Label(frame, text="Email:").pack(pady=(5, 2))
        email_entry = ttk.Entry(frame)
        email_entry.pack()
        ttk.Label(frame, text="Password:").pack(pady=(5, 2))
        password_entry = ttk.Entry(frame, show="*")
        password_entry.pack()

        show_password_var = tk.BooleanVar()
        show_password_checkbox = ttk.Checkbutton(frame, text="Show Password", variable=show_password_var,
            command=lambda: self.toggle_password_visibility(password_entry, show_password_var))
        show_password_checkbox.pack(pady=5)

        ttk.Button(frame, text="Login", command=lambda: self.attempt_login(email_entry.get(), password_entry.get())).pack(pady=10)
        ttk.Button(frame, text="Back", command=lambda: self.main_menu(logged_in=False)).pack(pady=5)

    def attempt_login(self, email, password):
        if self.system.login_user(email, password):
            self.main_menu(logged_in=True)

    def logout(self):
        self.system.current_user = None
        messagebox.showinfo("Logout", "You have been logged out successfully.")
        self.main_menu(logged_in=False)

    def toggle_password_visibility(self, entry, show_var):
        entry.config(show="" if show_var.get() else "*")

    def add_book(self):
        if self.system.current_user != "admin@gmail.com":
            messagebox.showerror("Error", "Only admin can add books.")
            return

        self.setup_page_with_background()
        frame = ttk.Frame(self.root, width=400, height=400)
        frame.place(relx=0.5, rely=0.5, anchor="center")
        frame.pack_propagate(False)
        ttk.Label(frame, text="Add Book", font=("Times New Roman", 25)).pack(pady=5)
        ttk.Label(frame, text="Title:").pack(pady=(5, 2))
        title_entry = ttk.Entry(frame)
        title_entry.pack()
        ttk.Label(frame, text="Author:").pack(pady=(5, 2))
        author_entry = ttk.Entry(frame)
        author_entry.pack()
        ttk.Label(frame, text="Copies:").pack(pady=(5, 2))
        copies_entry = ttk.Entry(frame)
        copies_entry.pack()
        ttk.Label(frame, text="Genre:").pack(pady=(5, 2))
        genre_entry = ttk.Entry(frame)
        genre_entry.pack()
        ttk.Button(frame, text="Add Book", command=lambda: self.add_book_action(title_entry.get(), author_entry.get(), copies_entry.get(), genre_entry.get())).pack(pady=10)
        ttk.Button(frame, text="Back", command=lambda: self.main_menu(logged_in=True)).pack(pady=5)

    def add_book_action(self, title, author, copies, genre):
        self.system.add_book(title, author, copies, genre)
        # After adding a book, go back to main menu
        self.main_menu(logged_in=True)

    def show_search_results(self, title, author):
        results = self.system.search_books(title, author)

        # Create a new Toplevel window to show the search results
        result_window = tk.Toplevel(self.root)
        result_window.title("Search Results")
        result_window.geometry("400x300")

        ttk.Label(result_window, text="Search Results", font=("Times New Roman", 20)).pack(pady=10)

        # Display the results in a Text widget within the Toplevel window
        result_text = tk.Text(result_window, wrap="word", height=10, width=40)
        result_text.pack(pady=10)
        result_text.insert("end", results)
        result_text.config(state="disabled")  # Make the text read-only

        # Add a Close button to the Toplevel window
        ttk.Button(result_window, text="Close", command=result_window.destroy).pack(pady=5)

    def search_books(self):
        self.setup_page_with_background()
        frame = ttk.Frame(self.root, width=400, height=350)
        frame.place(relx=0.5, rely=0.5, anchor="center")
        frame.pack_propagate(False)

        ttk.Label(frame, text="Search Books", font=("Times New Roman", 25)).pack(pady=25)

        ttk.Label(frame, text="Title:").pack(pady=(10, 5))
        title_entry = ttk.Entry(frame)
        title_entry.pack()

        ttk.Label(frame, text="Author:").pack(pady=(10, 5))
        author_entry = ttk.Entry(frame)
        author_entry.pack()

        # Modify the command to call show_search_results without needing a Text widget
        ttk.Button(frame, text="Search",
                   command=lambda: self.show_search_results(title_entry.get(), author_entry.get())).pack(pady=10)
        ttk.Button(frame, text="Back", command=lambda: self.main_menu(logged_in=True)).pack(pady=5)

    def view_all_books(self):
        self.setup_page_with_background()

        # Create a new window to display all books
        all_books_window = tk.Toplevel(self.root)
        all_books_window.title("All Books")
        all_books_window.geometry("500x400")

        # Label for the window
        ttk.Label(all_books_window, text="All Books", font=("Times New Roman", 25)).pack(pady=10)

        # Create a Canvas to hold the Text widget
        canvas = tk.Canvas(all_books_window)
        canvas.pack(side="left", fill="both", expand=True)

        # Create a scrollbar and link it to the Canvas
        scrollbar = ttk.Scrollbar(all_books_window, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")

        canvas.configure(yscrollcommand=scrollbar.set)

        # Create a frame inside the Canvas to hold the Text widget
        frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=frame, anchor="nw")

        # Create a Text widget inside the frame to display book details
        books_text = tk.Text(frame, wrap="word", height=15, width=30)
        books_text.pack(pady=10)

        # Populate the Text widget with book information
        all_books_info = ""
        for book_id, details in self.system.books.items():
            all_books_info += f"Book ID: {book_id}\n"
            all_books_info += f"Title: {details['title']}\n"
            all_books_info += f"Author: {details['author']}\n"
            all_books_info += f"Genre: {details['genre']}\n"
            all_books_info += f"Copies Available: {details['copies']}\n\n"

        books_text.insert("end", all_books_info)
        books_text.config(state="disabled")  # Make the text widget read-only

        # Update the scrollable region after inserting content
        frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

        # Add a Close button
        close_button = ttk.Button(all_books_window, text="Close",
                                  command=lambda: self.close_books_window(all_books_window))
        close_button.pack(pady=5)

    def close_books_window(self, all_books_window):
        all_books_window.destroy()  # Close the 'All Books' window
        self.main_menu(logged_in=True)  # Return to the main menu

    def borrow_book(self):
        self.setup_page_with_background()
        frame = ttk.Frame(self.root, width=400, height=350)
        frame.place(relx=0.5, rely=0.5, anchor="center")
        frame.pack_propagate(False)
        ttk.Label(frame, text="Borrow Book", font=("Times New Roman", 25)).pack(pady=10)
        ttk.Label(frame, text="Book ID:").pack(pady=(10, 5))
        book_id_entry = ttk.Entry(frame)
        book_id_entry.pack()
        ttk.Label(frame, text="Quantity:").pack(pady=(10, 5))
        quantity_entry = ttk.Entry(frame)
        quantity_entry.pack()
        ttk.Button(frame, text="Borrow", command=lambda: self.borrow_book_action(book_id_entry.get(), quantity_entry.get())).pack(pady=10)
        ttk.Button(frame, text="Back", command=lambda: self.main_menu(logged_in=True)).pack(pady=5)

    def borrow_book_action(self, book_id, quantity):
        self.system.borrow_book(book_id, quantity)
        # After borrowing, go back to main menu
        self.main_menu(logged_in=True)

    def return_book(self):
        self.setup_page_with_background()
        frame = ttk.Frame(self.root, width=400, height=350)
        frame.place(relx=0.5, rely=0.5, anchor="center")
        frame.pack_propagate(False)
        ttk.Label(frame, text="Return Book", font=("Times New Roman", 25)).pack(pady=5)
        ttk.Label(frame, text="Book ID:").pack(pady=(5, 2))
        book_id_entry = ttk.Entry(frame)
        book_id_entry.pack()
        ttk.Label(frame, text="Quantity:").pack(pady=(5, 2))
        quantity_entry = ttk.Entry(frame)
        quantity_entry.pack()
        ttk.Button(frame, text="Return", command=lambda: self.return_book_action(book_id_entry.get(), quantity_entry.get())).pack(pady=10)
        ttk.Button(frame, text="Back", command=lambda: self.main_menu(logged_in=True)).pack(pady=5)

    def return_book_action(self, book_id, quantity):
        self.system.return_book(book_id, quantity)
        # After returning, go back to main menu
        self.main_menu(logged_in=True)

    def view_report(self):
        if self.system.current_user != "admin@gmail.com":
            messagebox.showerror("Error", "Only admin can view borrowing reports.")
            return

        self.setup_page_with_background()  # Set up the background and clear old widgets

        # Create a frame for the report screen
        frame = ttk.Frame(self.root, width=650, height=500)
        frame.place(relx=0.5, rely=0.5, anchor="center")
        frame.pack_propagate(False)

        # Label for the report title
        ttk.Label(frame, text="Borrowing Report", font=("Times New Roman", 25)).pack(pady=10)

        # Create a Canvas to hold the Text widget for report
        canvas = tk.Canvas(frame)
        canvas.pack(side="left", fill="both", expand=True)

        # Create a vertical scrollbar for the Canvas
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")

        canvas.configure(yscrollcommand=scrollbar.set)

        # Create a frame inside the Canvas to hold the Text widget
        text_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=text_frame, anchor="nw")

        # Text widget to display the report
        report_text = tk.Text(text_frame, wrap="word", height=20, width=50)
        report_text.pack(pady=5)

        # Get the borrowing report and insert into the Text widget
        borrowings_info = self.system.generate_report()

        report_text.insert("end", borrowings_info)
        report_text.config(state="disabled")  # Make the text read-only

        # Update the scrollable region after inserting content
        text_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

        # Add the Back button to navigate to the main menu
        ttk.Button(frame, text="Back", command=lambda: self.main_menu(logged_in=True)).pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    system = LibraryManagementSystem()
    gui = LibraryManagementGUI(root, system)
    root.mainloop()
