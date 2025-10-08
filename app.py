import streamlit as st
import time
from geopy.geocoders import Nominatim
from geopy.distance import great_circle
import requests
from requests.exceptions import RequestException, Timeout
from geopy.exc import GeocoderUnavailable, GeocoderTimedOut

# --- 1. Configuration & Caching ---

@st.cache_data(show_spinner=True)
def geocode_address(address: str, max_retries: int = 3) -> tuple[float, float] | None:
    """Geocodes an address using OpenStreetMap Nominatim with retries."""
    geolocator = Nominatim(user_agent="vjo_route_optimizer_prototype")
    
    for attempt in range(max_retries):
        try:
            location = geolocator.geocode(address, timeout=10)
            if location:
                return (location.latitude, location.longitude)
        except (GeocoderUnavailable, GeocoderTimedOut, RequestException) as e:
            wait_time = 2 ** attempt
            time.sleep(wait_time) 
    
    return None

def calculate_distance(coords1: tuple, coords2: tuple) -> float:
    """Calculates the straight-line (Great-Circle) distance between two sets of coordinates in miles."""
    return great_circle(coords1, coords2).miles

# --- 2. Route Optimization Algorithm (Greedy) ---

def optimize_routes(start_coords: tuple, deliveries: list[dict], num_drivers: int) -> list[list[dict]]:
    """
    A greedy algorithm to optimize delivery routes by repeatedly assigning the nearest
    unassigned delivery to the closest driver's current last stop.
    """
    if not deliveries or num_drivers <= 0:
        return []

    # 1. Initialize routes for the specified number of drivers
    routes = [[{'address': "Start Location", 'coords': start_coords}] for _ in range(num_drivers)]
    unassigned_deliveries = deliveries.copy()
    
    # 2. Assign all deliveries
    while unassigned_deliveries:
        best_driver_index = -1
        best_delivery_index = -1
        min_distance = float('inf')
        
        # Find the best combination: Driver + Delivery
        for driver_index, route in enumerate(routes):
            last_stop_coords = route[-1]['coords']
            for delivery_index, delivery in enumerate(unassigned_deliveries):
                # Calculate distance from the driver's last stop to the new delivery
                current_distance = calculate_distance(last_stop_coords, delivery['coords'])
                
                if current_distance < min_distance:
                    min_distance = current_distance
                    best_driver_index = driver_index
                    best_delivery_index = delivery_index
        
        # Assign the closest delivery to the best driver
        if best_driver_index != -1:
            best_delivery = unassigned_deliveries.pop(best_delivery_index)
            routes[best_driver_index].append(best_delivery)
        else:
            # Should not happen if unassigned_deliveries is not empty
            break

    return routes

# --- 3. Streamlit App UI ---

def app_v1():
    """Main function for the V1 Prototype application."""
    st.title("🚚 Delivery Route Optimizer & Cost Analyzer ")
    st.markdown("Assign deliveries and calculate potential **fuel cost savings** using a multi-driver optimization model based on straight-line distance.")
    st.markdown("---")
    
    st.sidebar.header("Input Parameters")
    
    # Core Routing Inputs
    start_address_input = st.sidebar.text_input("**Enter Start Address**", "")
    delivery_addresses_input = st.sidebar.text_area(
        "**Enter Delivery Addresses (one address per line)**", 
        ""
    )

    st.sidebar.markdown("---")
    
    # Driver Inputs
    num_drivers_total = st.sidebar.number_input("**Total available drivers**", min_value=1, value=5, step=1)
    num_drivers_to_send = st.sidebar.number_input("**Number of drivers to send**", min_value=1, value=3, step=1)
    
    # Fuel/Cost Inputs (NEW)
    st.sidebar.markdown("### Cost Analysis")
    fuel_price_per_gallon = st.sidebar.number_input("Fuel price per gallon ($)", min_value=0.01, value=4.00, step=0.10)
    avg_mpg = st.sidebar.number_input("Average MPG", min_value=1.0, value=25.0, step=1.0)
    
    # Validation for Driver Count
    if num_drivers_to_send > num_drivers_total:
        st.sidebar.error("Drivers to send cannot exceed total available.")
        num_drivers_to_send = num_drivers_total 

    if st.sidebar.button("Calculate Routes & Costs"):
        if not start_address_input or not delivery_addresses_input:
            st.error("Please enter a start address and delivery addresses.")
            st.stop()
        if avg_mpg <= 0:
            st.error("Average MPG must be greater than zero for cost calculation.")
            st.stop()

        # --- Geocoding ---
        with st.spinner("1. Geocoding addresses..."):
            st.subheader("1. Geocoding Results")
            start_coords = geocode_address(start_address_input)
            if not start_coords:
                st.error(f"Could not geocode start address: {start_address_input}")
                st.stop()
            st.success("Start address geocoded.")

            raw_deliveries = [addr.strip() for addr in delivery_addresses_input.split('\n') if addr.strip()]
            deliveries = []
            
            for address in raw_deliveries:
                coords = geocode_address(address)
                if coords:
                    deliveries.append({'address': address, 'coords': coords})
                else:
                    st.warning(f"Skipping delivery: Could not geocode '{address}'.")
            
            if not deliveries:
                st.error("No valid delivery addresses could be geocoded.")
                st.stop()
            st.success(f"Successfully geocoded {len(deliveries)} out of {len(raw_deliveries)} deliveries.")

        # --- Baseline Calculation (Unoptimized Single Driver) ---
        st.subheader("2. Unoptimized Baseline (Single Driver)")
        unoptimized_distance = 0
        current_location = start_coords
        
        # Calculate sequential distance: Start -> D1 -> D2 -> ... -> Dn
        for delivery in deliveries:
            unoptimized_distance += calculate_distance(current_location, delivery['coords'])
            current_location = delivery['coords']
        
        unoptimized_fuel_cost = (unoptimized_distance / avg_mpg) * fuel_price_per_gallon
        st.write(f"**Baseline Total Distance (Sequential):** {unoptimized_distance:.2f} miles")
        st.write(f"**Baseline Total Fuel Cost:** ${unoptimized_fuel_cost:.2f}")

        # --- Route Optimization & Calculation ---
        st.subheader(f"3. Optimized Routes for {num_drivers_to_send} Driver(s)")
        optimized_routes = optimize_routes(start_coords, deliveries, num_drivers_to_send)
        
        total_optimized_distance = 0
        
        for i, route in enumerate(optimized_routes):
            if len(route) == 1:
                st.info(f"Driver {i+1} has no assigned deliveries.")
                continue

            st.markdown(f"### 🚗 Driver {i+1} Route Details")
            route_distance = 0
            current_stop_coords = route[0]['coords']
            
            st.markdown(f"**Start:** {route[0]['address']}")
            
            for j, stop in enumerate(route[1:]):
                distance_to_next = calculate_distance(current_stop_coords, stop['coords'])
                route_distance += distance_to_next
                
                st.markdown(f"-> **Stop {j+1}:** {stop['address']} (Distance from previous: **{distance_to_next:.2f} miles**)")
                current_stop_coords = stop['coords'] 
            
            total_optimized_distance += route_distance
            st.success(f"**Total distance for Driver {i+1}: {route_distance:.2f} miles**")
            st.markdown("---")

        # --- Final Summary & Savings (AS REQUESTED) ---
        st.header("4. Summary & Savings 💰")

        optimized_fuel_cost = (total_optimized_distance / avg_mpg) * fuel_price_per_gallon
        
        distance_saved = unoptimized_distance - total_optimized_distance
        fuel_cost_saved = unoptimized_fuel_cost - optimized_fuel_cost
        
        st.metric(
            label="Total Optimized Distance",
            value=f"{total_optimized_distance:.2f} miles",
            delta=f"-{distance_saved:.2f} miles saved" if distance_saved > 0 else "0 miles saved",
            delta_color="normal" if distance_saved > 0 else "off"
        )
        
        st.metric(
            label="Total Optimized Fuel Cost",
            value=f"${optimized_fuel_cost:.2f}",
            delta=f"-${fuel_cost_saved:.2f} saved" if fuel_cost_saved > 0 else "$0 saved",
            delta_color="normal" if fuel_cost_saved > 0 else "off"
        )
        
        st.info(
            f"This routing plan uses **{num_drivers_to_send}** out of **{num_drivers_total}** available drivers to complete all deliveries."
        )

if __name__ == '__main__':
    app_v1()