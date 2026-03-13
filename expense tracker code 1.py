
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import json
from streamlit_option_menu import option_menu
from streamlit_lottie import st_lottie
import filelock

# --- Configuration Constants ---
EXPENSE_CATEGORIES = [
    "Groceries", "Rent", "Utilities", "Transportation", "Dining Out",
    "Entertainment", "Shopping", "Healthcare", "Education", "Other"
]
INCOME_CATEGORIES = [
    "Salary", "Freelance", "Investment", "Gift", "Other"
]
DATE_FORMAT = "%Y-%m-%d"
TRANSACTIONS_FILE = "transactions.csv"
USERS_FILE = "users.csv"
BUDGETS_FILE = "budgets.csv"

# --- Custom CSS for Styling ---
CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

body {
    font-family: 'Poppins', sans-serif;
    color: #222;
    background-color: #f9f9f9;
}

.stApp {
    background-color: #f9f9f9;
}

.stSidebar {
    background-color: #ffffff;
    padding: 20px;
    box-shadow: 2px 0px 5px rgba(0,0,0,0.03);
    border-radius: 10px;
}

.stSidebar h2 {
    color: #2196F3;
    font-weight: 700;
    margin-bottom: 20px;
}

.stButton>button {
    background-color: #2196F3;
    color: white;
    padding: 10px 20px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-weight: 600;
    transition: background-color 0.3s ease, transform 0.2s ease, box-shadow 0.3s ease;
    box-shadow: 0 4px 6px rgba(0,0,0,0.07);
}

.stButton>button:hover {
    background-color: #1976D2;
    transform: translateY(-3px);
    box-shadow: 0 6px 8px rgba(0,0,0,0.10);
}

.stTextInput>div>div>input, .stSelectbox>div>div>select, .stDateInput>div>div>input {
    border-radius: 8px;
    border: 1px solid #e0e0e0;
    padding: 10px 12px;
    transition: border-color 0.3s ease, box-shadow 0.3s ease;
    background-color: #ffffff;
    color: #000000 !important;
    font-weight: 500;
}

.stTextInput>div>div>input:focus, .stSelectbox>div>div:focus-within, .stDateInput>div>div:focus-within {
    border-color: #2196F3;
    box-shadow: 0 0 0 0.2rem rgba(33, 150, 243, 0.15);
    outline: none;
}

.stMetric {
    background-color: #ffffff;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.07);
    margin-bottom: 20px;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    border-left: 5px solid #2196F3;
}

.stMetric:hover {
    transform: translateY(-5px);
    box-shadow: 0 6px 12px rgba(0,0,0,0.10);
}

.stMetric label {
    font-size: 1.2em;
    font-weight: 600;
    color: #444;
    margin-bottom: 5px;
}

.stMetric .css-1g6x9st-StMetric {
    font-size: 2.2em !important;
    font-weight: 700;
    color: #222;
}

.icon {
    margin-right: 8px;
    vertical-align: middle;
}

.fade-in {
    animation: fadeIn 1s ease-in-out;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.st-emotion-cache-1c7y2kl {
    padding: 2rem 3rem;
    background-color: #ffffff;
    border-radius: 10px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}

h1, h2, h3, h4, h5, h6 {
    color: #222;
    font-weight: 700;
}

p {
    line-height: 1.6;
    color: #222;
}

.stDataFrame {
    border-radius: 8px;
    overflow: hidden;
    background: #fff;
}

/* Fix for selectbox text visibility */
div[data-baseweb="select"] div[class*="SingleValue"],
div[data-baseweb="select"] div[class*="Placeholder"],
div[data-baseweb="select"] div[class*="ValueContainer"],
div[data-baseweb="select"] input {
    color: #000000 !important;
    background-color: #ffffff !important;
    font-weight: 500 !important;
}

div[data-baseweb="menu"],
div[data-baseweb="select"] ul {
    background-color: #ffffff !important;
    color: #000000 !important;
}

div[data-baseweb="menu"] li {
    color: #000000 !important;
    background-color: #ffffff !important;
}

div[data-baseweb="menu"] li:hover {
    background-color: #1976D2 !important;
    color: white !important;
}

.stAlert > div {
    background-color: #dff0d8;
    color: #3c763d;
}

.stAlert[data-testid="stAlert"][role="alert"][data-baseweb="notification"] > div {
    background-color: #dff0d8;
    color: #3c763d;
}

.stAlert[data-testid="stAlert"][role="alert"][data-baseweb="notification"][kind="warning"] > div {
    background-color: #fcf8e3;
    color: #8a6d3b;
}

.stAlert[data-testid="stAlert"][role="alert"][data-baseweb="notification"][kind="error"] > div {
    background-color: #f2dede;
    color: #dc3545;
}

.stAlert[data-testid="stAlert"][role="alert"][data-baseweb="notification"][kind="info"] > div {
    background-color: #d9edf7;
    color: #31708f;
}
"""

# --- Lottie Animations (Embedded JSON Data) ---
LOTTIE_FINANCIAL_GROWTH = {
    "v": "5.7.4", "fr": 60, "ip": 0, "op": 120, "w": 500, "h": 500, "nm": "Financial Growth",
    "ddd": 0, "assets": [], "layers": [
        {"ddd": 0, "ind": 0, "ty": 4, "nm": "Graph", "sr": 1, "ks": {
            "o": {"a": 0, "k": 100, "ix": 1},
            "r": {"a": 0, "k": 0, "ix": 2},
            "p": {"a": 0, "k": [250, 250, 0], "ix": 3},
            "a": {"a": 0, "k": [250, 250, 0], "ix": 4},
            "s": {"a": 0, "k": [100, 100, 100], "ix": 5}
        }, "ao": 0, "shapes": [
            {"ty": "gr", "it": [
                {"ind": 0, "ty": "sh", "ix": 1, "ks": {
                    "a": 0, "k": {
                        "i": [[0.833, 0.833], [0.833, 0.833], [0.833, 0.833], [0.833, 0.833]],
                        "o": [[0.167, 0.167], [0.167, 0.167], [0.167, 0.167], [0.167, 0.167]],
                        "v": [[100, 400], [200, 200], [300, 300], [400, 100]],
                        "c": False
                    }, "ix": 2
                }, "nm": "Path 1", "mn": "ADBE Vector Shape - Group", "hd": False},
                {"ty": "st", "c": {"a": 0, "k": [0.298, 0.686, 0.314, 1], "ix": 3},
                 "o": {"a": 0, "k": 100, "ix": 4}, "lw": {"a": 0, "k": 10, "ix": 5},
                 "lc": 1, "lj": 1, "ml": 4, "mn": "ADBE Vector Stroke", "hd": False},
                {"ty": "fl", "c": {"a": 0, "k": [0.298, 0.686, 0.314, 0.5], "ix": 6},
                 "o": {"a": 0, "k": 100, "ix": 7}, "r": 1, "mn": "ADBE Vector Fill", "hd": False}
            ], "nm": "Group 1", "np": 3, "cix": 2, "ix": 1, "mn": "ADBE Vector Group", "hd": False}
        ], "ef": [], "ip": 0, "op": 120, "st": 0, "bm": 0}
    ], "markers": []
}

LOTTIE_DATA_ANALYSIS = {
    "v": "5.7.4", "fr": 60, "ip": 0, "op": 120, "w": 500, "h": 500, "nm": "Data Analysis",
    "ddd": 0, "assets": [], "layers": [
        {"ddd": 0, "ind": 0, "ty": 4, "nm": "Chart", "sr": 1, "ks": {"o": {"a": 0, "k": 100, "ix": 1}, "r": {"a": 0, "k": 0, "ix": 2}, "p": {"a": 0, "k": [250, 250, 0], "ix": 3}, "a": {"a": 0, "k": [250, 250, 0], "ix": 4}, "s": {"a": 0, "k": [100, 100, 100], "ix": 5}}, "ao": 0, "shapes": [
            {"ty": "gr", "it": [
                {"ind": 0, "ty": "rc", "d": 1, "s": {"a": 0, "k": [50, 150], "ix": 2}, "p": {"a": 0, "k": [150, 350], "ix": 3}, "r": {"a": 0, "k": 5, "ix": 4}, "mn": "ADBE Vector Shape - Rect", "hd": False},
                {"ty": "fl", "c": {"a": 0, "k": [0.2, 0.6, 0.8, 1], "ix": 5}, "o": {"a": 0, "k": 100, "ix": 6}, "r": 1, "mn": "ADBE Vector Fill", "hd": False}
            ], "nm": "Bar 1", "np": 2, "cix": 2, "ix": 1, "mn": "ADBE Vector Group", "hd": False},
            {"ty": "gr", "it": [
                {"ind": 0, "ty": "rc", "d": 1, "s": {"a": 0, "k": [50, 100], "ix": 2}, "p": {"a": 0, "k": [250, 400], "ix": 3}, "r": {"a": 0, "k": 5, "ix": 4}, "mn": "ADBE Vector Shape - Rect", "hd": False},
                {"ty": "fl", "c": {"a": 0, "k": [0.2, 0.6, 0.8, 1], "ix": 5}, "o": {"a": 0, "k": 100, "ix": 6}, "r": 1, "mn": "ADBE Vector Fill", "hd": False}
            ], "nm": "Bar 2", "np": 2, "cix": 2, "ix": 2, "mn": "ADBE Vector Group", "hd": False},
            {"ty": "gr", "it": [
                {"ind": 0, "ty": "rc", "d": 1, "s": {"a": 0, "k": [50, 200], "ix": 2}, "p": {"a": 0, "k": [350, 300], "ix": 3}, "r": {"a": 0, "k": 5, "ix": 4}, "mn": "ADBE Vector Shape - Rect", "hd": False},
                {"ty": "fl", "c": {"a": 0, "k": [0.2, 0.6, 0.8, 1], "ix": 5}, "o": {"a": 0, "k": 100, "ix": 6}, "r": 1, "mn": "ADBE Vector Fill", "hd": False}
            ], "nm": "Bar 3", "np": 2, "cix": 2, "ix": 3, "mn": "ADBE Vector Group", "hd": False}
        ], "ef": [], "ip": 0, "op": 120, "st": 0, "bm": 0}
    ], "markers": []
}

LOTTIE_FORECAST = {
    "v": "5.7.4", "fr": 60, "ip": 0, "op": 120, "w": 500, "h": 500, "nm": "Forecast",
    "ddd": 0, "assets": [], "layers": [
        {"ddd": 0, "ind": 0, "ty": 4, "nm": "Cloud", "sr": 1, "ks": {"o": {"a": 0, "k": 100, "ix": 1}, "r": {"a": 0, "k": 0, "ix": 2}, "p": {"a": 0, "k": [250, 150, 0], "ix": 3}, "a": {"a": 0, "k": [250, 150, 0], "ix": 4}, "s": {"a": 0, "k": [100, 100, 100], "ix": 5}}, "ao": 0, "shapes": [
            {"ty": "gr", "it": [
                {"ind": 0, "ty": "el", "d": 1, "s": {"a": 0, "k": [200, 100], "ix": 2}, "p": {"a": 0, "k": [0, 0], "ix": 3}, "mn": "ADBE Vector Shape - Ellipse", "hd": False},
                {"ty": "fl", "c": {"a": 0, "k": [0.6, 0.8, 1, 1], "ix": 4}, "o": {"a": 0, "k": 100, "ix": 5}, "r": 1, "mn": "ADBE Vector Fill", "hd": False}
            ], "nm": "Cloud Shape", "np": 2, "cix": 2, "ix": 1, "mn": "ADBE Vector Group", "hd": False}
        ], "ef": [], "ip": 0, "op": 120, "st": 0, "bm": 0},
        {"ddd": 0, "ind": 1, "ty": 4, "nm": "Arrow", "sr": 1, "ks": {"o": {"a": 0, "k": 100, "ix": 1}, "r": {"a": 0, "k": 0, "ix": 2}, "p": {"a": 0, "k": [250, 350, 0], "ix": 3}, "a": {"a": 0, "k": [250, 350, 0], "ix": 4}, "s": {"a": 0, "k": [100, 100, 100], "ix": 5}}, "ao": 0, "shapes": [
            {"ty": "gr", "it": [
                {"ind": 0, "ty": "sh", "ix": 1, "ks": {"a": 0, "k": {"i": [[0.833, 0.833], [0.833, 0.833]], "o": [[0.167, 0.167], [0.167, 0.167]], "v": [[250, 400], [250, 300]]}, "ix": 2}, "nm": "Path 1", "mn": "ADBE Vector Shape - Group", "hd": False},
                {"ty": "st", "c": {"a": 0, "k": [0.8, 0.2, 0.2, 1], "ix": 3}, "o": {"a": 0, "k": 100, "ix": 4}, "lw": {"a": 0, "k": 10, "ix": 5}, "lc": 1, "lj": 1, "ml": 4, "mn": "ADBE Vector Stroke", "hd": False}
            ], "nm": "Arrow Line", "np": 2, "cix": 2, "ix": 1, "mn": "ADBE Vector Group", "hd": False},
            {"ty": "gr", "it": [
                {"ind": 0, "ty": "sh", "ix": 1, "ks": {"a": 0, "k": {"i": [[0, 0], [0, 0], [0, 0]], "o": [[0, 0], [0, 0], [0, 0]], "v": [[250, 280], [240, 290], [260, 290]]}, "ix": 2}, "nm": "Path 1", "mn": "ADBE Vector Shape - Group", "hd": False},
                {"ty": "fl", "c": {"a": 0, "k": [0.8, 0.2, 0.2, 1], "ix": 3}, "o": {"a": 0, "k": 100, "ix": 4}, "r": 1, "mn": "ADBE Vector Fill", "hd": False}
            ], "nm": "Arrow Head", "np": 2, "cix": 2, "ix": 2, "mn": "ADBE Vector Group", "hd": False}
        ], "ef": [], "ip": 0, "op": 120, "st": 0, "bm": 0}
    ], "markers": []
}

# --- Utility Functions for Data Handling ---
def load_transactions(username=None):
    """Loads transactions from CSV. Filters by username if provided."""
    try:
        if not os.path.exists(TRANSACTIONS_FILE):
            return pd.DataFrame(columns=['username', 'date', 'type', 'category', 'amount', 'description'])
        df = pd.read_csv(TRANSACTIONS_FILE)
        if not {'username', 'date', 'type', 'category', 'amount', 'description'}.issubset(df.columns):
            st.error("CSV file is corrupted or missing required columns. Resetting data.")
            return pd.DataFrame(columns=['username', 'date', 'type', 'category', 'amount', 'description'])
        df['date'] = pd.to_datetime(df['date'], format=DATE_FORMAT, errors='coerce')
        df.dropna(subset=['date'], inplace=True)
        # Ensure amount is always float
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0.0)
        if username:
            return df[df['username'] == username].copy()
        return df
    except Exception as e:
        st.error(f"Error loading transactions: {str(e)}. Using empty dataset.")
        return pd.DataFrame(columns=['username', 'date', 'type', 'category', 'amount', 'description'])

def save_transaction(username, date, type, category, amount, description):
    """Appends a new transaction to the CSV file with file locking."""
    with filelock.FileLock(TRANSACTIONS_FILE + ".lock"):
        # Load all existing transactions
        if os.path.exists(TRANSACTIONS_FILE):
            df = pd.read_csv(TRANSACTIONS_FILE)
        else:
            df = pd.DataFrame(columns=['username', 'date', 'type', 'category', 'amount', 'description'])
        new_entry = pd.DataFrame([{
            'username': username,
            'date': date,
            'type': type,
            'category': category,
            'amount': float(amount) if amount is not None else 0.0,
            'description': description
        }])
        df = pd.concat([df, new_entry], ignore_index=True)
        df.to_csv(TRANSACTIONS_FILE, index=False)
        st.success("Transaction saved successfully.")

def load_users():
    """Loads user credentials from CSV."""
    try:
        if not os.path.exists(USERS_FILE):
            return pd.DataFrame(columns=['username', 'password'])
        return pd.read_csv(USERS_FILE)
    except Exception as e:
        st.error(f"Error loading users: {str(e)}. Using empty dataset.")
        return pd.DataFrame(columns=['username', 'password'])

def add_user(username, password):
    """Adds a new user to the CSV file."""
    with filelock.FileLock(USERS_FILE + ".lock"):
        df = load_users()
        if username in df['username'].values:
            return False
        new_user = pd.DataFrame([{'username': username, 'password': password}])
        df = pd.concat([df, new_user], ignore_index=True)
        df.to_csv(USERS_FILE, index=False)
        return True

def load_budgets(username=None):
    """Loads budgets from CSV. Filters by username if provided."""
    try:
        if not os.path.exists(BUDGETS_FILE):
            return pd.DataFrame(columns=['username', 'category', 'budget_amount'])
        df = pd.read_csv(BUDGETS_FILE)
        if not {'username', 'category', 'budget_amount'}.issubset(df.columns):
            st.error("Budget CSV is corrupted or missing required columns. Resetting data.")
            return pd.DataFrame(columns=['username', 'category', 'budget_amount'])
        if username:
            return df[df['username'] == username].copy()
        return df
    except Exception as e:
        st.error(f"Error loading budgets: {str(e)}. Using empty dataset.")
        return pd.DataFrame(columns=['username', 'category', 'budget_amount'])

def save_budget(username, category, budget_amount):
    """Saves or updates a budget for a category."""
    with filelock.FileLock(BUDGETS_FILE + ".lock"):
        df = load_budgets()
        df = df[~((df['username'] == username) & (df['category'] == category))]
        new_budget = pd.DataFrame([{
            'username': username,
            'category': category,
            'budget_amount': float(budget_amount) if budget_amount is not None else 0.0
        }])
        df = pd.concat([df, new_budget], ignore_index=True)
        df.to_csv(BUDGETS_FILE, index=False)

# --- Machine Learning Model Functions ---
def preprocess_data(df):
    """Preprocesses transaction data for ML model."""
    if df.empty:
        return pd.DataFrame()
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    if df['date'].isna().all():
        return pd.DataFrame()
    df = df.sort_values(by='date')
    daily_expenses = df[df['type'] == 'expense'].groupby('date')['amount'].sum().reset_index()
    if daily_expenses.empty:
        return pd.DataFrame()
    daily_expenses.columns = ['date', 'daily_expense']
    daily_expenses['year'] = daily_expenses['date'].dt.year
    daily_expenses['month'] = daily_expenses['date'].dt.month
    daily_expenses['day'] = daily_expenses['date'].dt.day
    daily_expenses['day_of_week'] = daily_expenses['date'].dt.dayofweek
    daily_expenses['day_of_year'] = daily_expenses['date'].dt.dayofyear
    for i in range(1, 8):
        daily_expenses[f'lag_{i}'] = daily_expenses['daily_expense'].shift(i)
    daily_expenses.dropna(inplace=True)
    return daily_expenses

def train_model(df, model_type='RandomForest'):
    """Trains a selected ML model on preprocessed expense data."""
    preprocessed_df = preprocess_data(df)
    if preprocessed_df.empty or len(preprocessed_df) < 10:
        return None, None, "Not enough historical data (at least 10 entries required) to train the model.", None
    features = [col for col in preprocessed_df.columns if 'lag_' in col or col in ['year', 'month', 'day', 'day_of_week', 'day_of_year']]
    target = 'daily_expense'
    if not features:
        return None, None, "No valid features could be created. Insufficient historical data.", None
    X = preprocessed_df[features]
    y = preprocessed_df[target]
    if len(X) < 2:
        return None, None, "Not enough samples for training after creating features.", None
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    model = None
    if model_type == 'RandomForest':
        model = RandomForestRegressor(n_estimators=100, random_state=42)
    elif model_type == 'SVM':
        model = SVR(kernel='rbf')
    else:
        return None, None, "Invalid model type specified.", None
    try:
        model.fit(X_train_scaled, y_train)
        y_pred = model.predict(X_test_scaled)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        return model, scaler, (mae, r2), features
    except Exception as e:
        return None, None, f"Error during model training: {str(e)}", None

def predict_future_expenses(model, scaler, historical_df, num_days=30, features=None):
    """Predicts future daily expenses using the trained model."""
    if model is None or scaler is None or features is None:
        return None, "Model, scaler, or features not provided."
    preprocessed_df = preprocess_data(historical_df)
    if preprocessed_df.empty or len(preprocessed_df) < 7:
        return None, "Not enough historical data (at least 7 days required) to generate future lags."
    latest_data = preprocessed_df.tail(1).copy()
    last_date = latest_data['date'].iloc[0]
    future_dates = [last_date + pd.Timedelta(days=i) for i in range(1, num_days + 1)]
    latest_lags = preprocessed_df[[f'lag_{i}' for i in range(1, 8)]].tail(1).values[0]
    predictions = []
    current_lags = latest_lags.tolist()
    for _ in range(num_days):
        input_dict = dict(zip([f'lag_{i}' for i in range(1, 8)], current_lags))
        input_dict['year'] = last_date.year
        input_dict['month'] = last_date.month
        input_dict['day'] = last_date.day
        input_dict['day_of_week'] = last_date.dayofweek
        input_dict['day_of_year'] = last_date.dayofyear
        # Ensure input_features has the same columns and order as features
        input_features = pd.DataFrame([{k: input_dict[k] for k in features}])
        input_scaled = scaler.transform(input_features)
        predicted_expense = model.predict(input_scaled)[0]
        predicted_expense = max(0, predicted_expense)
        predictions.append(predicted_expense)
        current_lags.pop(0)
        current_lags.append(predicted_expense)
        last_date += pd.Timedelta(days=1)
    return pd.DataFrame({'date': future_dates, 'predicted_expense': predictions}), None

# --- Streamlit Application ---
st.set_page_config(
    page_title="Personal Finance Tracker",
    page_icon="ð°",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.markdown(f"<style>{CUSTOM_CSS}</style>", unsafe_allow_html=True)

# --- Session State Management ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.current_page = "Dashboard"
if 'alerts' not in st.session_state:
    st.session_state.alerts = []

# --- User Authentication ---
def show_login_signup():
    """Displays login and sign-up forms in the sidebar."""
    st.sidebar.title("Welcome to Finance Tracker!")
    choice = st.sidebar.radio("Choose an option:", ["Login", "Sign Up"])
    if choice == "Login":
        with st.sidebar.form("Login_Form"):
            st.subheader("Login")
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            login_button = st.form_submit_button("Login")
            if login_button:
                users_df = load_users()
                user_match = users_df[(users_df['username'] == username) & (users_df['password'] == password)]
                if not user_match.empty:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success(f"Welcome back, {username}! ð")
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
    else:
        with st.sidebar.form("SignUp_Form"):
            st.subheader("Sign Up")
            new_username = st.text_input("New Username", key="signup_username")
            new_password = st.text_input("New Password", type="password", key="signup_password")
            signup_button = st.form_submit_button("Sign Up")
            if signup_button:
                if new_username and new_password:
                    if add_user(new_username, new_password):
                        st.success("Account created successfully! Please login.")
                    else:
                        st.error("Username already exists. Choose a different one.")
                else:
                    st.warning("Please enter both a username and a password.")

# --- Main Application Logic ---
if not st.session_state.logged_in:
    show_login_signup()
else:
    with st.sidebar:
        st.write(f"Logged in as: <b>{st.session_state.username}</b>", unsafe_allow_html=True)
        st.markdown("---")
        selected = option_menu(
            menu_title="Main Menu",
            options=["Dashboard", "Add Transaction", "Set Budget", "History", "Forecast", "Insights"],
            icons=["house", "currency-exchange", "piggy-bank", "clock-history", "graph-up", "lightbulb"],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "#f8f9fa"},
                "icon": {"color": "#4CAF50", "font-size": "20px"},
                "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px", "--hover-color": "#e2f0d6"},
                "nav-link-selected": {"background-color": "#4CAF50", "color": "white"},
            }
        )
        st.markdown("---")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.current_page = "Dashboard"
            st.session_state.alerts = []
            st.rerun()

    st.markdown("<h1 class='fade-in'>ð° Personal Finance Tracker</h1>", unsafe_allow_html=True)

    # --- Dashboard Page ---
    if selected == "Dashboard":
        st.header("Overview")
        current_transactions = load_transactions(st.session_state.username)
        budgets = load_budgets(st.session_state.username)
        if not current_transactions.empty:
            # Budget Alerts
            if not budgets.empty:
                for _, budget in budgets.iterrows():
                    category_spent = current_transactions[(current_transactions['category'] == budget['category']) & 
                                                         (current_transactions['type'] == 'expense')]['amount'].sum()
                    if category_spent > budget['budget_amount'] and budget['budget_amount'] > 0:
                        st.session_state.alerts.append(f"â ï¸ Budget exceeded for {budget['category']}: Spent â¹{category_spent:.2f} against â¹{budget['budget_amount']:.2f}")
            for alert in st.session_state.alerts:
                st.warning(alert)
            total_income = current_transactions[current_transactions['type'] == 'income']['amount'].sum()
            total_expenses = current_transactions[current_transactions['type'] == 'expense']['amount'].sum()
            net_balance = total_income - total_expenses
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label="Total Income ð", value=f"â¹{total_income:,.2f}")
            with col2:
                st.metric(label="Total Expenses ð", value=f"â¹{total_expenses:,.2f}")
            with col3:
                st.metric(label="Net Balance ð¼", value=f"â¹{net_balance:,.2f}")
            st.markdown("---")
            st.subheader("Spending Breakdown by Category")
            expense_by_category = current_transactions[current_transactions['type'] == 'expense'].groupby('category')['amount'].sum().reset_index()
            if not expense_by_category.empty:
                fig_pie = px.pie(expense_by_category, values='amount', names='category', title='Expense Distribution',
                                hole=0.3, color_discrete_sequence=px.colors.qualitative.Pastel)
                fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("No expenses to display breakdown.")
            st.subheader("Income vs. Expenses Over Time")
            daily_summary = current_transactions.groupby(['date', 'type'])['amount'].sum().unstack(fill_value=0).reset_index()
            daily_summary['net'] = daily_summary.get('income', 0) - daily_summary.get('expense', 0)
            fig_line = go.Figure()
            if 'income' in daily_summary.columns and not daily_summary['income'].isna().all():
                fig_line.add_trace(go.Scatter(x=daily_summary['date'], y=daily_summary['income'], mode='lines+markers', name='Income', line=dict(color='#28a745')))
            if 'expense' in daily_summary.columns and not daily_summary['expense'].isna().all():
                fig_line.add_trace(go.Scatter(x=daily_summary['date'], y=daily_summary['expense'], mode='lines+markers', name='Expenses', line=dict(color='#dc3545')))
            fig_line.update_layout(title='Daily Income vs. Expenses', xaxis_title='Date', yaxis_title='Amount (â¹)', 
                                 hovermode="x unified", template="plotly_white")
            st.plotly_chart(fig_line, use_container_width=True)
            st_lottie(LOTTIE_FINANCIAL_GROWTH, height=200, key="financial_growth_animation")
        else:
            st.info("No transactions yet. Add some to see your dashboard!")
            st_lottie(LOTTIE_DATA_ANALYSIS, height=200, key="no_data_dashboard")

    # --- Add Transaction Page ---
    elif selected == "Add Transaction":
        st.header("Add New Transaction")
        with st.form("transaction_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                transaction_type = st.radio("Transaction Type", ["Expense", "Income"], horizontal=True, key="transaction_type_radio")
            with col2:
                amount = st.number_input("Amount (â¹)", min_value=0.01, format="%.2f", step=0.01)
                date = st.date_input("Date", datetime.today())
                category = st.selectbox("Category", EXPENSE_CATEGORIES if transaction_type == "Expense" else INCOME_CATEGORIES, index=0, key="dynamic_category")
            description = st.text_area("Description").strip()
            submitted = st.form_submit_button("Add Transaction")
            if submitted:
                if amount <= 0:
                    st.error("Amount must be greater than zero.")
                else:
                    save_transaction(
                        username=st.session_state.username,
                        date=date.strftime(DATE_FORMAT),
                        type=transaction_type.lower(),
                        category=category,
                        amount=amount,
                        description=description
                    )
                    st.success(f"Transaction added: â¹{amount:.2f} ({transaction_type}) for {category} ð")
                    st.session_state.alerts.append(f"Added {transaction_type}: â¹{amount:.2f} for {category}")
                    st.rerun()

    # --- Set Budget Page ---
    elif selected == "Set Budget":
        st.header("ð¯ Set Budget")
        with st.form("budget_form", clear_on_submit=True):
            category = st.selectbox("Category", EXPENSE_CATEGORIES)
            budget_amount = st.number_input("Budget Amount (â¹)", min_value=0.01, format="%.2f", step=0.01)
            submit = st.form_submit_button("Set Budget")
            if submit:
                if budget_amount <= 0:
                    st.error("Budget amount must be greater than zero.")
                else:
                    save_budget(st.session_state.username, category, budget_amount)
                    st.success(f"Budget set for {category}: â¹{budget_amount:.2f} ð")
                    st.session_state.alerts.append(f"Budget set for {category}: â¹{budget_amount:.2f}")
                    st.rerun()

    # --- History Page ---
    elif selected == "History":
        st.header("Transaction History")
        current_transactions = load_transactions(st.session_state.username)
        if current_transactions.empty:
            st.info("No transaction history available.")
            st_lottie(LOTTIE_DATA_ANALYSIS, height=200, key="no_history_data")
        else:
            st.dataframe(current_transactions.sort_values(by='date', ascending=False).reset_index(drop=True), use_container_width=True)
            st.subheader("Filter and Analyze History")
            col1, col2 = st.columns(2)
            with col1:
                filter_type = st.selectbox("Filter by Type", ["All", "Expense", "Income"])
            with col2:
                all_categories = list(set(current_transactions['category'].tolist()))
                filter_category = st.selectbox("Filter by Category", ["All"] + all_categories)
            filtered_df = current_transactions.copy()
            if filter_type != "All":
                filtered_df = filtered_df[filtered_df['type'] == filter_type.lower()]
            if filter_category != "All":
                filtered_df = filtered_df[filtered_df['category'] == filter_category]
            st.dataframe(filtered_df.sort_values(by='date', ascending=False).reset_index(drop=True), use_container_width=True)

    # --- Forecast Page ---
    elif selected == "Forecast":
        st.header("Financial Forecasting")
        st.write("Predict your future expenses based on historical spending patterns.")
        current_transactions = load_transactions(st.session_state.username)
        expense_data = current_transactions[current_transactions['type'] == 'expense'].copy()
        # Check unique days in expense data
        unique_expense_days = expense_data['date'].nunique()
        if unique_expense_days < 17:
            st.warning(f"Not enough daily expense data (at least 17 unique days required, you have {unique_expense_days}). Add more daily entries to train a reliable forecasting model.")
            st_lottie(LOTTIE_FORECAST, height=200, key="no_forecast_data_animation")
        else:
            model_type = st.selectbox("Choose Forecasting Model", ["RandomForest", "SVM"])
            num_days_forecast = st.slider("Forecast for how many days?", 7, 90, 30)
            if st.button("Generate Forecast"):
                with st.spinner("Training model and generating forecast..."):
                    model, scaler, (mae, r2), features = train_model(expense_data, model_type=model_type)
                    if model is None:
                        st.error(f"Model training failed: {r2 if isinstance(r2, str) else 'Unknown error'}")
                    else:
                        forecast_df, predict_error = predict_future_expenses(model, scaler, expense_data, num_days=num_days_forecast, features=features)
                        if predict_error:
                            st.error(f"Error generating forecast: {predict_error}")
                        else:
                            st.subheader(f"Predicted Expenses for the Next {num_days_forecast} Days")
                            st.dataframe(forecast_df, use_container_width=True)
                            fig_forecast = px.line(forecast_df, x='date', y='predicted_expense',
                                                  title=f'Future Expense Prediction (MAE: {mae:.2f}, RÂ²: {r2:.2f})',
                                                  labels={'date': 'Date', 'predicted_expense': 'Predicted Expense (â¹)'},
                                                  color_discrete_sequence=['#ff7f0e'])
                            historical_daily_expenses = expense_data.groupby('date')['amount'].sum().reset_index()
                            fig_forecast.add_trace(go.Scatter(x=historical_daily_expenses['date'], y=historical_daily_expenses['amount'],
                                                            mode='lines', name='Historical Expenses', line=dict(color='#1f77b4')))
                            fig_forecast.update_layout(hovermode="x unified", template="plotly_white")
                            st.plotly_chart(fig_forecast, use_container_width=True)
                            st_lottie(LOTTIE_FORECAST, height=200, key="forecast_results_animation")

    # --- Insights Page ---
    elif selected == "Insights":
        st.header("Personalized Financial Insights")
        current_transactions = load_transactions(st.session_state.username)
        if current_transactions.empty:
            st.info("No data available to generate insights. Add transactions to get started!")
            st_lottie(LOTTIE_DATA_ANALYSIS, height=200, key="no_insights_data_animation")
        else:
            st.subheader("Spending Habits Analysis")
            monthly_expenses = current_transactions[current_transactions['type'] == 'expense'].copy()
            if not monthly_expenses.empty:
                monthly_expenses['month_year'] = monthly_expenses['date'].dt.to_period('M').astype(str)
                avg_monthly_expense = monthly_expenses.groupby('month_year')['amount'].sum().mean()
                st.markdown(f"Your average monthly spending is around <b>â¹{avg_monthly_expense:,.2f}</b>.", unsafe_allow_html=True)
            else:
                st.info("No expense data to analyze spending habits.")
            top_expense_categories = monthly_expenses.groupby('category')['amount'].sum().nlargest(3)
            if not top_expense_categories.empty:
                st.write("Your top 3 spending categories are:")
                for category, amount in top_expense_categories.items():
                    st.markdown(f"- <b>{category}</b>: â¹{amount:,.2f}", unsafe_allow_html=True)
                st.warning("Consider reviewing expenses in these categories for potential savings.")
            else:
                st.info("No top expense categories to display.")
            st.subheader("Saving Potential")
            total_income = current_transactions[current_transactions['type'] == 'income']['amount'].sum()
            total_expenses = current_transactions[current_transactions['type'] == 'expense']['amount'].sum()
            net_balance = total_income - total_expenses
            if net_balance > 0:
                st.markdown(f"<div style='color: #3c763d; background-color: #dff0d8; padding: 10px; border-radius: 5px;'>Great! You have a positive net balance of <b>â¹{net_balance:,.2f}</b>. Keep it up!</div>", unsafe_allow_html=True)
                st.write("Consider allocating surplus to savings or investments.")
            elif net_balance < 0:
                st.markdown(f"<div style='color: #dc3545; background-color: #f2dede; padding: 10px; border-radius: 5px;'>Your expenses exceed income by <b>â¹{abs(net_balance):,.2f}</b>.</div>", unsafe_allow_html=True)
                st.write("Identify areas to cut back by reviewing top expense categories.")
            else:
                st.info("Your income and expenses are balanced. Aim for a positive balance.")
            st.subheader("Life Insurance Suggestions")
            st.markdown(
                """
                <i>Disclaimer: This is a simplified suggestion and not professional financial advice. Consult a qualified advisor for personalized recommendations.</i>
                """, unsafe_allow_html=True
            )
            if total_income > 50000 and net_balance > 10000:
                st.markdown("<div style='color: #3c763d; background-color: #dff0d8; padding: 10px; border-radius: 5px;'>Based on your healthy income and savings, consider <b>term life insurance</b> for financial security.</div>", unsafe_allow_html=True)
                st.markdown("[Learn more about Term Life Insurance](https://www.investopedia.com/terms/t/termlife.asp)")
            elif total_expenses > total_income * 0.8 and total_income > 0:
                st.markdown("<div style='color: #8a6d3b; background-color: #fcf8e3; padding: 10px; border-radius: 5px;'>High expenses suggest building an emergency fund before considering <b>basic life coverage</b>.</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div style='color: #31708f; background-color: #d9edf7; padding: 10px; border-radius: 5px;'>Maintain a steady financial path and revisit insurance options later.</div>", unsafe_allow_html=True)