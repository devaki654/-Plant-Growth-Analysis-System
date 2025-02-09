import mysql.connector

# Establish a connection to the MySQL database
connection = mysql.connector.connect(
    host="localhost",  # Replace with your MySQL host (e.g., "localhost")
    user="root",  # Replace with your MySQL username
    password="devaki@123456",  # Replace with your MySQL password
    database="plat"  # Replace with your database name
)

# Create a cursor object
cursor = connection.cursor()

# Create the plant_info table if it doesn't exist
create_table_query = """
CREATE TABLE IF NOT EXISTS plant_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50),
    growth_days INT,
    season VARCHAR(50),
    disease VARCHAR(100),
    pesticides VARCHAR(100),
    soil VARCHAR(50),
    monsoon BOOLEAN,
    water_level VARCHAR(50),
    temperature FLOAT,
    humidity_level FLOAT
);
"""
cursor.execute(create_table_query)

# Insert data into the plant_info table
insert_query = """
INSERT INTO plant_info (name, growth_days, season, disease, pesticides, soil, monsoon, water_level, temperature, humidity_level)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
"""
data = [
    ("Mango", 120, "Summer", "Anthracnose", "Copper Fungicide", "Loamy", True, "High", 30.5, 60.0),
    ("Guava", 150, "Rainy", "Wilt", "Neem Oil", "Sandy Loam", True, "Moderate", 28.0, 70.0),
    ("Lemon", 90, "Winter", "Canker", "Bordeaux Mixture", "Clay Loam", False, "Low", 25.0, 50.0),
    ("Papaya", 180, "All Seasons", "Powdery Mildew", "Sulfur Dust", "Sandy", True, "Moderate", 29.0, 65.0),
    ("Pepper", 200, "Winter", "Leaf Spot", "Chlorothalonil", "Loamy", False, "High", 22.0, 55.0),
]

cursor.executemany(insert_query, data)
connection.commit()
print(f"Inserted {cursor.rowcount} rows into plant_info table.")

# Fetch and display the data
select_query = "SELECT * FROM plant_info;"
cursor.execute(select_query)
rows = cursor.fetchall()

print("\nPlant Details:")
for row in rows:
    print(row)

# Close the cursor and connection
cursor.close()
connection.close()
