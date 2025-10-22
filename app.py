import streamlit as st
import time
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from geopy.distance import great_circle
from requests.exceptions import RequestException
from geopy.exc import GeocoderUnavailable, GeocoderTimedOut

# --- 1. Configuration & Caching --- #

@st.cache_data(show_spinner=True)
def geocode_address(address: str, max_retries: int = 3) -> tuple[float, float] | None:
    """Geocodes an address using OpenStreetMap Nominatim with retries and rate limiting."""
    #  unique and compliant user_agent + rate limit to avoid blocking on Cloud
    geolocator = Nominatim(user_agent="vjo_route_optimizer_demo@example.com", timeout=10)
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)  # 1 req/sec required by OSM

    for attempt in range(max_retries):
        try:
            location = geocode(address)
            if location:
                return (location.latitude, location.longitude)
        except (GeocoderUnavailable, GeocoderTimedOut, RequestException):
            wait_time = 2 ** attempt
            time.sleep(wait_time)
    return None


def calculate_distance(coords1: tuple, coords2: tuple) -> float:
    """Calculates straight-line (great-circle) distance between two coordinates in miles."""
    return great_circle(coords1, coords2).miles


# --- 2. Route Optimization Algorithm (Greedy) --- #

def optimize_routes(start_coords: tuple, deliveries: list[dict], num_drivers: int) -> list[list[dict]]:
    """
    Greedy delivery optimization - assigns each unassigned stop to the nearest driver's latest stop.
    """
    if not deliveries or num_drivers <= 0:
        return []

    routes = [[{'address': "Start Location", 'coords': start_coords}] for _ in range(num_drivers)]
    unassigned_deliveries = deliveries.copy()

    while unassigned_deliveries:
        best_driver_index = -1
        best_delivery_index = -1
        min_distance = float('inf')

        for driver_index, route in enumerate(routes):
            last_coords = route[-1]['coords']
            for delivery_index, delivery in enumerate(unassigned_deliveries):
                dist = calculate_distance(last_coords, delivery['coords'])
                if dist < min_distance:
                    min_distance = dist
                    best_driver_index = driver_index
                    best_delivery_index = delivery_index

        if best_driver_index != -1:
            best_delivery = unassigned_deliveries.pop(best_delivery_index)
            routes[best_driver_index].append(best_delivery)
        else:
            break

    return routes


# --- 3. Streamlit App --- #

def app_v1():
    """Streamlit-based Delivery Route Optimizer & Cost Estimator prototype."""
    st.title("🚚 Delivery Route Optimizer & Cost Analyzer")
    st.markdown(
        "Optimize routes, assign deliveries, and estimate **fuel cost savings** with multi-driver path optimization."
    )
    st.markdown("---")

    # Sidebar inputs
    st.sidebar.header("Input Parameters")

    start_address_input = st.sidebar.text_input("**Enter Start Address**", "")
    delivery_addresses_input = st.sidebar.text_area(
        "**Enter Delivery Addresses (one per line)**", ""
    )

    st.sidebar.markdown("---")

    # Drivers
    num_drivers_total = st.sidebar.number_input("**Total available drivers**", min_value=1, value=5)
    num_drivers_to_send = st.sidebar.number_input("**Number of drivers to send**", min_value=1, value=3)

    st.sidebar.markdown("### Cost Analysis")
    fuel_price_per_gallon = st.sidebar.number_input("Fuel price per gallon ($)", min_value=0.01, value=4.00)
    avg_mpg = st.sidebar.number_input("Average MPG", min_value=1.0, value=25.0)

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
            st.subheader("1️⃣ Geocoding Results")
            start_coords = geocode_address(start_address_input)
            if not start_coords:
                st.error(f"Could not geocode start address: {start_address_input}")
                st.stop()
            st.success("Start address geocoded successfully.")

            raw_deliveries = [addr.strip() for addr in delivery_addresses_input.split('\n') if addr.strip()]
            deliveries = []
            for address in raw_deliveries:
                coords = geocode_address(address)
                if coords:
                    deliveries.append({'address': address, 'coords': coords})
                else:
                    st.warning(f"Skipping '{address}' — could not geocode.")
                    time.sleep(1)

            if not deliveries:
                st.error("No valid delivery addresses were geocoded.")
                st.stop()
            st.success(f"Successfully geocoded {len(deliveries)} of {len(raw_deliveries)} addresses.")

        # --- Baseline Single Route ---
        st.subheader("2️⃣ Unoptimized Baseline (Single Driver)")
        total_distance_unoptimized = 0
        current_loc = start_coords

        for d in deliveries:
            total_distance_unoptimized += calculate_distance(current_loc, d['coords'])
            current_loc = d['coords']

        total_cost_unoptimized = (total_distance_unoptimized / avg_mpg) * fuel_price_per_gallon
        st.write(f"**Distance:** {total_distance_unoptimized:.2f} miles")
        st.write(f"**Fuel Cost:** ${total_cost_unoptimized:.2f}")

        # --- Optimized Routes ---
        st.subheader(f"3️⃣ Optimized Routes for {num_drivers_to_send} Driver(s)")
        optimized_routes = optimize_routes(start_coords, deliveries, num_drivers_to_send)
        total_distance_optimized = 0

        for i, route in enumerate(optimized_routes):
            if len(route) == 1:
                st.info(f"Driver {i+1} has no assigned deliveries.")
                continue

            st.markdown(f"#### 🚗 Driver {i+1} Route")
            route_distance = 0
            cur_stop = route[0]['coords']

            for j, stop in enumerate(route[1:]):
                d = calculate_distance(cur_stop, stop['coords'])
                route_distance += d
                st.markdown(f"→ Stop {j+1}: {stop['address']} ({d:.2f} miles)")
                cur_stop = stop['coords']
            total_distance_optimized += route_distance
            st.success(f"Total distance: {route_distance:.2f} miles")
            st.markdown("---")

        # --- Summary ---
        st.header("4️⃣ Summary & Fuel Savings 💰")
        optimized_cost = (total_distance_optimized / avg_mpg) * fuel_price_per_gallon
        distance_saved = total_distance_unoptimized - total_distance_optimized
        cost_saved = total_cost_unoptimized - optimized_cost

        st.metric("Total Optimized Distance", f"{total_distance_optimized:.2f} miles", f"-{distance_saved:.2f} miles saved")
        st.metric("Total Optimized Fuel Cost", f"${optimized_cost:.2f}", f"-${cost_saved:.2f} saved")

        st.info(f"Used {num_drivers_to_send} / {num_drivers_total} available drivers to complete all deliveries.")


if __name__ == "__main__":
    app_v1()
