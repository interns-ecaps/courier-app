import pyodbc
import time
from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Any, Optional, Tuple, Union


class DatabaseConnector:
    _instance = None
    
    def __new__(cls, server=None, database=None, username=None, password=None, port=15666):
        """Implement Singleton pattern to ensure only one connection exists"""
        if cls._instance is None:
            cls._instance = super(DatabaseConnector, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, server, database, username, password, port=15666):
        """Initialize database connection parameters"""
        self.server = server
        self.database = database
        self.username = username
        self.password = password
        self.port = port
        self.conn = None
        self.cursor = None
        self.conn_str = f"""
            DRIVER={{ODBC Driver 18 for SQL Server}};
            SERVER={server},{port};
            DATABASE={database};
            UID={username};
            PWD={password};
            TrustServerCertificate=yes;
            Connection Timeout=60;
        """
        self._initialized = True
        self.connect()

    def connect(self):
        """Establish connection to the database"""
        try:
            if self.conn is None:
                print(f"Connecting to {self.database} database...")
                self.conn = pyodbc.connect(self.conn_str)
                self.cursor = self.conn.cursor()
                return True
            return True  # Already connected
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    def disconnect(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None
            print("Connection closed.")

    def execute_query(self, query, fetch_all=True, params=None):
        """Execute a SQL query and return results"""
        tries = 0
        max_tries = 3
        
        while tries < max_tries:
            tries += 1
            try:
                # Ensure connection exists
                if not self.conn or not self.cursor:
                    self.connect()
                
                # Check if connection is still valid
                try:
                    # Simple test query to verify connection
                    test_cursor = self.conn.cursor()
                    test_cursor.execute("SELECT 1")
                    test_cursor.close()
                except:
                    # Connection is invalid, reconnect
                    print("Connection lost, reconnecting...")
                    self.conn = None
                    self.connect()
                
                # Execute the actual query
                if params:
                    self.cursor.execute(query, params)
                else:
                    self.cursor.execute(query)

                if fetch_all:
                    return self.cursor.fetchall()
                else:
                    return self.cursor.fetchone()
                    
            except pyodbc.Error as e:
                if tries < max_tries:
                    # Connection issue, try to reconnect
                    print(f"Query failed (attempt {tries}): {e}. Reconnecting...")
                    self.conn = None
                    time.sleep(1)  # Wait a bit before retrying
                else:
                    print(f"Query execution failed after {max_tries} attempts: {e}")
                    return None
        
        return None

    def commit(self):
        """Commit transactions to the database"""
        if self.conn:
            self.conn.commit()

    # Methods for ALLTRANSACTIONS table with specific columns
    def get_all_transactions(self, limit=None):
        columns = """
            TimeStamp, TransID, UserID, FirstName, LastName, DistributorID, Distributor,
            SuperDistributorID, SuperDistributor, ProdName, ProdCategory, RechargeSource,
            RechargeAmount
        """

        base_query = f"SELECT {columns} FROM ALLTRANSACTIONS"

        # Add limit if specified
        if limit:
            query = f"SELECT TOP {limit} {columns} FROM ALLTRANSACTIONS"
        else:
            query = base_query

        return self.execute_query(query)

    def get_transactions_by_date_range(self, start_date, end_date, limit=None):
        """
        Get transactions within a specified date range directly from the database
        """
        columns = """
            TimeStamp, TransID, UserID, FirstName, LastName, DistributorID, Distributor,
            SuperDistributorID, SuperDistributor, ProdName, ProdCategory, RechargeSource,
            RechargeAmount
        """

        base_query = f"""
            SELECT {columns}
            FROM ALLTRANSACTIONS
            WHERE TimeStamp BETWEEN ? AND ?
            ORDER BY TimeStamp DESC
        """
        if limit:
            query = f"SELECT TOP {limit} {columns} FROM ALLTRANSACTIONS WHERE TimeStamp BETWEEN ? AND ? ORDER BY TimeStamp DESC"
        else:
            query = base_query
        # Debug print
        print(f"Executing query with start_date={start_date}, end_date={end_date}")
        
        return self.execute_query(query, params=(start_date, end_date))
    
    def get_transactions_by_id(self, trans_id):
        """Get transactions by TransID"""
        query = "SELECT * FROM ALLTRANSACTIONS WHERE TransID = ?"
        return self.execute_query(query, params=(trans_id,))

    def get_transactions_by_user(self, user_id):
        """Get transactions by UserID"""
        query = "SELECT * FROM ALLTRANSACTIONS WHERE UserID = ?"
        return self.execute_query(query, params=(user_id,))

    def get_transactions_by_distributor(self, distributor_id):
        """Get transactions by DistributorID"""
        query = "SELECT * FROM ALLTRANSACTIONS WHERE DistributorID = ?"
        return self.execute_query(query, params=(distributor_id,))

    def get_transactions_by_super_distributor(self, super_distributor_id):
        """Get transactions by SuperDistributorID"""
        query = "SELECT * FROM ALLTRANSACTIONS WHERE SuperDistributorID = ?"
        return self.execute_query(query, params=(super_distributor_id,))

    def get_transactions_by_product_category(self, category):
        """Get transactions by ProdCategory"""
        query = "SELECT * FROM ALLTRANSACTIONS WHERE ProdCategory = ?"
        return self.execute_query(query, params=(category,))

    def get_transactions_by_status(self, status):
        """Get transactions by Status"""
        query = "SELECT * FROM ALLTRANSACTIONS WHERE Status = ?"
        return self.execute_query(query, params=(status,))

    def get_transactions_by_amount_range(self, min_amount, max_amount):
        """Get transactions within an amount range"""
        query = "SELECT * FROM ALLTRANSACTIONS WHERE RechargeAmount BETWEEN ? AND ?"
        return self.execute_query(query, params=(min_amount, max_amount))

    def get_transaction_summary_by_distributor(self):
        """Get summary of transactions grouped by distributor"""
        query = """
            SELECT 
                DistributorID, 
                Distributor, 
                COUNT(*) as TransactionCount, 
                SUM(RechargeAmount) as TotalAmount, 
                SUM(MarginAmount) as TotalMargin
            FROM ALLTRANSACTIONS
            GROUP BY DistributorID, Distributor
        """
        return self.execute_query(query)

    def get_transaction_summary_by_product(self):
        """Get summary of transactions grouped by product category"""
        query = """
            SELECT 
                ProdCategory, 
                COUNT(*) as TransactionCount, 
                SUM(RechargeAmount) as TotalAmount, 
                SUM(MarginAmount) as TotalMargin
            FROM ALLTRANSACTIONS
            GROUP BY ProdCategory
        """
        return self.execute_query(query)

    # Methods for AllRefunds table
    def get_all_refunds(self, limit=None):
        """Get refunds from AllRefunds table"""
        query = "SELECT * FROM AllRefunds"
        if limit:
            query = f"SELECT TOP {limit} * FROM AllRefunds"
        return self.execute_query(query)

    # Advanced query methods
    def execute_custom_query(self, query, params=None):
        """Execute a custom SQL query"""
        return self.execute_query(query, params=params)

    def get_transaction_data_as_dict(self, transaction_row):
        """Convert a transaction row to a dictionary with proper column names"""
        columns = [
            "TimeStamp",
            "TransID",
            "UserID",
            "FirstName",
            "LastName",
            "DistributorID",
            "Distributor",
            "SuperDistributorID",
            "SuperDistributor",
            "ProdName",
            "ProdCategory",
            "RechargeSource",
            "RechargeAmount"
        ]

        result = {}
        for i, column in enumerate(columns):
            if i < len(transaction_row):
                result[column] = transaction_row[i]

        return result

    def get_transactions_as_dicts(self, transactions):
        """Convert multiple transaction rows to dictionaries"""
        return [self.get_transaction_data_as_dict(row) for row in transactions]
