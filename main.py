import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from CoolProp.CoolProp import PropsSI

# Function to plot the p-h diagram with user-defined limits
def plot_ph_diagram(points, fluid, h_min, h_max, p_min, p_max):
    # Generate a range of pressures for plotting
    pressures = np.logspace(np.log10(p_min), np.log10(p_max), 100)

    h_f = []
    h_g = []

    # Get critical properties to avoid exceeding physical limits
    critical_pressure = PropsSI('Pcrit', fluid)

    # Collect saturated liquid (Q=0) and vapor (Q=1) enthalpies for plotting
    for P in pressures:
        if P < critical_pressure:
            h_f.append(PropsSI('H', 'P', P, 'Q', 0, fluid))
            h_g.append(PropsSI('H', 'P', P, 'Q', 1, fluid))
        else:
            # For pressures above the critical point, assume constant enthalpy
            h_f.append(PropsSI('H', 'P', critical_pressure, 'Q', 0, fluid))
            h_g.append(PropsSI('H', 'P', critical_pressure, 'Q', 1, fluid))

    # Create the plot
    plt.figure(figsize=(10, 8))
    plt.fill_betweenx(pressures / 1e6, h_f, h_g, color='lightgrey', alpha=0.5, where=(pressures < critical_pressure))

    # Plot isotherms with user-defined limits on enthalpy
    temperatures = np.linspace(273.15 + 10, 823.15, 10)
    for T in temperatures:
        try:
            h = [PropsSI('H', 'P', P, 'T', T, fluid) for P in pressures]
            if all(h_min <= val <= h_max for val in h):  # Plot only within enthalpy limits
                plt.plot(h, pressures / 1e6, label=f'{T-273.15:.0f} °C')
        except ValueError:
            pass

    # Calculate and plot user-defined points
    h_values = []
    p_values = []
    for point in points:
        try:
            h = PropsSI('H', 'P', point['P'], 'T', point['T'], fluid)
            h_values.append(h)
            p_values.append(point['P'] / 1e6)
            plt.plot(h, point['P'] / 1e6, 'o', label=f"Point ({point['T']-273.15:.0f}°C, {point['P']/1e6:.2f}MPa)")
        except ValueError:
            st.error(f"Invalid point: T={point['T']-273.15:.1f}°C, P={point['P']/1e6:.2f} MPa")

    # Connect points and fill the area between them
    if len(h_values) > 1:
        plt.plot(h_values, p_values, 'k-', alpha=0.7)
        plt.fill(h_values, p_values, 'green', alpha=0.3)  # Fill the area

    # Set axis limits as per user input
    plt.xlim(h_min, h_max)
    plt.ylim(p_min / 1e6, p_max / 1e6)

    # Customize labels and scales
    plt.xlabel('Enthalpy [J/kg]')
    plt.ylabel('Pressure [MPa]')
    plt.title(f'p-h Diagram for {fluid} (Custom Limits)')
    plt.legend(title='Isotherms & Points', loc='upper right')
    plt.yscale('log')
    plt.grid(True)
    plt.tight_layout()

    return plt

# Optimization: Best energy extraction window
def optimize_energy_extraction(points, fluid):
    max_delta_h = 0
    best_pair = None
    
    for i in range(len(points) - 1):
        h1 = PropsSI('H', 'P', points[i]['P'], 'T', points[i]['T'], fluid)
        h2 = PropsSI('H', 'P', points[i + 1]['P'], 'T', points[i + 1]['T'], fluid)
        delta_h = abs(h2 - h1)
        
        if delta_h > max_delta_h:
            max_delta_h = delta_h
            best_pair = (points[i], points[i + 1])

    return max_delta_h, best_pair

# Streamlit app
st.title("Interactive p-h Diagram with Optimization")

# Sidebar for settings
st.sidebar.header("Settings")
fluid = st.sidebar.selectbox("Select Fluid", ['Water', 'R134a', 'Ammonia', 'Propane', 'Isobutane'])

# Define axis limits (enthalpy and pressure)
st.sidebar.header("Axis Limits")
h_min = st.sidebar.number_input("Min Enthalpy [J/kg]", value=0, step=100000)
h_max = st.sidebar.number_input("Max Enthalpy [J/kg]", value=3000000, step=100000)
p_min = st.sidebar.number_input("Min Pressure [kPa]", value=100, step=100) * 1e3
p_max = st.sidebar.number_input("Max Pressure [kPa]", value=5000, step=100) * 1e3

# User-defined points
st.sidebar.header("Define the Points")
points = []
for i in range(1, 5):
    T = st.sidebar.number_input(f"Point {i} Temperature (°C)", value=60 + 10*i, format='%d') + 273.15
    P = st.sidebar.number_input(f"Point {i} Pressure (kPa)", value=10000 * (i + 1), format='%d') * 1e3
    points.append({'T': T, 'P': P})

# Plot button
if st.button('Plot p-h Diagram'):
    fig = plot_ph_diagram(points, fluid, h_min, h_max, p_min, p_max)
    st.pyplot(fig)

# Optimization button
if st.button('Optimize Energy Extraction'):
    delta_h, best_points = optimize_energy_extraction(points, fluid)
    if best_points:
        st.write(f"Best energy extraction between:")
        st.write(f"Point 1: T = {best_points[0]['T'] - 273.15:.1f}°C, P = {best_points[0]['P'] / 1e6:.2f} MPa")
        st.write(f"Point 2: T = {best_points[1]['T'] - 273.15:.1f}°C, P = {best_points[1]['P'] / 1e6:.2f} MPa")
        st.write(f"Enthalpy difference: {delta_h:.2f} J/kg")
    else:
        st.write("Not enough points to optimize energy extraction.")
