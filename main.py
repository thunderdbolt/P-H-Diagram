import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from CoolProp.CoolProp import PropsSI

# Function to plot the p-h diagram with scaling and limits per fluid
def plot_ph_diagram(points, fluid):
    # Get critical properties
    critical_pressure = PropsSI('Pcrit', fluid)
    critical_temperature = PropsSI('Tcrit', fluid)
    
    # Adjust pressure range based on critical pressure (Avoid going far beyond the critical pressure)
    pressures = np.logspace(5, np.log10(min(critical_pressure * 1.2, 250e6)), 100)  # Up to 120% of critical pressure
    
    h_f = []
    h_g = []

    # Collect saturated liquid (Q=0) and vapor (Q=1) enthalpies for plotting
    for P in pressures:
        if P < critical_pressure:
            h_f.append(PropsSI('H', 'P', P, 'Q', 0, fluid))
            h_g.append(PropsSI('H', 'P', P, 'Q', 1, fluid))
        else:
            # For pressures above the critical point, assume enthalpy remains constant
            h_f.append(PropsSI('H', 'P', critical_pressure, 'Q', 0, fluid))
            h_g.append(PropsSI('H', 'P', critical_pressure, 'Q', 1, fluid))

    # Create the plot
    plt.figure(figsize=(10, 8))
    plt.fill_betweenx(pressures / 1e6, h_f, h_g, color='lightgrey', alpha=0.5, where=(pressures < critical_pressure))

    # Plot isotherms with temperature range limited based on fluid's critical temperature
    temperature_range = np.linspace(273.15 + 10, min(critical_temperature + 200, 823.15), 10)  # 10°C to critical + buffer
    
    for T in temperature_range:
        try:
            h = [PropsSI('H', 'P', P, 'T', T, fluid) for P in pressures]
            plt.plot(h, pressures / 1e6, label=f'{T-273.15:.0f} °C')
        except ValueError:
            # In case any values are invalid, skip them
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
            st.error(f"Invalid state point: T={point['T']-273.15:.1f}°C, P={point['P']/1e6:.2f} MPa")

    # Connect the points and fill the area
    if len(h_values) > 1:
        plt.plot(h_values, p_values, 'k-', alpha=0.7)
        plt.fill(h_values, p_values, 'green', alpha=0.3)  # Fill the area

    # Customize axis labels and scales
    plt.xlabel('Enthalpy [J/kg]')
    plt.ylabel('Pressure [MPa]')
    plt.title(f'p-h Diagram for {fluid} (Limited Range)')
    plt.legend(title='Isotherms & Points', loc='upper right')
    plt.yscale('log')
    plt.xscale('linear')
    plt.grid(True)
    plt.tight_layout()

    return plt

st.title("Interactive p-h Diagram")

# User inputs for fluid and points
st.sidebar.header("Settings")
fluid = st.sidebar.selectbox("Select Fluid", ['Water', 'R134a', 'Ammonia', 'Propane', 'Isobutane'])

st.sidebar.header("Define the Points")
points = []
for i in range(1, 5):
    T = st.sidebar.number_input(f"Point {i} Temperature (°C)", value=60 + 10*i, format='%d') + 273.15
    P = st.sidebar.number_input(f"Point {i} Pressure (kPa)", value=10000 * (i + 1), format='%d') * 1e3
    points.append({'T': T, 'P': P})

# Plot button
if st.button('Plot p-h Diagram'):
    fig = plot_ph_diagram(points, fluid)
    st.pyplot(fig)
