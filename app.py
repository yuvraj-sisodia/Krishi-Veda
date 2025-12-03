import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
import random
from datetime import date, timedelta

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Krishi Veda | Smart Farm OS",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- SESSION STATE INITIALIZATION ---
if 'expenses' not in st.session_state:
    st.session_state['expenses'] = pd.DataFrame([
        {'Category': 'Seeds', 'Amount': 2000, 'Date': date.today() - timedelta(days=5)},
        {'Category': 'Fertilizer', 'Amount': 1500, 'Date': date.today() - timedelta(days=2)},
        {'Category': 'Labor', 'Amount': 500, 'Date': date.today()}
    ])

if 'soil_history' not in st.session_state:
    st.session_state['soil_history'] = []

# --- CUSTOM THEME & CSS ---
st.markdown("""
    <style>
    /* Global Styles */
    h1, h2, h3 { 
        color: #2E7D32 !important; 
        font-family: 'Segoe UI', sans-serif; 
    }
    
    /* Metrics Styling */
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        color: #333333; /* Force dark text for metrics */
    }
    
    /* Custom Success Box */
    .success-box {
        padding: 20px;
        background-color: #e8f5e9;
        border-left: 5px solid #2e7d32;
        border-radius: 5px;
        margin-bottom: 20px;
        color: #1b5e20; /* Force dark green text */
    }
    .success-box h3 {
        margin-top: 0;
        color: #1b5e20 !important;
    }
    .success-box p {
        color: #2e7d32 !important;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #1b5e20;
    }
    
    /* Force white text for all sidebar elements */
    section[data-testid="stSidebar"] .stMarkdown, 
    section[data-testid="stSidebar"] .stRadio label,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown("## Krishi Veda")
    st.markdown("*Intelligent Farm OS*")
    st.markdown("---")
    
    menu = st.radio(
        "Navigation", 
        ["Dashboard", "Smart Crop Advisor", "Profit Calculator", "Activity Scheduler"]
    )
    
    st.markdown("---")
    st.info("Status: System Online")
    st.caption("v3.0.0 | Build: Ind-Agri")

# =================================================================================
# 1. DASHBOARD (HOME)
# =================================================================================
if menu == "Dashboard":
    st.title("Farm Dashboard")
    st.markdown("Welcome back! Here is your live farm summary.")
    
    # --- DYNAMIC DATA LOGIC ---
    
    # 1. Total Expense
    total_expense = st.session_state['expenses']['Amount'].sum()
    
    # 2. Soil Status
    if st.session_state['soil_history']:
        last_test = st.session_state['soil_history'][-1]['Date']
        days_ago = (date.today() - last_test).days
        if days_ago == 0:
            soil_msg = "Tested Today"
            soil_delta = "Up to Date"
        else:
            soil_msg = "Tested"
            soil_delta = f"{days_ago} days ago"
    else:
        soil_msg = "Pending"
        soil_delta = "Action Needed"
        
    # 3. Weather (Simulated)
    weather_options = [
        ("Clear Sky", "No Rain Expected"),
        ("Cloudy", "High Humidity (80%)"),
        ("Light Rain", "Irrigation Not Needed"),
        ("Windy", "15 km/h North")
    ]
    curr_weather = random.choice(weather_options)

    # Top Metrics Row
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Expense", f"Rs. {total_expense}", "This Month")
    m2.metric("Weather (Live)", curr_weather[0], curr_weather[1])
    m3.metric("Soil Health", soil_msg, soil_delta)
    m4.metric("Govt Scheme", "PM-Kisan", "Active")
    
    # --- DATA TRACKING SECTION ---
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.subheader("Financial Tracker")
        if not st.session_state['expenses'].empty:
            fig = px.bar(
                st.session_state['expenses'], 
                x='Category', 
                y='Amount', 
                color='Category',
                title="Expense Breakdown (Live Data)",
                text='Amount'
            )
            fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", height=350)
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
                    new_entry = pd.DataFrame([{'Category': cat, 'Amount': amt, 'Date': date.today()}])
                    st.session_state['expenses'] = pd.concat([st.session_state['expenses'], new_entry], ignore_index=True)
                    st.success("Entry Saved! Chart Updated.")
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
            n = st.slider("Nitrogen (N)", 0, 140, 50)
            p = st.slider("Phosphorus (P)", 0, 145, 40)
            k = st.slider("Potassium (K)", 0, 205, 30)
            ph = st.slider("pH Level", 0.0, 14.0, 6.5)
            rain = st.number_input("Rainfall (mm)", value=100)
            temp = st.number_input("Avg Temp (C)", value=26)
            
            submitted = st.form_submit_button("Analyze Soil")

    if submitted:
        with col2:
            st.subheader("Analysis Report")
            
            # 1. SOIL STATUS SUMMARY (Text Output)
            st.markdown("#### Soil Nutrient Summary")
            st.write("Here is the breakdown of your field's current status:")
            
            c1, c2, c3 = st.columns(3)
            c1.info(f"**Nitrogen:** {n}")
            c2.info(f"**Phosphorus:** {p}")
            c3.info(f"**Potassium:** {k}")
            
            c4, c5 = st.columns(2)
            c4.warning(f"**pH Level:** {ph}")
            c5.warning(f"**Rainfall:** {rain} mm")
            
            st.markdown("---")
            
            # 2. LOGIC ENGINE
            crop = ""
            confidence = 0
            
            if rain > 150 and temp > 20:
                crop = "Rice (Paddy)"
                confidence = 92
            elif 21 <= temp <= 35 and n > 70:
                crop = "Cotton"
                confidence = 88
            elif temp < 25 and 20 <= rain <= 100:
                crop = "Wheat"
                confidence = 95
            elif 18 <= temp <= 30 and rain > 50:
                crop = "Maize"
                confidence = 85
            else:
                crop = "Millets"
                confidence = 90
            
            # 3. RESULT CARD
            st.markdown(f"""
            <div class="success-box">
                <h3>Recommended: {crop}</h3>
                <p>AI Confidence Score: <b>{confidence}%</b> based on NPK signature.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # 4. FERTILIZER CALC
            st.subheader("Fertilizer Recommendation")
            st.success(f"**Key Input for {crop}:** Apply 2 bags Urea and 1 bag DAP per acre.")
            st.write(f"**Why?** {crop} requires this specific balance to boost growth in your soil conditions (N={n}, P={p}).")
            
            # Save this result to history
            st.session_state['soil_history'].append({'Date': date.today(), 'Crop': crop, 'Confidence': confidence})
            st.caption(f"Record saved to session history. Total records: {len(st.session_state['soil_history'])}")

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
        fig = px.bar(cost_df, x='Category', y='Amount', color='Category', title="Cost vs Profit Analysis")
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
                