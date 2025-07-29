import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from db_handler import init_db, get_items, add_item, update_item, delete_item, get_expiring_items
from datetime import datetime, timedelta

class ItemApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Non-Inventory Item Timer")
        self.tree = None
        self.build_ui()
        self.refresh_items()
        self.check_expiring()

    def build_ui(self):
        self.tree = ttk.Treeview(self.root, columns=("ID", "Part Number", "Quantity", "Value", "Added", "Days", "Time Left"), show='headings')
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
        self.tree.pack(fill=tk.BOTH, expand=True)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(fill=tk.X)

        tk.Button(btn_frame, text="Add", command=self.add_item).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(btn_frame, text="Modify", command=self.modify_item).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(btn_frame, text="Delete", command=self.delete_item).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(btn_frame, text="Refresh", command=self.refresh_items).pack(side=tk.LEFT, padx=5, pady=5)

    def refresh_items(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for item in get_items():
            added = datetime.fromisoformat(item[4])
            expiry = added + timedelta(days=item[5])
            time_left = (expiry - datetime.now()).days
            self.tree.insert('', tk.END, values=(
                item[0], item[1], item[2], f"${item[3]:.2f}",
                added.date(), item[5], f"{time_left} day(s)"
            ))

    def add_item(self):
        part = simpledialog.askstring("Part Number", "Enter Part Number:")
        qty = simpledialog.askinteger("Quantity", "Enter Quantity:")
        val = simpledialog.askfloat("Value", "Enter Value:")
        days = simpledialog.askinteger("Days", "Enter days (30–90):")
        if None in (part, qty, val, days): return
        if not 1 <= days <= 90:
            messagebox.showerror("Error", "Days must be between 30 and 90")
            return
        add_item(part, qty, val, days)
        self.refresh_items()

    def modify_item(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select Item", "No item selected.")
            return
        item_data = self.tree.item(selected[0])['values']
        item_id = item_data[0]
        part = simpledialog.askstring("Part Number", "Modify Part Number:", initialvalue=item_data[1])
        qty = simpledialog.askinteger("Quantity", "Modify Quantity:", initialvalue=item_data[2])
        val = simpledialog.askfloat("Value", "Modify Value:", initialvalue=float(item_data[3].replace("$", "")))
        days = simpledialog.askinteger("Days", "Modify Days (30–90):", initialvalue=item_data[5])
        if None in (part, qty, val, days): return
        if not 30 <= days <= 90:
            messagebox.showerror("Error", "Days must be between 30 and 90")
            return
        update_item(item_id, part, qty, val, days)
        self.refresh_items()

    def delete_item(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select Item", "No item selected.")
            return
        item_id = self.tree.item(selected[0])['values'][0]
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this item?"):
            delete_item(item_id)
            self.refresh_items()

    def check_expiring(self):
        expiring = get_expiring_items()
        if expiring:
            msg = "⚠️ The following items are expiring soon:\n\n"
            for p, q, v, date, left in expiring:
                msg += f"- {p} (Qty: {q}, Value: ${v}, {left} day(s) left, Expires: {date})\n"
            messagebox.showwarning("Expiring Items", msg)

if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = ItemApp(root)
    root.mainloop()
