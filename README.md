# 🚚 Streamlit Delivery Route Optimizer

This project features an interactive Delivery Route Optimization Dashboard built using Streamlit and Python, designed to help businesses minimize fuel costs and reduce total travel distance through intelligent route optimization.

# 🔍 What It Does

The app allows users to quickly estimate fuel cost savings achieved by optimizing delivery routes across multiple drivers.

It provides instant insights into:

💰 Fuel Cost Savings

🧭 Optimized Multi-Driver Routing

📊 Baseline vs Optimized Distance Comparison

🚦 Operational Efficiency Metrics

# ⚙️ How It Works

The application uses a Greedy Routing Algorithm that assigns each delivery stop to the nearest available driver, minimizing the overall route distance.

It also includes:

📍 Great-Circle Distance Calculation for accurate distance measurement

🌍 Free Geocoding with OpenStreetMap (Nominatim) — no paid APIs required

💵 Cost Savings Calculator based on user-input Fuel Price and Average MPG

# 🧰 Tools & Technologies Used

Python – Core programming language

Streamlit – Interactive web dashboard framework

geopy – Geocoding and distance calculation

requests – API handling for geolocation lookups

# 📸 Dashboard Preview

Delivery Route Optimizer Dashboard

<img width="1706" height="873" alt="image" src="https://github.com/user-attachments/assets/a703956b-9cf3-4dfb-8d95-ff6c1463f537" />


<img width="1447" height="862" alt="image" src="https://github.com/user-attachments/assets/5fa9c99d-c85b-4c25-9fcc-4b7deff9b43f" />


<img width="1511" height="846" alt="image" src="https://github.com/user-attachments/assets/f3159cd9-375c-4d5e-8597-d98a1575dd87" />


# 📂 Files Included

app.py – Main Streamlit application code

requirements.txt – Python dependencies

dashboard_screenshot

# 🧠 Skills Demonstrated

Data Visualization using Streamlit

Optimization Algorithms (Greedy Approach)

Geocoding & Distance Computation

Analytical Thinking & ROI Estimation

Building Zero-Cost Proof-of-Concept Apps

# 📌 Use Case

This dashboard is ideal for:

🚛 Delivery Managers looking to optimize logistics costs

📈 Business Analysts validating ROI from route optimization

🧮 Data Engineers or Developers exploring POC projects in logistics analytics

It serves as a zero-cost, quick-deployment prototype for organizations aiming to evaluate the financial benefits of optimized delivery routes before investing in enterprise routing solutions.

# 🚀 How to Run the App

1️⃣ Install Prerequisites
Make sure Python 3.7+ is installed.

2️⃣ Install Dependencies

pip install streamlit geopy requests

3️⃣ Run the App

streamlit run app.py

Your browser will automatically open the Delivery Route Optimizer Dashboard 🌍

# 🗺️ Future Enhancements

    🔁 Integration with Google Maps API or OpenRouteService for real-world routing

    🧮 Incorporation of advanced optimization algorithms (e.g., OR-Tools, Genetic Algorithms)

    🗂️ Exporting reports in CSV or PDF format

    🗾 Interactive map visualization using folium
