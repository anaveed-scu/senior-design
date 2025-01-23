from flask import Flask, request, redirect, render_template_string
import sqlite3
from sklearn.neighbors import NearestNeighbors
import numpy as np

app = Flask(__name__)

# Initialize database
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL
        )
    """)
    # Borrowers table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS borrowers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            amount_want_to_borrow REAL NOT NULL,
            reason TEXT NOT NULL
        )
    """)
    # Lenders table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lenders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            amount_want_to_lend REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Route: Home (Root)
@app.route("/")
def home():
    return render_template_string(
        """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Home</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    text-align: center;
                    background-color: #f4f4f9;
                    margin: 0;
                    padding: 0;
                }

                .container {
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    flex-direction: column;
                }

                h1 {
                    color: #333;
                    margin-bottom: 30px;
                }

                .button {
                    display: inline-block;
                    background-color: #4CAF50;
                    color: white;
                    padding: 15px 32px;
                    text-align: center;
                    text-decoration: none;
                    font-size: 18px;
                    border-radius: 25px;
                    margin: 10px;
                    transition: 0.3s ease-in-out;
                    box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
                }

                .button:hover {
                    background-color: #45a049;
                    transform: scale(1.1);
                }

                .button:active {
                    transform: scale(0.95);
                }

                .button-container {
                    display: flex;
                    flex-wrap: wrap;
                    justify-content: center;
                    gap: 20px;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Welcome to the Application</h1>
                <div class="button-container">
                    <a href="/borrowers" class="button">Borrowers Form</a>
                    <a href="/lenders" class="button">Lenders Form</a>
                    <a href="/display_borrowers" class="button">View Borrowers</a>
                    <a href="/display_lenders" class="button">View Lenders</a>
                    <a href="/match" class="button">Match Borrowers and Lenders</a>
                </div>
            </div>
        </body>
        </html>
        """
    )

# Route: Borrowers (Input Form)
@app.route("/borrowers", methods=["GET", "POST"])
def borrowers():
    if request.method == "POST":
        name = request.form.get("name")
        amount_want_to_borrow = request.form.get("amount_want_to_borrow")
        reason = request.form.get("reason")

        # Insert into database
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO borrowers (name, amount_want_to_borrow, reason) VALUES (?, ?, ?)", 
            (name, float(amount_want_to_borrow), reason)
        )
        conn.commit()
        conn.close()

        return redirect("/display_borrowers")

    return render_template_string(
        """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Borrower Data</title>
        </head>
        <body>
            <h1>Enter Borrower Data</h1>
            <form method="POST" action="/borrowers">
                <label for="name">Name:</label>
                <input type="text" id="name" name="name" required>
                <br>
                <label for="amount_want_to_borrow">Amount Want to Borrow:</label>
                <input type="number" id="amount_want_to_borrow" name="amount_want_to_borrow" required>
                <br>
                <label for="reason">Reason for Borrowing:</label>
                <textarea id="reason" name="reason" required></textarea>
                <br><br>
                <button type="submit">Submit</button>
            </form>
            <br>
            <a href="/">Go Back</a>
        </body>
        </html>
        """
    )

# Route: Display Borrowers
@app.route("/display_borrowers")
def display_borrowers():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM borrowers")
    rows = cursor.fetchall()
    conn.close()

    return render_template_string(
        """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Borrower Records</title>
        </head>
        <body>
            <h1>All Borrowers</h1>
            <table border="1">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Amount Want to Borrow</th>
                        <th>Reason</th>
                    </tr>
                </thead>
                <tbody>
                    {% for row in rows %}
                    <tr>
                        <td>{{ row[0] }}</td>
                        <td>{{ row[1] }}</td>
                        <td>{{ row[2] }}</td>
                        <td>{{ row[3] }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            <br>
            <a href="/">Go Back</a>
        </body>
        </html>
        """,
        rows=rows
    )

# Route: Lenders (Input Form)
@app.route("/lenders", methods=["GET", "POST"])
def lenders():
    if request.method == "POST":
        name = request.form.get("name")
        amount_want_to_lend = request.form.get("amount_want_to_lend")

        # Insert into database
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO lenders (name, amount_want_to_lend) VALUES (?, ?)", 
            (name, float(amount_want_to_lend))
        )
        conn.commit()
        conn.close()

        return redirect("/display_lenders")

    return render_template_string(
        """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Lender Data</title>
        </head>
        <body>
            <h1>Enter Lender Data</h1>
            <form method="POST" action="/lenders">
                <label for="name">Name:</label>
                <input type="text" id="name" name="name" required>
                <br>
                <label for="amount_want_to_lend">Amount Want to Lend:</label>
                <input type="number" id="amount_want_to_lend" name="amount_want_to_lend" required>
                <br><br>
                <button type="submit">Submit</button>
            </form>
            <br>
            <a href="/">Go Back</a>
        </body>
        </html>
        """
    )

# Route: Display Lenders
@app.route("/display_lenders")
def display_lenders():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM lenders")
    rows = cursor.fetchall()
    conn.close()

    return render_template_string(
        """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Lender Records</title>
        </head>
        <body>
            <h1>All Lenders</h1>
            <table border="1">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Amount Want to Lend</th>
                    </tr>
                </thead>
                <tbody>
                    {% for row in rows %}
                    <tr>
                        <td>{{ row[0] }}</td>
                        <td>{{ row[1] }}</td>
                        <td>{{ row[2] }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            <br>
            <a href="/">Go Back</a>
        </body>
        </html>
        """,
        rows=rows
    )

# Route: Match Borrowers and Lenders with ML Algorithm (KNN)
@app.route("/match")
def match():
    # Fetch borrowers and lenders from the database
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    
    # Get all borrowers
    cursor.execute("SELECT * FROM borrowers")
    borrowers = cursor.fetchall()
    
    # Get all lenders
    cursor.execute("SELECT * FROM lenders")
    lenders = cursor.fetchall()
    
    conn.close()

    # Prepare data for machine learning model
    borrower_amounts = np.array([borrower[2] for borrower in borrowers]).reshape(-1, 1)  # Borrower amounts (amount_want_to_borrow)
    lender_amounts = np.array([lender[2] for lender in lenders]).reshape(-1, 1)  # Lender amounts (amount_want_to_lend)

    # Use K-Nearest Neighbors to find the closest lender for each borrower
    knn = NearestNeighbors(n_neighbors=1)  # We're only interested in the closest lender
    knn.fit(lender_amounts)  # Fit the model using lender amounts

    # Find the closest lenders for each borrower
    matches = []
    for borrower in borrowers:
        borrower_id, borrower_name, amount_to_borrow, reason = borrower
        distance, index = knn.kneighbors([[amount_to_borrow]])  # Find closest lender

        closest_lender = lenders[index[0][0]]  # Get the closest lender based on index
        lender_name = closest_lender[1]
        lender_amount = closest_lender[2]

        # Store the match
        matches.append({
            "borrower": borrower_name,
            "borrower_id": borrower_id,
            "borrower_amount": amount_to_borrow,
            "lender": lender_name,
            "lender_amount": lender_amount,
        })

    return render_template_string(
        """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Match Borrowers and Lenders</title>
            <style>
                .container {
                    display: flex;
                    justify-content: space-between;
                    gap: 20px;
                }
                .box {
                    width: 45%;
                    padding: 10px;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                }
                th, td {
                    padding: 8px;
                    text-align: left;
                    border: 1px solid #ddd;
                }
            </style>
        </head>
        <body>
            <h1>Matching Borrowers and Lenders</h1>

            <div class="container">
                <div class="box">
                    <h2>Borrowers</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Name</th>
                                <th>Amount to Borrow</th>
                                <th>Reason</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for borrower in borrowers %}
                            <tr>
                                <td>{{ borrower[0] }}</td>
                                <td>{{ borrower[1] }}</td>
                                <td>{{ borrower[2] }}</td>
                                <td>{{ borrower[3] }}</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>

                <div class="box">
                    <h2>Lenders</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Name</th>
                                <th>Amount to Lend</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for lender in lenders %}
                            <tr>
                                <td>{{ lender[0] }}</td>
                                <td>{{ lender[1] }}</td>
                                <td>{{ lender[2] }}</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>

            <h2>Matching Results</h2>
            <table>
                <thead>
                    <tr>
                        <th>Borrower Name</th>
                        <th>Amount to Borrow</th>
                        <th>Lender Name</th>
                        <th>Lender Amount</th>
                    </tr>
                </thead>
                <tbody>
                    {% for match in matches %}
                    <tr>
                        <td>{{ match.borrower }}</td>
                        <td>{{ match.borrower_amount }}</td>
                        <td>{{ match.lender }}</td>
                        <td>{{ match.lender_amount }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            <a href="/">Go Back</a>
        </body>
        </html>
        """,
        borrowers=borrowers,
        lenders=lenders,
        matches=matches
    )

if __name__ == "__main__":
    app.run(debug=True)