"""
Database setup and utilities for Hisaab application
"""
import sqlite3
from datetime import datetime, timedelta
import random


def create_database(db_path: str = "app/local_database/hisaab.db") -> None:
    """Create the SQLite database and required tables."""
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row

    try:
        cursor = conn.cursor()

        # Table 1: Shopkeepers
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS shopkeepers (
                id INTEGER PRIMARY KEY,
                phone TEXT UNIQUE NOT NULL,
                name TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        print("✅ Shopkeepers table created")

        # Table 2: Customers
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY,
                shopkeeper_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                phone TEXT,
                total_owed REAL DEFAULT 0,
                total_paid REAL DEFAULT 0,
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (shopkeeper_id) REFERENCES shopkeepers(id),
                UNIQUE(shopkeeper_id, name)
            )
            """
        )
        print("✅ Customers table created")

        # Table 3: Credit Transactions
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS credit_transactions (
                id INTEGER PRIMARY KEY,
                shopkeeper_id INTEGER NOT NULL,
                customer_id INTEGER NOT NULL,
                customer_name TEXT,
                type TEXT NOT NULL,
                items TEXT,
                amount REAL NOT NULL,
                voice_note_text TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (shopkeeper_id) REFERENCES shopkeepers(id),
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            )
            """
        )

        conn.commit()
        print("✅ Database initialized")
    finally:
        conn.close()


def add_mock_data(db_path: str = "app/local_database/hisaab.db", shopkeeper_phone: str = None, shopkeeper_name: str = None) -> None:
    """Add realistic mock data for testing."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get shopkeeper details from user input if not provided
    if not shopkeeper_phone:
        shopkeeper_phone = input("Enter shopkeeper phone number (e.g., 923008246348): ").strip()
        if not shopkeeper_phone:
            shopkeeper_phone = "923008246348"  # Default fallback
    
    if not shopkeeper_name:
        shopkeeper_name = input("Enter shopkeeper/store name (e.g., Muzammil's Karyana Store): ").strip()
        if not shopkeeper_name:
            shopkeeper_name = "Muzammil's Karyana Store"  # Default fallback

    print(f"Adding shopkeeper: {shopkeeper_name} ({shopkeeper_phone})")

    # Add shopkeeper
    cursor.execute(
        "INSERT OR IGNORE INTO shopkeepers (phone, name) VALUES (?, ?)",
        (shopkeeper_phone, shopkeeper_name)
    )
    shopkeeper_id = cursor.lastrowid or 1

    # Customer data with nicknames
    customers = [
        ("Ali erum wala", "923001111111"),
        ("Rizwan colony wala", "923002222222"),
        ("Shahid mechanic", "923003333333"),
        ("Fatima aunty", "923004444444"),
        ("Hassan bhai", None),
        ("Saleem driver", "923006666666"),
        ("Bilal shop wala", "923007777777"),
        ("Nadia teacher", "923008888888"),
        ("Kamran uncle", None),
        ("Sana bibi", "923001010101"),
    ]

    # Items for transactions
    items_list = [
        ("2 unday, 1 doodh", 300),
        ("1 atta bag", 1200),
        ("3 sabun", 450),
        ("2 shampoo sachets", 80),
        ("5kg chawal", 900),
        ("1 cooking oil", 800),
        ("4 biscuit packets", 320),
        ("1 dishwashing liquid", 250),
        ("2 detergent", 600),
        ("6 dairy milk", 540),
        ("3kg atta", 450),
        ("1 chana dal", 350),
    ]

    # Add customers with various balances
    for name, phone in customers:
        cursor.execute(
            """
            INSERT OR IGNORE INTO customers 
            (shopkeeper_id, name, phone, total_owed, total_paid) 
            VALUES (?, ?, ?, ?, ?)
            """,
            (shopkeeper_id, name, phone, 0, 0)
        )

    conn.commit()

    # Get customer IDs
    cursor.execute("SELECT id, name FROM customers WHERE shopkeeper_id = ?", (shopkeeper_id,))
    customer_records = cursor.fetchall()

    # Add transactions for each customer
    for customer_id, customer_name in customer_records:
        # Random number of transactions (2-8)
        num_transactions = random.randint(2, 8)
        
        for i in range(num_transactions):
            # Random date in last 30 days
            days_ago = random.randint(0, 30)
            transaction_date = datetime.now() - timedelta(days=days_ago)
            
            # 70% credit given, 30% payment received
            transaction_type = random.choice(['credit_given'] * 7 + ['payment_received'] * 3)
            
            if transaction_type == 'credit_given':
                items, amount = random.choice(items_list)
                voice_text = f"{customer_name} ne {items} liye udhar"
                
                cursor.execute(
                    """
                    INSERT INTO credit_transactions 
                    (shopkeeper_id, customer_id, customer_name, type, items, amount, voice_note_text, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (shopkeeper_id, customer_id, customer_name, transaction_type, items, amount, voice_text, transaction_date)
                )
                
                # Update customer balance
                cursor.execute(
                    "UPDATE customers SET total_owed = total_owed + ? WHERE id = ?",
                    (amount, customer_id)
                )
            
            else:  # payment_received
                # Check current balance before adding payment
                cursor.execute("SELECT total_owed, total_paid FROM customers WHERE id = ?", (customer_id,))
                current = cursor.fetchone()
                current_balance = current[0] - current[1]
                
                if current_balance > 0:
                    # Payment up to current balance
                    amount = min(random.choice([100, 200, 300, 500, 1000]), current_balance)
                    voice_text = f"{customer_name} ne {amount} rupay diye"
                    
                    cursor.execute(
                        """
                        INSERT INTO credit_transactions 
                        (shopkeeper_id, customer_id, customer_name, type, items, amount, voice_note_text, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (shopkeeper_id, customer_id, customer_name, transaction_type, None, amount, voice_text, transaction_date)
                    )
                    
                    cursor.execute(
                        "UPDATE customers SET total_paid = total_paid + ? WHERE id = ?",
                        (amount, customer_id)
                    )

    conn.commit()
    conn.close()
    print("✅ Mock data added successfully")


def verify_database_data(db_path: str = "app/local_database/hisaab.db") -> None:
    """Verify and display database data"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT name, total_owed, total_paid, (total_owed - total_paid) as balance 
        FROM customers 
        WHERE (total_owed - total_paid) > 0
        ORDER BY balance DESC
    """)
    
    print("\n📊 Customers with outstanding balance:")
    for row in cursor.fetchall():
        print(f"  {row['name']}: Owed {row['total_owed']}, Paid {row['total_paid']}, Balance {row['balance']}")
    
    conn.close()


if __name__ == "__main__":
    print("🏪 Hisaab Database Setup")
    print("=" * 40)
    
    # Ask user if they want to create new database or use existing
    choice = input("Do you want to create a new database? (y/n): ").strip().lower()
    
    if choice == 'y':
        print("\n📝 Creating database...")
        create_database()
        
        print("\n👤 Shopkeeper Information:")
        shopkeeper_phone = input("Enter shopkeeper phone number: ").strip()
        shopkeeper_name = input("Enter shopkeeper/store name: ").strip()
        
        print("\n📊 Adding mock data...")
        add_mock_data(shopkeeper_phone=shopkeeper_phone, shopkeeper_name=shopkeeper_name)
        
        print("\n✅ Database setup complete!")
        verify_database_data()
    else:
        print("Using existing database...")
        verify_database_data()
