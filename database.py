import tkinter as tk
from tkinter import ttk
import sqlite3
from tkinter import messagebox
import json
from datetime import datetime


class DatabaseViewer:
    def __init__(self, master):
        self.master = master
        self.master.title("Grocery Store Database Viewer")
        self.master.geometry("1600x900")

        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()

        # Create notebook (tabs)
        self.notebook = ttk.Notebook(master)
        self.notebook.pack(fill='both', expand=True)

        # Create frames for each table
        self.create_users_tab()
        self.create_products_tab()
        self.create_orders_tab()
        self.create_contact_tab()  # ← New tab for contact_messages

        # Load initial data
        self.load_data()

    def configure_styles(self):
        self.style.configure('Treeview.Heading', font=('Helvetica', 11, 'bold'),
                             background='#4a7a8c', foreground='white')
        self.style.configure('Treeview', font=('Helvetica', 10), rowheight=28)
        self.style.map('Treeview.Heading', background=[('active', '#366477')])
        self.style.configure('TNotebook.Tab', font=('Helvetica', 11, 'bold'), padding=[20, 5])
        self.style.configure('Detail.TFrame', background='#f0f4f7')
        self.style.configure('Detail.TLabel', font=('Helvetica', 10), background='#f0f4f7')

    def create_users_tab(self):
        self.users_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.users_frame, text="👥 Users")

        # Treeview with horizontal scroll
        container = ttk.Frame(self.users_frame)
        container.pack(fill='both', expand=True)

        self.users_tree = ttk.Treeview(
            container,
            columns=('ID', 'Name', 'Email', 'Password'),
            show='headings'
        )
        headings = [
            ('ID', 50),
            ('Name', 150),
            ('Email', 250),
            ('Password', 200)
        ]

        for heading, width in headings:
            self.users_tree.heading(heading, text=heading)
            self.users_tree.column(
                heading,
                width=width,
                anchor='center' if heading == 'ID' else 'w'
            )

        # Add both scrollbars
        vsb = ttk.Scrollbar(container, orient="vertical", command=self.users_tree.yview)
        hsb = ttk.Scrollbar(container, orient="horizontal", command=self.users_tree.xview)
        self.users_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Layout
        self.users_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Mask passwords
        self.users_tree.tag_configure('masked', font=('Helvetica', 10), foreground='#666666')
        self.users_tree.bind('<ButtonRelease-1>', self.mask_passwords)

    def mask_passwords(self, event):
        for item in self.users_tree.get_children():
            values = list(self.users_tree.item(item, 'values'))
            if len(values) > 3 and values[3] != '********':
                values[3] = '********'
                self.users_tree.item(item, values=values, tags=('masked',))

    def create_products_tab(self):
        self.products_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.products_frame, text="🛒 Products")

        container = ttk.Frame(self.products_frame)
        container.pack(fill='both', expand=True)

        self.products_tree = ttk.Treeview(
            container,
            columns=('ID', 'Name', 'Price', 'Category', 'Image'),
            show='headings'
        )
        headings = [
            ('ID', 50),
            ('Name', 200),
            ('Price', 100),
            ('Category', 150),
            ('Image', 400)
        ]

        for heading, width in headings:
            self.products_tree.heading(heading, text=heading)
            self.products_tree.column(
                heading,
                width=width,
                anchor='center' if heading in ('ID', 'Price') else 'w'
            )

        vsb = ttk.Scrollbar(container, orient="vertical", command=self.products_tree.yview)
        hsb = ttk.Scrollbar(container, orient="horizontal", command=self.products_tree.xview)
        self.products_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.products_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

    def create_orders_tab(self):
        self.orders_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.orders_frame, text="📦 Orders")

        # Create paned window for split view
        self.orders_paned = ttk.PanedWindow(self.orders_frame, orient=tk.VERTICAL)
        self.orders_paned.pack(fill='both', expand=True)

        # Orders Treeview (top section)
        container = ttk.Frame(self.orders_paned)
        self.orders_tree = ttk.Treeview(
            container,
            columns=('ID', 'User ID', 'Customer', 'Phone', 'Total',
                     'Date', 'Product Count'),
            show='headings'
        )
        headings = [
            ('ID', 60),
            ('User ID', 90),
            ('Customer', 180),
            ('Phone', 130),
            ('Total', 120),
            ('Date', 160),
            ('Product Count', 120)
        ]

        for heading, width in headings:
            self.orders_tree.heading(heading, text=heading)
            self.orders_tree.column(
                heading,
                width=width,
                anchor='center' if heading in ('ID', 'User ID', 'Total', 'Product Count') else 'w'
            )

        vsb = ttk.Scrollbar(container, orient="vertical", command=self.orders_tree.yview)
        hsb = ttk.Scrollbar(container, orient="horizontal", command=self.orders_tree.xview)
        self.orders_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.orders_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Order Details Frame (bottom section)
        self.details_frame = ttk.Frame(self.orders_paned, style='Detail.TFrame')
        self.details_label = ttk.Label(
            self.details_frame,
            text="Order Details",
            style='Detail.TLabel',
            font=('Helvetica', 12, 'bold')
        )
        self.details_label.pack(pady=5, anchor='w')

        # Product display area with formatted text and scrollbar
        text_container = ttk.Frame(self.details_frame)
        text_container.pack(fill='both', expand=True, padx=10, pady=(0, 10))

        self.details_text = tk.Text(
            text_container,
            wrap=tk.WORD,
            font=('Helvetica', 10),
            padx=10,
            pady=10,
            bg='#ffffff',
            borderwidth=1,
            relief='solid'
        )
        vsb_text = ttk.Scrollbar(text_container, command=self.details_text.yview)
        self.details_text.configure(yscrollcommand=vsb_text.set)

        self.details_text.grid(row=0, column=0, sticky='nsew')
        vsb_text.grid(row=0, column=1, sticky='ns')
        text_container.grid_rowconfigure(0, weight=1)
        text_container.grid_columnconfigure(0, weight=1)

        self.details_text.tag_configure('product', font=('Helvetica', 10, 'bold'), foreground='#2c3e50')
        self.details_text.tag_configure('quantity', font=('Courier New', 9), foreground='#7f8c8d')

        # Add panes to the paned window
        self.orders_paned.add(container, weight=3)
        self.orders_paned.add(self.details_frame, weight=2)

        # Bind selection event
        self.orders_tree.bind('<<TreeviewSelect>>', self.show_order_details)

    def create_contact_tab(self):
        self.contact_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.contact_frame, text="✉️ Contact Messages")

        container = ttk.Frame(self.contact_frame)
        container.pack(fill='both', expand=True)

        # Create Treeview for contact_messages
        self.contacts_tree = ttk.Treeview(
            container,
            columns=(
                'ID', 'User ID', 'Name', 'Email', 'Phone',
                'Subject', 'Message', 'Timestamp'
            ),
            show='headings'
        )
        headings = [
            ('ID', 50),
            ('User ID', 80),
            ('Name', 150),
            ('Email', 200),
            ('Phone', 120),
            ('Subject', 200),
            ('Message', 400),
            ('Timestamp', 160)
        ]

        for heading, width in headings:
            self.contacts_tree.heading(heading, text=heading)
            self.contacts_tree.column(
                heading,
                width=width,
                anchor='center' if heading in ('ID', 'User ID') else 'w'
            )

        # Add scrollbars
        vsb = ttk.Scrollbar(container, orient="vertical", command=self.contacts_tree.yview)
        hsb = ttk.Scrollbar(container, orient="horizontal", command=self.contacts_tree.xview)
        self.contacts_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Layout
        self.contacts_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

    def show_order_details(self, event):
        self.details_text.delete(1.0, tk.END)
        selected_item = self.orders_tree.selection()
        if not selected_item:
            return

        order_id = self.orders_tree.item(selected_item[0], 'values')[0]
        conn = sqlite3.connect('product_users.db')
        order = conn.execute(
            '''SELECT products_ordered FROM orders WHERE order_id = ?''',
            (order_id,)
        ).fetchone()
        conn.close()

        if order:
            try:
                products = json.loads(order[0])
                self.details_text.insert(tk.END, "🛍️ Products Ordered:\n\n", 'product')
                for idx, product in enumerate(products, 1):
                    self.details_text.insert(tk.END, f"{idx}. ", 'quantity')
                    self.details_text.insert(tk.END, f"{product['name']}\n", 'product')
                    self.details_text.insert(
                        tk.END,
                        f"   Quantity: {product.get('quantity', 1)}",
                        'quantity'
                    )
                    if 'price' in product:
                        price = f"₹{product['price']:.2f}"
                        self.details_text.insert(tk.END, f"   Price: {price} each", 'quantity')
                    self.details_text.insert(tk.END, "\n")
            except json.JSONDecodeError:
                self.details_text.insert(tk.END, "⚠️ Error decoding product data", 'product')

    def load_data(self):
        try:
            conn = sqlite3.connect('product_users.db')

            # Load users
            users = conn.execute(
                'SELECT id, name, email, password FROM users'
            ).fetchall()
            for user in users:
                masked_user = list(user)
                masked_user[3] = '********'  # Mask password
                self.users_tree.insert('', 'end', values=masked_user, tags=('masked',))

            # Load products
            products = conn.execute(
                'SELECT product_id, name, price, category, image_path FROM products'
            ).fetchall()
            for product in products:
                formatted_product = list(product)
                formatted_product[2] = f"₹{formatted_product[2]:.2f}"  # Format price
                self.products_tree.insert('', 'end', values=formatted_product)

            # Load orders with product counts
            orders = conn.execute(
                '''
                SELECT order_id, user_id, full_name, phone_number, 
                       total_amount, order_date, products_ordered 
                FROM orders
                '''
            ).fetchall()
            for order in orders:
                formatted_order = list(order)
                # Format total amount
                formatted_order[4] = f"₹{formatted_order[4]:.2f}"
                # Format date
                try:
                    date_obj = datetime.strptime(formatted_order[5], '%Y-%m-%d %H:%M:%S')
                    formatted_order[5] = date_obj.strftime('%d %b %Y %I:%M %p')
                except:
                    pass
                # Calculate product count
                try:
                    products_list = json.loads(formatted_order[6])
                    product_count = f"{len(products_list)} items"
                except json.JSONDecodeError:
                    product_count = "N/A"

                # Replace products data with count
                formatted_order[6] = product_count
                self.orders_tree.insert('', 'end', values=formatted_order)

            # Load contact_messages
            contacts = conn.execute(
                '''
                SELECT id, user_id, name, email, phone, subject, message, timestamp 
                FROM contact_messages
                '''
            ).fetchall()
            for contact in contacts:
                contact_row = list(contact)
                # Format timestamp (if possible)
                try:
                    ts_obj = datetime.strptime(contact_row[7], '%Y-%m-%d %H:%M:%S')
                    contact_row[7] = ts_obj.strftime('%d %b %Y %I:%M %p')
                except:
                    pass

                self.contacts_tree.insert('', 'end', values=contact_row)

            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", f"Error loading data: {str(e)}")


if __name__ == '__main__':
    root = tk.Tk()
    app = DatabaseViewer(root)
    root.mainloop()
