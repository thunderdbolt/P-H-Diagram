import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from CoolProp.CoolProp import PropsSI

# Function to plot p-h diagram with multiple energy extraction scenarios (each with four points)
def plot_ph_diagram(fluid, scenarios, h_min, h_max, p_min, p_max, delta_T):
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

    # Plot isotherms
    temperature_range = np.arange(273.15 + 10, 823.15, delta_T)
    for T in temperature_range:
        try:
            h = [PropsSI('H', 'P', P, 'T', T, fluid) for P in pressures]
            if all(h_min <= val <= h_max for val in h):
                plt.plot(h, pressures / 1e6, label=f'{T-273.15:.0f} °C')
        except ValueError:
            pass

    # Plot each scenario window
    for scenario in scenarios:
        h_values = []
        p_values = []
        for point in scenario['points']:
            try:
                h = PropsSI('H', 'P', point['P'], 'T', point['T'], fluid)
                h_values.append(h)
                p_values.append(point['P'] / 1e6)
                plt.plot(h, point['P'] / 1e6, 'o', label=f"Point ({point['T']-273.15:.0f}°C, {point['P']/1e6:.2f}MPa)")
            except ValueError:
                st.error(f"Invalid point: T={point['T']-273.15:.1f}°C, P={point['P']/1e6:.2f} MPa")

        if len(h_values) == 4:
            plt.plot(h_values, p_values, '-', label=scenario['label'])
            plt.fill(h_values, p_values, alpha=0.3)  # Fill the area for this scenario

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

# Sidebar for fluid selection and other inputs
st.sidebar.header("Fluid and Scenario Settings")

# Add fluid selection dropdown
fluid = st.sidebar.selectbox("Select Fluid", ['Isobutane', 'Propane', 'Water', 'R134a', 'Ammonia'])

# Scenario input parameters
scenarios = []

# We will simulate multiple scenarios (e.g., scenario 1, scenario 2, etc.)
for scenario_num in range(1, 3):  # Example: 2 scenarios, can add more
    st.sidebar.header(f"Scenario {scenario_num}")
    well_temp = st.sidebar.number_input(f"Well Temperature (°C) - Scenario {scenario_num}", value=100, step=1) + 273.15
    well_pressure = st.sidebar.number_input(f"Well Pressure (MPa) - Scenario {scenario_num}", value=1.0, step=0.1) * 1e6

    cooler_temp = st.sidebar.number_input(f"Cooler Temperature (°C) - Scenario {scenario_num}", value=30, step=1) + 273.15
    cooler_pressure = st.sidebar.number_input(f"Cooler Pressure (MPa) - Scenario {scenario_num}", value=0.1, step=0.01) * 1e6

    turbine_temp = st.sidebar.number_input(f"Turbine Outlet Temperature (°C) - Scenario {scenario_num}", value=50, step=1) + 273.15
    turbine_pressure = st.sidebar.number_input(f"Turbine Outlet Pressure (MPa) - Scenario {scenario_num}", value=0.5, step=0.1) * 1e6

    # Four points for the scenario window
    points = [
        {'T': well_temp, 'P': well_pressure},         # Well output
        {'T': turbine_temp, 'P': well_pressure},      # Before turbine
        {'T': turbine_temp, 'P': turbine_pressure},   # After turbine
        {'T': cooler_temp, 'P': cooler_pressure}      # After cooler
    ]

    scenarios.append({
        'points': points,
        'label': f'Scenario {scenario_num}'
    })

# Axis limits for the p-h diagram
st.sidebar.header("p-h Diagram Axis Limits")
h_min = st.sidebar.number_input("Min Enthalpy [J/kg]", value=0, step=100000)
h_max = st.sidebar.number_input("Max Enthalpy [J/kg]", value=3000000, step=100000)
p_min = st.sidebar.number_input("Min Pressure [kPa]", value=100, step=100) * 1e3
p_max = st.sidebar.number_input("Max Pressure [kPa]", value=5000, step=100) * 1e3

# Temperature line spacing (delta T)
delta_T = st.sidebar.number_input("Delta T for Isotherms (°C)", value=50, step=10)

# Plot the p-h diagram when the button is pressed
if st.button('Plot p-h Diagram'):
    fig = plot_ph_diagram(fluid, scenarios, h_min, h_max, p_min, p_max, delta_T)
    st.pyplot(fig)
