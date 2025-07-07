import tkinter as tk
from tkinter import messagebox
import sqlite3
import functools
import random
from collections import Counter

class CafeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Lavender & Lattes - Online Cafe Ordering")
        self.root.geometry("1100x600")

        # Gradient canvas
        self.canvas = tk.Canvas(self.root, width=1100, height=600)
        self.canvas.pack(fill="both", expand=True)
        self.draw_gradient(self.canvas, "#D8B2D1", "#B57EDC")

        # Overlay frame with transparent background
        self.frame = tk.Frame(self.root, bg="#D8B2D1")
        self.frame.place(relwidth=1, relheight=1)

        self.cart = []
        self.conn = sqlite3.connect("cafe_menu.db")
        self.create_tables()
        self.load_categories()
        self.seed_items()

        self.create_widgets()

    def draw_gradient(self, canvas, color1, color2):
        r1, g1, b1 = self.root.winfo_rgb(color1)
        r2, g2, b2 = self.root.winfo_rgb(color2)
        r_ratio = (r2 - r1) / 600
        g_ratio = (g2 - g1) / 600
        b_ratio = (b2 - b1) / 600

        for i in range(600):
            nr = int(r1 + (r_ratio * i))
            ng = int(g1 + (g_ratio * i))
            nb = int(b1 + (b_ratio * i))
            hex_color = f'#{nr//256:02x}{ng//256:02x}{nb//256:02x}'
            canvas.create_line(0, i, 1100, i, fill=hex_color)

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                category_id INTEGER,
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
        """)
        self.conn.commit()

    def load_categories(self):
        cursor = self.conn.cursor()
        self.category_display = {
            'Coffees': '☕ Coffees',
            'Pastries': '🥐 Pastries',
            'Beverages': '🍹 Beverages',
            'Sandwiches & Wraps': '🥪 Sandwiches & Wraps',
            'Salads': '🥗 Salads',
        }
        for category in self.category_display:
            cursor.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (category,))
        self.conn.commit()
        cursor.execute("SELECT id, name FROM categories")
        self.categories = cursor.fetchall()
        self.category_map = {name: cat_id for cat_id, name in self.categories}

    def seed_items(self):
        cursor = self.conn.cursor()
        items_to_add = [
            ("Espresso", 120.0, "Coffees"),
            ("Latte", 150.0, "Coffees"),
            ("Cappuccino", 160.0, "Coffees"),
            ("Mocha", 170.0, "Coffees"),
            ("Americano", 130.0, "Coffees"),
            ("Flat White", 160.0, "Coffees"),
            ("Macchiato", 140.0, "Coffees"),
            ("Cold Brew", 180.0, "Coffees"),
            ("Iced Tea", 80.0, "Beverages"),
            ("Lemonade", 75.0, "Beverages"),
            ("Fruit Punch", 95.0, "Beverages"),
            ("Mango Smoothie", 120.0, "Beverages"),
            ("Strawberry Milkshake", 130.0, "Beverages"),
            ("Cold Coffee", 140.0, "Beverages"),
            ("Hot Chocolate", 150.0, "Beverages"),
            ("Croissant", 90.0, "Pastries"),
            ("Blueberry Muffin", 110.0, "Pastries"),
            ("Chocolate Danish", 120.0, "Pastries"),
            ("Cinnamon Roll", 100.0, "Pastries"),
            ("Apple Turnover", 110.0, "Pastries"),
            ("Chicken Wrap", 180.0, "Sandwiches & Wraps"),
            ("Veg Wrap", 150.0, "Sandwiches & Wraps"),
            ("Greek Salad", 140.0, "Salads"),
            ("Caesar Salad", 160.0, "Salads"),
        ]
        for name, price, cat_name in items_to_add:
            cat_id = self.category_map.get(cat_name)
            if cat_id:
                cursor.execute("INSERT OR IGNORE INTO items (name, price, category_id) VALUES (?, ?, ?)",
                               (name, price, cat_id))
        self.conn.commit()

    def create_widgets(self):
        self.app_title = tk.Label(self.frame, text="Lavender & Lattes",
                                  font=("Georgia", 28, "bold"), bg="#D8B2D1", fg="black")
        self.app_title.pack(pady=10)

        self.slogan = tk.Label(self.frame, text="Sip ☕ • Relax 🏋 • Enjoy 🍰",
                               font=("Arial", 16, "italic"), bg="#D8B2D1", fg="black")
        self.slogan.pack()

        self.category_frame = tk.Frame(self.frame, bg="#D8B2D1")
        self.category_frame.pack(pady=10)

        added = set()
        for cat_id, name in self.categories:
            if name in added:
                continue
            added.add(name)
            display_name = self.category_display.get(name, name)
            btn = tk.Button(self.category_frame, text=display_name, font=("Arial", 14, "bold"),
                            bg="#fef6ff", fg="black", bd=2, relief=tk.RAISED,
                            command=functools.partial(self.show_menu_items, cat_id))
            btn.pack(side=tk.LEFT, padx=8, pady=5)

        self.menu_display = tk.Text(self.frame, height=20, width=60, font=("Arial", 12), fg="black", bg="white")
        self.menu_display.tag_configure("bold_black", font=("Arial", 14, "bold"), foreground="black")
        self.menu_display.pack(side=tk.LEFT, padx=20, pady=10)

        self.cart_frame = tk.Frame(self.frame, bg="#fdf3e7", bd=2, relief=tk.RIDGE)
        self.cart_frame.pack(side=tk.RIGHT, fill="y", padx=20, pady=10)

        self.cart_label = tk.Label(self.cart_frame, text="🛒 Your Cart", font=("Arial", 14, "bold"), bg="#fdf3e7", fg="black")
        self.cart_label.pack(pady=5)

        self.cart_listbox = tk.Listbox(self.cart_frame, width=35, height=15, font=("Arial", 12), fg="black")
        self.cart_listbox.pack(pady=5)

        self.total_label = tk.Label(self.cart_frame, text="Total: ₹0.00", font=("Arial", 14, "bold"), bg="#fdf3e7", fg="black")
        self.total_label.pack(pady=5)

        self.checkout_button = tk.Button(self.cart_frame, text="Checkout 💳", font=("Arial", 14, "bold"),
                                         bg="#b2f7ef", fg="black", command=self.checkout)
        self.checkout_button.pack(pady=10)

    def show_menu_items(self, category_id):
        self.menu_display.delete(1.0, tk.END)
        cursor = self.conn.cursor()
        cursor.execute("SELECT name, price FROM items WHERE category_id=?", (category_id,))
        items = cursor.fetchall()

        for name, price in items:
            self.menu_display.insert(tk.END, f"{name} - ₹{price:.2f}\n", "bold_black")
            add_btn = tk.Button(self.menu_display, text="Add", font=("Arial", 10, "bold"),
                                command=functools.partial(self.add_to_cart, name, price))
            self.menu_display.window_create(tk.END, window=add_btn)
            self.menu_display.insert(tk.END, "\n\n")

    def add_to_cart(self, name, price):
        self.cart.append((name, price))
        self.cart_listbox.insert(tk.END, f"{name} - ₹{price:.2f}")
        total = sum(item[1] for item in self.cart)
        self.total_label.config(text=f"Total: ₹{total:.2f}")

    def checkout(self):
        if not self.cart:
            messagebox.showinfo("Cart Empty", "Please add items to your cart before checking out!")
            return

        item_counts = Counter([item[0] for item in self.cart])
        checkout_win = tk.Toplevel(self.root)
        checkout_win.title("Order Summary - Lavender & Lattes")
        checkout_win.geometry("450x500")
        checkout_win.configure(bg="#fff0f5")

        title = tk.Label(checkout_win, text="📟 Order Summary", font=("Arial", 16, "bold"), bg="#fff0f5", fg="black")
        title.pack(pady=10)

        summary_frame = tk.Frame(checkout_win, bg="#fff0f5")
        summary_frame.pack(pady=10)

        headers = tk.Label(summary_frame, text=f"{'Item':<20}{'Qty':<5}{'Price':>8}", font=("Arial", 12, "underline"), bg="#fff0f5", anchor="w", justify="left", fg="black")
        headers.pack(anchor="w")

        total = 0
        for name, count in item_counts.items():
            price = next(item[1] for item in self.cart if item[0] == name)
            line_total = price * count
            total += line_total
            item_summary = tk.Label(summary_frame, text=f"{name:<20}{count:<5}₹{line_total:.2f}", font=("Arial", 12), bg="#fff0f5", anchor="w", fg="black")
            item_summary.pack(anchor="w")

        total_label = tk.Label(checkout_win, text=f"Total: ₹{total:.2f}", font=("Arial", 14, "bold"), bg="#fff0f5", fg="black")
        total_label.pack(pady=20)

        quotes = [
            "Thanks a latte for your order! ☕",
            "You made our day brew-tiful! 🌸",
            "Your taste is as classy as your order! ✨",
            "Come back for more magic in a cup! 💫",
            "Hope your day is as sweet as our pastries! 🥐",
        ]
        quote = random.choice(quotes)

        thank_you = tk.Label(checkout_win, text=quote, font=("Arial", 12, "italic"), bg="#fff0f5", fg="black", wraplength=400)
        thank_you.pack(pady=15)

        done_button = tk.Button(checkout_win, text="Close", font=("Arial", 12, "bold"), bg="#dcd6f7", fg="black", command=checkout_win.destroy)
        done_button.pack(pady=10)

        self.cart.clear()
        self.cart_listbox.delete(0, tk.END)
        self.total_label.config(text="Total: ₹0.00")

if __name__ == "__main__":
    root = tk.Tk()
    app = CafeApp(root)
    root.mainloop()
