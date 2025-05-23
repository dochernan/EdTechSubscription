import pyodbc

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=172.25.43.9,52799;"
    "DATABASE=destiny;"
    "UID=sa;"
    "PWD=D35+1ny!;"
    "Encrypt=yes;"
    "TrustServerCertificate=yes"
)

try:
    conn = pyodbc.connect(conn_str, timeout=5)
    print("✅ Connection successful with encryption fallback!")

    cursor = conn.cursor()
    cursor.execute("SELECT TOP 5 * FROM INFORMATION_SCHEMA.TABLES")
    for row in cursor.fetchall():
        print(row)
    conn.close()

except pyodbc.Error as e:
    print("❌ Connection failed.")
    print(e)
