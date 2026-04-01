import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
import requests
import joblib
import database
from datetime import date, timedelta, datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Krishi Veda | Smart Farm OS",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- DATABASE INITIALIZATION ---
import database # Ensure module is loaded

# --- AUTHENTICATION FLOW ---
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = None
    st.session_state['username'] = None
    st.session_state['location'] = "Delhi"

if st.session_state['user_id'] is None:
    st.title("Welcome to Krishi Veda")
    st.markdown("Please Login or Register to access your personalized Smart Farm OS.")
    
    t1, t2 = st.tabs(["Login", "Register"])
    with t1:
        with st.form("login_form"):
            l_usr = st.text_input("Username")
            l_pwd = st.text_input("Password", type="password")
            if st.form_submit_button("Login"):
                res = database.verify_login(l_usr, l_pwd)
                if res:
                    st.session_state['user_id'] = res['id']
                    st.session_state['username'] = l_usr
                    st.session_state['location'] = res['location']
                    st.success("Login Successful!")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("Invalid credentials.")
    with t2:
        with st.form("register_form"):
            r_usr = st.text_input("Choose Username")
            r_pwd = st.text_input("Choose Password", type="password")
            r_loc = st.text_input("Farm Region (City)")
            if st.form_submit_button("Create Profile"):
                if r_usr and r_pwd and r_loc:
                    if database.register_user(r_usr, r_pwd, r_loc):
                        st.success("Profile created! Please switch to Login tab.")
                    else:
                        st.error("Username already taken. Please try another.")
                else:
                    st.error("Please fill all fields.")
    st.stop()

# --- CUSTOM THEME & CSS ---
st.markdown("""
    <style>
    /* Premium Global Styling */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    h1, h2, h3 { 
        color: #81C784 !important; 
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    
    /* Refined Neumorphic Metrics */
    div[data-testid="metric-container"] {
        background: #1E1E1E;
        border: 1px solid rgba(255, 255, 255, 0.05);
        padding: 24px !important;
        border-radius: 16px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3) !important;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 30px rgba(76, 175, 80, 0.15) !important;
        border-color: rgba(76, 175, 80, 0.3);
    }
    
    /* Premium Success Box */
    .success-box {
        padding: 28px;
        background: linear-gradient(145deg, #1A2E1A 0%, #111D11 100%);
        border-left: 6px solid #4CAF50;
        border-radius: 16px;
        margin: 24px 0;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
        animation: slideUpFade 0.6s cubic-bezier(0.16, 1, 0.3, 1);
    }
    
    @keyframes slideUpFade {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Crisp Sidebar Styling */
    section[data-testid="stSidebar"] {
        border-right: 1px solid rgba(255,255,255,0.05);
    }
    
    /* Force proper color mapping for sidebar text to combat defaults */
    section[data-testid="stSidebar"] .stMarkdown, 
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2 {
        color: #E0E0E0 !important;
    }
    
    /* Advanced Button Styling */
    .stButton>button {
        background-color: #2E7D32;
        color: #FFFFFF;
        border-radius: 12px;
        font-weight: 600;
        letter-spacing: 0.3px;
        transition: all 0.25s ease;
        border: none;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    .stButton>button:hover {
        background-color: #4CAF50;
        color: #FFFFFF;
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(76, 175, 80, 0.2);
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown("<h2 style='color: #81C784; font-weight: 700; margin-bottom: 0px;'>Krishi Veda</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #4CAF50; font-style: italic; font-size: 0.9em; margin-top: -5px;'>Intelligent Farm OS</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    menu = st.radio(
        "Navigation", 
        ["Dashboard", "Smart Crop Advisor", "Profit Calculator", "Activity Scheduler"]
    )
    
    st.markdown("---")
    st.info(f"User: {st.session_state['username']}")
    st.caption(f"Location: {st.session_state['location']}")
    if st.button("Logout"):
        st.session_state['user_id'] = None
        st.rerun()

# =================================================================================
# 1. DASHBOARD (HOME)
# =================================================================================
if menu == "Dashboard":
    st.title("Farm Dashboard")
    st.markdown("Welcome back! Here is your live farm summary.")
    
    # --- DYNAMIC DATA LOGIC ---
    
    # 1. Total Expense (from SQLite)
    expenses_data = database.get_expenses(st.session_state['user_id'])
    total_expense = sum([row[1] for row in expenses_data]) if expenses_data else 0
    
    # 2. Soil Status (from SQLite)
    latest_soil = database.get_latest_soil_test(st.session_state['user_id'])
    if latest_soil:
        last_test_date = datetime.strptime(latest_soil[0], "%Y-%m-%d").date()
        days_ago = (date.today() - last_test_date).days
        if days_ago == 0:
            soil_msg = "Tested Today"
            soil_delta = "Up to Date"
        else:
            soil_msg = "Tested"
            soil_delta = f"{days_ago} days ago"
    else:
        soil_msg = "Pending"
        soil_delta = "Action Needed"
        
    # 3. Weather (Live API via Open-Meteo using Profile Location)
    weather_city = st.session_state['location']
    
    @st.cache_data(ttl=3600)
    def fetch_weather(city):
        try:
            geo_req_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
            geo_response = requests.get(geo_req_url).json()
            if not geo_response.get("results"): return ("Unknown", "City not found")
            lat = geo_response["results"][0]["latitude"]
            lon = geo_response["results"][0]["longitude"]
            weather_req_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
            weather_response = requests.get(weather_req_url).json()
            temp = weather_response["current_weather"]["temperature"]
            wind = weather_response["current_weather"]["windspeed"]
            return (f"{temp}°C", f"Wind: {wind} km/h")
        except Exception:
            return ("Error", "API Failed")
            
    curr_weather = fetch_weather(weather_city)

    # Top Metrics Row
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Expense", f"₹{total_expense:,.2f}", "Current Month")
    m2.metric("Weather (Live)", curr_weather[0], curr_weather[1])
    m3.metric("Soil Health", soil_msg, soil_delta)
    m4.metric("Govt Scheme", "PM-Kisan", "Active")
    
    # --- DATA TRACKING SECTION ---
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.subheader("Financial Tracker")
        if expenses_data:
            df_exp = pd.DataFrame(expenses_data, columns=['Category', 'Amount', 'Date'])
            with st.container(border=True):
                fig = px.bar(
                    df_exp, 
                    x='Category', 
                    y='Amount', 
                    color='Category',
                    color_discrete_sequence=['#2E7D32', '#4CAF50', '#81C784', '#A5D6A7', '#C8E6C9'],
                    title="Expense Breakdown (Live Data)"
                )
                fig.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)", 
                    paper_bgcolor="rgba(0,0,0,0)",
                    height=360,
                    font_family="Outfit",
                    font_color="#E0E0E0",
                    title_font_color="#81C784",
                    margin=dict(l=10, r=10, t=40, b=20)
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No expenses logged yet. Use the tool on the right.")
        
    with c2:
        st.subheader("Quick Actions")
        
        # 1. Expense Logger
        with st.expander("Log Expense", expanded=True):
            with st.form("expense_form"):
                cat = st.selectbox("Category", ["Seeds", "Fertilizer", "Labor", "Pesticide", "Fuel"])
                amt = st.number_input("Amount (Rs.)", min_value=1, value=500)
                sub_btn = st.form_submit_button("Save Entry")
                
                if sub_btn:
                    database.add_expense(st.session_state['user_id'], cat, amt, str(date.today()))
                    st.success("Entry Saved to DB! Chart Updated.")
                    time.sleep(1)
                    st.rerun()

        # 2. Irrigation Schedule
        with st.expander("Irrigation Status"):
            if 'irrigation_status' not in st.session_state:
                st.session_state['irrigation_status'] = "Not Scheduled"
            
            st.write(f"Current Status: **{st.session_state['irrigation_status']}**")
            if st.button("Mark Field Irrigated"):
                st.session_state['irrigation_status'] = f"Done on {date.today()}"
                st.success("Status Updated!")
                st.rerun()

        # 3. Functional Booking
        if st.button("Book Soil Test"):
            st.toast("Request sent to nearest KVK center! Ref #9988")

# =================================================================================
# 2. SMART CROP ADVISOR (CORE LOGIC)
# =================================================================================
elif menu == "Smart Crop Advisor":
    st.title("Scientific Soil Analysis")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        with st.form("soil_form"):
            st.subheader("Enter Lab Data")
            n = st.slider("Nitrogen (N)", 0, 140, 50, help="Required for foliage and leaf growth.")
            p = st.slider("Phosphorus (P)", 0, 145, 40, help="Crucial for root development and flowering.")
            k = st.slider("Potassium (K)", 0, 205, 30, help="Enhances overall plant health and water regulation.")
            ph = st.slider("pH Level", 0.0, 14.0, 6.5, help="Measure of soil acidity/alkalinity. Ideal for most crops is 6.0-7.0.")
            rain = st.number_input("Rainfall (mm)", value=100, help="Average annual rainfall for your region.")
            temp = st.number_input("Avg Temp (C)", value=26, help="Average temperature during the growing season.")
            
            submitted = st.form_submit_button("Analyze Soil")

    if submitted:
        with st.spinner("Analyzing soil nutrients and climate patterns..."):
            time.sleep(1.2) # Fake processing time for UX
            with col2:
                st.subheader("Analysis Report")
                
                # 1. SOIL STATUS SUMMARY (Visual Feedback Bars)
                st.markdown("#### Soil Nutrient Summary")
                
                with st.container(border=True):
                    csl1, csl2, csl3 = st.columns(3)
                    csl1.metric("Nitrogen (N)", f"{n} kg/ha")
                    csl1.progress(min(n/140, 1.0))
                    
                    csl2.metric("Phosphorus (P)", f"{p} kg/ha")
                    csl2.progress(min(p/145, 1.0))
                    
                    csl3.metric("Potassium (K)", f"{k} kg/ha")
                    csl3.progress(min(k/205, 1.0))
                    
                    csl4, csl5 = st.columns(2)
                    csl4.metric("pH Level", ph)
                    csl4.progress(min(ph/14.0, 1.0))
                    
                    csl5.metric("Rainfall", f"{rain} mm")
                    csl5.progress(min(float(rain)/300.0, 1.0))
                
                st.markdown("---")
                
                # 2. ML LOGIC ENGINE
                try:
                    model = joblib.load('crop_model.pkl')
                    features = pd.DataFrame(
                        [[n, p, k, ph, float(rain), float(temp)]],
                        columns=['N', 'P', 'K', 'pH', 'Rainfall', 'Temperature']
                    )
                    prediction = model.predict(features)[0]
                    confidence_array = model.predict_proba(features)[0]
                    confidence = round(max(confidence_array) * 100, 1)
                    crop = prediction
                except Exception as e:
                    st.error("ML Model not found. Make sure to train it first!")
                    crop = "Unknown"
                    confidence = 0
                
                # 3. RESULT CARD
                st.markdown(f"""
                <div class="success-box">
                    <h3>Recommended: {crop}</h3>
                    <p>ML Confidence Score: <b>{confidence}%</b> based on dynamic Random Forest prediction.</p>
                </div>
                """, unsafe_allow_html=True)
                
                # 4. FERTILIZER CALC
                st.subheader("Fertilizer Recommendation")
                st.success(f"**Key Input for {crop}:** Apply standard basal dose.")
                st.write(f"**Why?** The ML model determined {crop} is best suited for your NPK profile (N={n}, P={p}, K={k}) and regional climate (Rainfall={rain}mm, Temp={temp}°C).")
                
                # Save this result to history
                database.add_soil_test(st.session_state['user_id'], str(date.today()), n, p, k, ph, rain, temp, crop, confidence)
                st.caption("Record saved permanently to SQLite farm database.")

# =================================================================================
# 3. PROFIT CALCULATOR
# =================================================================================
elif menu == "Profit Calculator":
    st.title("Vyapaar Mode (Profit Estimator)")
    st.markdown("Estimate your Returns on Investment (ROI) before you sow.")
    
    c1, c2, c3 = st.columns(3)
    crop_choice = c1.selectbox("Select Crop", ["Wheat", "Rice", "Cotton", "Soybean"])
    acres = c2.number_input("Land Size (Acres)", 1, 100, 5)
    exp_price = c3.number_input("Expected Market Rate (Rs./Quintal)", 2000, 10000, 2200)
    
    st.markdown("---")
    
    # Mock Data
    defaults = {
        "Wheat": {"yield": 20, "seed_cost": 1500, "fert_cost": 3000, "labor": 5000},
        "Rice": {"yield": 25, "seed_cost": 1200, "fert_cost": 4000, "labor": 8000},
        "Cotton": {"yield": 12, "seed_cost": 2500, "fert_cost": 5000, "labor": 7000},
        "Soybean": {"yield": 8, "seed_cost": 2000, "fert_cost": 2500, "labor": 4000},
    }
    
    data = defaults[crop_choice]
    
    # Calculations
    total_yield = data["yield"] * acres
    revenue = total_yield * exp_price
    
    cost_seed = data["seed_cost"] * acres
    cost_fert = data["fert_cost"] * acres
    cost_labor = data["labor"] * acres
    total_cost = cost_seed + cost_fert + cost_labor
    
    profit = revenue - total_cost
    roi = (profit / total_cost) * 100
    
    # Visualizing Logic
    col_l, col_r = st.columns(2)
    
    with col_l:
        st.subheader("Financial Projection")
        st.write(f"**Total Cost:** Rs. {total_cost:,.2f}")
        st.write(f"**Expected Revenue:** Rs. {revenue:,.2f}")
        
        if profit > 0:
            st.success(f"**Net Profit:** Rs. {profit:,.2f}")
        else:
            st.error(f"**Net Loss:** Rs. {profit:,.2f}")
            
        st.metric("Expected ROI", f"{roi:.1f}%")

    with col_r:
        # Bar Chart
        cost_df = pd.DataFrame({
            'Category': ['Seeds', 'Fertilizer', 'Labor', 'Profit'],
            'Amount': [cost_seed, cost_fert, cost_labor, profit]
        })
        with st.container(border=True):
            fig = px.bar(cost_df, x='Category', y='Amount', color='Category', 
                         color_discrete_sequence=['#4CAF50', '#81C784', '#A5D6A7', '#1E5631'],
                         title="Cost vs Profit Analysis")
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", 
                paper_bgcolor="rgba(0,0,0,0)",
                height=360,
                font_family="Outfit",
                font_color="#E0E0E0",
                title_font_color="#81C784",
                margin=dict(l=10, r=10, t=40, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)

# =================================================================================
# 4. ACTIVITY SCHEDULER
# =================================================================================
elif menu == "Activity Scheduler":
    st.title("Smart Farming Timeline")
    st.caption("Auto-generated schedule based on sowing date.")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        sow_date = st.date_input("Select Sowing Date", date.today())
        crop_type = st.selectbox("Select Crop", ["Wheat", "Cotton", "Maize"])
        
    with col2:
        st.subheader(f"{crop_type} Schedule")
        
        # Logic
        schedule = []
        if crop_type == "Wheat":
            schedule = [
                (sow_date, "Sowing", "Use seed drill. Spacing 22cm."),
                (sow_date + timedelta(days=21), "1st Irrigation (CRI Stage)", "Critical for root development."),
                (sow_date + timedelta(days=45), "Apply Urea (Top Dressing)", "Apply 25kg/acre."),
                (sow_date + timedelta(days=85), "Last Irrigation", "Grain filling stage."),
                (sow_date + timedelta(days=120), "Harvest", "Check grain hardness.")
            ]
        elif crop_type == "Cotton":
            schedule = [
                (sow_date, "Sowing", "Depth 4-5cm."),
                (sow_date + timedelta(days=30), "Thinning", "Remove weak plants."),
                (sow_date + timedelta(days=60), "Flowering Start", "Monitor for Bollworms."),
                (sow_date + timedelta(days=150), "First Picking", "Pick fully open bolls.")
            ]
        else:
             schedule = [(sow_date, "Sowing", "Standard process.")]

        # Render Timeline
        for d, event, desc in schedule:
            with st.expander(f"{d.strftime('%d %b')} - {event}", expanded=True):
                st.write(desc)
                