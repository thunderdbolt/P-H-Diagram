import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from CoolProp.CoolProp import PropsSI

# Function to plot p-h diagram (we will update this in later phases)
def plot_ph_diagram(points, fluid, h_min, h_max, p_min, p_max, delta_T):
    pressures = np.logspace(np.log10(p_min), np.log10(p_max), 100)
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

    temperature_range = np.arange(273.15 + 10, 823.15, delta_T)
    for T in temperature_range:
        try:
            h = [PropsSI('H', 'P', P, 'T', T, fluid) for P in pressures]
            if all(h_min <= val <= h_max for val in h):
                plt.plot(h, pressures / 1e6, label=f'{T-273.15:.0f} °C')
        except ValueError:
            pass

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

    if len(h_values) > 1:
        plt.plot(h_values, p_values, 'k-', alpha=0.7)
        plt.fill(h_values, p_values, 'green', alpha=0.3)

    plt.xlim(h_min, h_max)
    plt.ylim(p_min / 1e6, p_max / 1e6)

    plt.xlabel('Enthalpy [J/kg]')
    plt.ylabel('Pressure [MPa]')
    plt.title(f'p-h Diagram for {fluid} (Custom Limits)')
    plt.legend(title='Isotherms & Points', loc='upper right')
    plt.yscale('log')
    plt.grid(True)
    plt.tight_layout()

    return plt

st.title("Geothermal System Optimization Tool")

# Sidebar for enhanced input parameters
st.sidebar.header("Geothermal Well Input")

# Define the range of geothermal well output temperatures
geothermal_temp_min = st.sidebar.number_input("Geothermal Well Temp Min (°C)", value=100, step=1) + 273.15
geothermal_temp_max = st.sidebar.number_input("Geothermal Well Temp Max (°C)", value=200, step=1) + 273.15

# Define the geothermal well pressure (we can optimize this later)
geothermal_pressure = st.sidebar.number_input("Geothermal Well Pressure (MPa)", value=1.0, step=0.1) * 1e6

st.sidebar.header("Cooler and Turbine Parameters")

# Input for cooler performance (low condenser temperature or pressure)
cooler_temp = st.sidebar.number_input("Cooler Temperature (°C)", value=30, step=1) + 273.15
cooler_pressure = st.sidebar.number_input("Cooler Pressure (MPa)", value=0.1, step=0.01) * 1e6

# Input for turbine isentropic efficiency
turbine_efficiency = st.sidebar.number_input("Turbine Isentropic Efficiency (%)", value=80, step=1) / 100

# Input for flow rate (optional, can optimize this later)
flow_rate = st.sidebar.number_input("Fluid Mass Flow Rate (kg/s)", value=10.0, step=1.0)

st.sidebar.header("p-h Diagram Axis Limits and Settings")

# Define axis limits for p-h diagram
h_min = st.sidebar.number_input("Min Enthalpy [J/kg]", value=0, step=100000)
h_max = st.sidebar.number_input("Max Enthalpy [J/kg]", value=3000000, step=100000)
p_min = st.sidebar.number_input("Min Pressure [kPa]", value=100, step=100) * 1e3
p_max = st.sidebar.number_input("Max Pressure [kPa]", value=5000, step=100) * 1e3

# Define delta T for isotherms
delta_T = st.sidebar.number_input("Delta T for Isotherms (°C)", value=50, step=10)

# Placeholder for user-defined points (this will be optimized later)
points = [
    {'T': geothermal_temp_min, 'P': geothermal_pressure},
    {'T': cooler_temp, 'P': cooler_pressure}
]

# Plot button
if st.button('Plot p-h Diagram'):
    fig = plot_ph_diagram(points, 'Isobutane', h_min, h_max, p_min, p_max, delta_T)
    st.pyplot(fig)

# Future Phases: Simulation of Scenarios, Optimization, etc.
st.write("Additional features will be added in the next phases.")
