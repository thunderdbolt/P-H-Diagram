import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from CoolProp.CoolProp import PropsSI

# Function to plot the p-h diagram
def plot_ph_diagram(points, fluid):
    pressures = np.logspace(5, np.log10(250e6), 100)  # From 0.1 to 250 MPa
    h_f = []
    h_g = []

    critical_pressure = PropsSI('Pcrit', fluid)
    for P in pressures:
        if P < critical_pressure:
            h_f.append(PropsSI('H', 'P', P, 'Q', 0, fluid))
            h_g.append(PropsSI('H', 'P', P, 'Q', 1, fluid))
        else:
            h_f.append(PropsSI('H', 'P', critical_pressure, 'Q', 0, fluid))
            h_g.append(PropsSI('H', 'P', critical_pressure, 'Q', 1, fluid))

    plt.figure(figsize=(10, 8))
    plt.fill_betweenx(pressures / 1e6, h_f, h_g, color='lightgrey', alpha=0.5, where=(pressures < critical_pressure))

    # Plot isotherms
    temperatures = np.linspace(273.15 + 10, 823.15, 10)  # From 10 to 550°C
    for T in temperatures:
        h = [PropsSI('H', 'P', P, 'T', T, fluid) for P in pressures]
        plt.plot(h, pressures / 1e6, label=f'{T-273.15:.0f} °C')

    # Calculate enthalpy for the user-defined points and plot
    h_values = []
    p_values = []
    for point in points:
        h = PropsSI('H', 'P', point['P'], 'T', point['T'], fluid)
        h_values.append(h)
        p_values.append(point['P'] / 1e6)
        plt.plot(h, point['P'] / 1e6, 'o', label=f"Point ({point['T']-273.15:.0f}°C, {point['P']/1e6:.2f}MPa)")

    # Connect the points and fill the area
    if len(h_values) > 1:
        plt.plot(h_values, p_values, 'k-', alpha=0.7)
        plt.fill(h_values, p_values, 'green', alpha=0.3)  # Fill the area

    plt.xlabel('Enthalpy [J/kg]')
    plt.ylabel('Pressure [MPa]')
    plt.title(f'p-h Diagram for {fluid} up to 250 MPa')
    plt.legend(title='Isotherms & Points', loc='upper right')
    plt.yscale('log')
    plt.xscale('linear')
    plt.grid(True)
    plt.tight_layout()

    return plt

st.title("Interactive p-h Diagram")

# User inputs for fluid and points
st.sidebar.header("Settings")
fluid = st.sidebar.selectbox("Select Fluid", ['Water', 'R134a', 'Ammonia', 'Propane', 'CO2'])

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
