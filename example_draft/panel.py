import tkinter as tk
from tkinter import ttk
import requests
import threading

API_URL = 'http://localhost:8000'
REFRESH_INTERVAL = 1000  # Refresh every 1000ms (1s)


class ProductionPanel(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Production Panel")
        self.geometry("600x400")
        self.configure(bg='black')

        self.label_title = tk.Label(self, text="Production Orders", font=("Arial", 24, "bold"), fg="white", bg="black")
        self.label_title.pack(pady=10)

        self.table_frame = tk.Frame(self, bg="black")
        self.table_frame.pack(expand=True, fill="both", padx=20, pady=10)

        self.tree = None
        self.create_table()

        self.update_data()

    def create_table(self):
        """Creates a new table inside table_frame."""
        if self.tree:
            self.tree.destroy()

        self.tree = ttk.Treeview(self.table_frame, columns=("Order ID", "State", "Ready / Ordered"), show="headings",
                                 height=10)
        self.tree.heading("Order ID", text="Order ID")
        self.tree.heading("State", text="State")
        self.tree.heading("Ready / Ordered", text="Ready / Ordered")
        self.tree.pack(expand=True, fill="both")

    def update_data(self):
        threading.Thread(target=self.fetch_orders, daemon=True).start()
        self.after(REFRESH_INTERVAL, self.update_data)

    def fetch_orders(self):
        try:
            response = requests.get(f"{API_URL}/orders")
            if response.status_code == 200:
                orders = response.json()
                orders.sort(key=lambda x: x['timestamp'], reverse=True)

                for order in orders:
                    order["ready_count"], order["ordered_count"] = self.fetch_product_counts(order["id"])

                self.after(0, lambda: self.switch_table(orders))
        except requests.RequestException:
            pass

    def fetch_product_counts(self, order_id):
        try:
            response = requests.get(f"{API_URL}/orders/{order_id}/products")
            if response.status_code == 200:
                products = response.json()
                ready_count = sum(1 for p in products if p['state'] == "READY")
                ordered_count = sum(1 for p in products if p['state'] == "ORDERED")
                return ready_count, ordered_count
        except requests.RequestException:
            pass
        return 0, 0

    def switch_table(self, orders):
        """Creates a new table in the background and switches it in one step."""
        new_frame = tk.Frame(self, bg="black")
        new_tree = ttk.Treeview(new_frame, columns=("Order ID", "State", "Ready / Ordered"), show="headings", height=10)
        new_tree.heading("Order ID", text="Order ID")
        new_tree.heading("State", text="State")
        new_tree.heading("Ready / Ordered", text="Ready / Ordered")
        new_tree.pack(expand=True, fill="both")

        for order in orders:
            color = "green" if order["state"] == "IN_PROGRESS" else "red"
            new_tree.insert("", "end",
                            values=(order["id"], order["state"], f"{order['ready_count']} / {order['ordered_count'] + order['ready_count']}"),
                            tags=(color,))

        new_tree.tag_configure("green", background="green", foreground="white")
        new_tree.tag_configure("red", background="red", foreground="white")

        # Swap the table frames smoothly
        self.table_frame.destroy()
        self.table_frame = new_frame
        self.table_frame.pack(expand=True, fill="both", padx=20, pady=10)
        self.tree = new_tree


if __name__ == "__main__":
    app = ProductionPanel()
    app.mainloop()
