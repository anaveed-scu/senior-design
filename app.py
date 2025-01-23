from flask import Flask, request, redirect, render_template_string
import sqlite3
import numpy as np
from sklearn.neighbors import NearestNeighbors

app = Flask(__name__)

# Initialize the database with necessary tables
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS borrowers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            amount_want_to_borrow REAL NOT NULL,
            reason TEXT NOT NULL
        )
    """)
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
            <link href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;600&display=swap" rel="stylesheet">
            <style>
                body {
                    font-family: 'Open Sans', sans-serif;
                    margin: 0;
                    padding: 0;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    overflow: hidden;
                    position: relative;
                }

                .menu-container {
                    background-color: white;
                    border-radius: 8px;
                    padding: 30px;
                    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
                    width: 100%;
                    max-width: 600px;
                    text-align: center;
                    position: relative;
                    z-index: 1;
                }

                h1 {
                    font-size: 36px;
                    font-weight: 600;
                    color: #333;
                    margin-bottom: 30px;
                }

                .menu-btn {
                    background-color: #007bff;
                    color: white;
                    padding: 15px 30px;
                    border-radius: 8px;
                    width: 100%;
                    margin: 10px 0;
                    font-size: 18px;
                    cursor: pointer;
                    border: none;
                    transition: background-color 0.3s ease;
                }

                .menu-btn:hover {
                    background-color: #0056b3;
                }

                .background {
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: #ff8a00;
                    background: linear-gradient(315deg, #ff8a00 0%, #da1b60 74%);
                    animation: gradientBG 10s ease infinite;
                    z-index: 0;
                }

                @keyframes gradientBG {
                    0% {
                        background: linear-gradient(315deg, #ff8a00 0%, #da1b60 74%);
                    }
                    50% {
                        background: linear-gradient(315deg, #ff2a68 0%, #fc4a1a 74%);
                    }
                    100% {
                        background: linear-gradient(315deg, #ff8a00 0%, #da1b60 74%);
                    }
                }
            </style>
        </head>
        <body>
            <div class="background"></div>
            <div class="menu-container">
                <h1>Welcome to the Application</h1>
                <button class="menu-btn" onclick="window.location.href='/borrowers'">Borrowers Form</button>
                <button class="menu-btn" onclick="window.location.href='/lenders'">Lenders Form</button>
                <button class="menu-btn" onclick="window.location.href='/display_borrowers'">View Borrowers</button>
                <button class="menu-btn" onclick="window.location.href='/display_lenders'">View Lenders</button>
                <button class="menu-btn" onclick="window.location.href='/match'">Match Borrowers and Lenders</button>
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
            <title>Borrower Form</title>
            <link href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;600&display=swap" rel="stylesheet">
            <style>
                body {
                    font-family: 'Open Sans', sans-serif;
                    margin: 0;
                    padding: 0;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    overflow: hidden;
                    position: relative;
                }

                .form-container {
                    background: white;
                    border-radius: 8px;
                    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
                    padding: 40px;
                    width: 100%;
                    max-width: 500px;
                    position: relative;
                    z-index: 1;
                }

                h1 {
                    font-size: 24px;
                    font-weight: 600;
                    margin-bottom: 20px;
                    text-align: center;
                    color: #333;
                }

                .input-field {
                    margin-bottom: 20px;
                    width: 100%;
                }

                .input-field input,
                .input-field textarea {
                    width: 100%;
                    padding: 15px;
                    border-radius: 8px;
                    border: 1px solid #ddd;
                    font-size: 16px;
                    color: #555;
                }

                .input-field input:focus,
                .input-field textarea:focus {
                    border-color: #007bff;
                    outline: none;
                }

                .input-field textarea {
                    resize: vertical;
                    height: 120px;
                }

                .submit-btn {
                    background-color: #007bff;
                    color: white;
                    padding: 15px 30px;
                    border-radius: 8px;
                    border: none;
                    font-size: 18px;
                    cursor: pointer;
                    width: 100%;
                    transition: background-color 0.3s;
                }

                .submit-btn:hover {
                    background-color: #0056b3;
                }

                .back-link {
                    display: block;
                    text-align: center;
                    margin-top: 20px;
                    font-size: 16px;
                }

                .back-link a {
                    text-decoration: none;
                    color: #007bff;
                }

                .background {
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: #ff8a00;
                    background: linear-gradient(315deg, #ff8a00 0%, #da1b60 74%);
                    animation: gradientBG 10s ease infinite;
                    z-index: 0;
                }

                @keyframes gradientBG {
                    0% {
                        background: linear-gradient(315deg, #ff8a00 0%, #da1b60 74%);
                    }
                    50% {
                        background: linear-gradient(315deg, #ff2a68 0%, #fc4a1a 74%);
                    }
                    100% {
                        background: linear-gradient(315deg, #ff8a00 0%, #da1b60 74%);
                    }
                }
            </style>
        </head>
        <body>
            <div class="background"></div>
            <div class="form-container">
                <h1>Enter Borrower Data</h1>
                <form method="POST" action="/borrowers">
                    <div class="input-field">
                        <input type="text" id="name" name="name" placeholder="Enter your name" required>
                    </div>
                    <div class="input-field">
                        <input type="number" id="amount_want_to_borrow" name="amount_want_to_borrow" placeholder="Amount to Borrow" required>
                    </div>
                    <div class="input-field">
                        <textarea id="reason" name="reason" placeholder="Reason for borrowing" required></textarea>
                    </div>
                    <button type="submit" class="submit-btn">Submit</button>
                </form>
                <div class="back-link">
                    <a href="/">Go Back</a>
                </div>
            </div>
        </body>
        </html>
        """
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
            <title>Lender Form</title>
            <link href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;600&display=swap" rel="stylesheet">
            <style>
                body {
                    font-family: 'Open Sans', sans-serif;
                    margin: 0;
                    padding: 0;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    overflow: hidden;
                    position: relative;
                }

                .form-container {
                    background: white;
                    border-radius: 8px;
                    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
                    padding: 40px;
                    width: 100%;
                    max-width: 500px;
                    position: relative;
                    z-index: 1;
                }

                h1 {
                    font-size: 24px;
                    font-weight: 600;
                    margin-bottom: 20px;
                    text-align: center;
                    color: #333;
                }

                .input-field {
                    margin-bottom: 20px;
                    width: 100%;
                }

                .input-field input {
                    width: 100%;
                    padding: 15px;
                    border-radius: 8px;
                    border: 1px solid #ddd;
                    font-size: 16px;
                    color: #555;
                }

                .input-field input:focus {
                    border-color: #007bff;
                    outline: none;
                }

                .submit-btn {
                    background-color: #007bff;
                    color: white;
                    padding: 15px 30px;
                    border-radius: 8px;
                    border: none;
                    font-size: 18px;
                    cursor: pointer;
                    width: 100%;
                    transition: background-color 0.3s;
                }

                .submit-btn:hover {
                    background-color: #0056b3;
                }

                .back-link {
                    display: block;
                    text-align: center;
                    margin-top: 20px;
                    font-size: 16px;
                }

                .back-link a {
                    text-decoration: none;
                    color: #007bff;
                }

                .background {
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: #ff8a00;
                    background: linear-gradient(315deg, #ff8a00 0%, #da1b60 74%);
                    animation: gradientBG 10s ease infinite;
                    z-index: 0;
                }

                @keyframes gradientBG {
                    0% {
                        background: linear-gradient(315deg, #ff8a00 0%, #da1b60 74%);
                    }
                    50% {
                        background: linear-gradient(315deg, #ff2a68 0%, #fc4a1a 74%);
                    }
                    100% {
                        background: linear-gradient(315deg, #ff8a00 0%, #da1b60 74%);
                    }
                }
            </style>
        </head>
        <body>
            <div class="background"></div>
            <div class="form-container">
                <h1>Enter Lender Data</h1>
                <form method="POST" action="/lenders">
                    <div class="input-field">
                        <input type="text" id="name" name="name" placeholder="Enter your name" required>
                    </div>
                    <div class="input-field">
                        <input type="number" id="amount_want_to_lend" name="amount_want_to_lend" placeholder="Amount to Lend" required>
                    </div>
                    <button type="submit" class="submit-btn">Submit</button>
                </form>
                <div class="back-link">
                    <a href="/">Go Back</a>
                </div>
            </div>
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
    borrowers = cursor.fetchall()
    conn.close()

    return render_template_string(
        """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Borrowers</title>
            <link href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;600&display=swap" rel="stylesheet">
            <style>
                body {
                    font-family: 'Open Sans', sans-serif;
                    margin: 0;
                    padding: 0;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    overflow: hidden;
                    position: relative;
                }

                .table-container {
                    background-color: white;
                    border-radius: 8px;
                    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
                    padding: 20px;
                    width: 100%;
                    max-width: 600px;
                    position: relative;
                    z-index: 1;
                    overflow-y: auto;
                    height: 70vh;
                }

                h1 {
                    text-align: center;
                    margin-bottom: 20px;
                }

                table {
                    width: 100%;
                    border-collapse: collapse;
                }

                th, td {
                    padding: 12px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }

                .background {
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: #ff8a00;
                    background: linear-gradient(315deg, #ff8a00 0%, #da1b60 74%);
                    animation: gradientBG 10s ease infinite;
                    z-index: 0;
                }

                @keyframes gradientBG {
                    0% {
                        background: linear-gradient(315deg, #ff8a00 0%, #da1b60 74%);
                    }
                    50% {
                        background: linear-gradient(315deg, #ff2a68 0%, #fc4a1a 74%);
                    }
                    100% {
                        background: linear-gradient(315deg, #ff8a00 0%, #da1b60 74%);
                    }
                }
            </style>
        </head>
        <body>
            <div class="background"></div>
            <div class="table-container">
                <h1>Borrowers</h1>
                <table>
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Amount</th>
                            <th>Reason</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for borrower in borrowers %}
                            <tr>
                                <td>{{ borrower[1] }}</td>
                                <td>{{ borrower[2] }}</td>
                                <td>{{ borrower[3] }}</td>
                            </tr>
                        {% endfor %}
                    </tbody>
                </table>
                <div class="back-link">
                    <a href="/">Go Back</a>
                </div>
            </div>
        </body>
        </html>
        """, borrowers=borrowers)

# Route: Display Lenders
@app.route("/display_lenders")
def display_lenders():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM lenders")
    lenders = cursor.fetchall()
    conn.close()

    return render_template_string(
        """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Lenders</title>
            <link href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;600&display=swap" rel="stylesheet">
            <style>
                body {
                    font-family: 'Open Sans', sans-serif;
                    margin: 0;
                    padding: 0;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    overflow: hidden;
                    position: relative;
                }

                .table-container {
                    background-color: white;
                    border-radius: 8px;
                    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
                    padding: 20px;
                    width: 100%;
                    max-width: 600px;
                    position: relative;
                    z-index: 1;
                    overflow-y: auto;
                    height: 70vh;
                }

                h1 {
                    text-align: center;
                    margin-bottom: 20px;
                }

                table {
                    width: 100%;
                    border-collapse: collapse;
                }

                th, td {
                    padding: 12px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }

                .background {
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: #ff8a00;
                    background: linear-gradient(315deg, #ff8a00 0%, #da1b60 74%);
                    animation: gradientBG 10s ease infinite;
                    z-index: 0;
                }

                @keyframes gradientBG {
                    0% {
                        background: linear-gradient(315deg, #ff8a00 0%, #da1b60 74%);
                    }
                    50% {
                        background: linear-gradient(315deg, #ff2a68 0%, #fc4a1a 74%);
                    }
                    100% {
                        background: linear-gradient(315deg, #ff8a00 0%, #da1b60 74%);
                    }
                }
            </style>
        </head>
        <body>
            <div class="background"></div>
            <div class="table-container">
                <h1>Lenders</h1>
                <table>
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Amount</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for lender in lenders %}
                            <tr>
                                <td>{{ lender[1] }}</td>
                                <td>{{ lender[2] }}</td>
                            </tr>
                        {% endfor %}
                    </tbody>
                </table>
                <div class="back-link">
                    <a href="/">Go Back</a>
                </div>
            </div>
        </body>
        </html>
        """, lenders=lenders)

# Route: Match Borrowers and Lenders using Machine Learning
@app.route("/match")
def match():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Fetch all borrowers and lenders
    cursor.execute("SELECT * FROM borrowers")
    borrowers = cursor.fetchall()
    cursor.execute("SELECT * FROM lenders")
    lenders = cursor.fetchall()
    conn.close()

    # Prepare data for KNN model: Borrowers' and Lenders' amounts
    borrowers_data = np.array([borrower[2] for borrower in borrowers]).reshape(-1, 1)  # Borrowing amounts
    lenders_data = np.array([lender[2] for lender in lenders]).reshape(-1, 1)  # Lending amounts

    # Use KNN to find closest lender for each borrower
    knn = NearestNeighbors(n_neighbors=1)  # We want to find the closest match
    knn.fit(lenders_data)

    matches = []

    for borrower in borrowers:
        borrower_name = borrower[1]
        borrower_amount = borrower[2]

        # Find the closest lender to this borrower using KNN
        distances, indices = knn.kneighbors([[borrower_amount]])  # Find nearest lender
        closest_lender_idx = indices[0][0]
        closest_lender_distance = distances[0][0]
        closest_lender = lenders[closest_lender_idx]

        matches.append({
            'borrower': borrower_name,
            'borrowed_amount': borrower_amount,
            'lender': closest_lender[1],
            'lended_amount': closest_lender[2],
            'distance': closest_lender_distance
        })

    return render_template_string(
        """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Matches</title>
            <link href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;600&display=swap" rel="stylesheet">
            <style>
                body {
                    font-family: 'Open Sans', sans-serif;
                    margin: 0;
                    padding: 0;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    overflow: hidden;
                    position: relative;
                }

                .table-container {
                    background-color: white;
                    border-radius: 8px;
                    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
                    padding: 20px;
                    width: 100%;
                    max-width: 600px;
                    position: relative;
                    z-index: 1;
                    overflow-y: auto;
                    height: 70vh;
                }

                h1 {
                    text-align: center;
                    margin-bottom: 20px;
                }

                table {
                    width: 100%;
                    border-collapse: collapse;
                }

                th, td {
                    padding: 12px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }

                .background {
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: #ff8a00;
                    background: linear-gradient(315deg, #ff8a00 0%, #da1b60 74%);
                    animation: gradientBG 10s ease infinite;
                    z-index: 0;
                }

                @keyframes gradientBG {
                    0% {
                        background: linear-gradient(315deg, #ff8a00 0%, #da1b60 74%);
                    }
                    50% {
                        background: linear-gradient(315deg, #ff2a68 0%, #fc4a1a 74%);
                    }
                    100% {
                        background: linear-gradient(315deg, #ff8a00 0%, #da1b60 74%);
                    }
                }
            </style>
        </head>
        <body>
            <div class="background"></div>
            <div class="table-container">
                <h1>Matched Borrowers and Lenders</h1>
                <table>
                    <thead>
                        <tr>
                            <th>Borrower</th>
                            <th>Amount Borrowed</th>
                            <th>Lender</th>
                            <th>Amount Lended</th>
                            <th>Match Distance</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for match in matches %}
                            <tr>
                                <td>{{ match['borrower'] }}</td>
                                <td>{{ match['borrowed_amount'] }}</td>
                                <td>{{ match['lender'] }}</td>
                                <td>{{ match['lended_amount'] }}</td>
                                <td>{{ match['distance'] }}</td>
                            </tr>
                        {% endfor %}
                    </tbody>
                </table>
                <div class="back-link">
                    <a href="/">Go Back</a>
                </div>
            </div>
        </body>
        </html>
        """, matches=matches)

if __name__ == "__main__":
    # Initialize DB
    init_db()

    # Run the Flask app
    app.run(debug=True)
