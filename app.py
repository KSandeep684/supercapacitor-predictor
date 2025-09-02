# ==============================================================================
# CAPSTONE PROJECT: INTERACTIVE SUPERAPACITOR PREDICTOR WEB APP (SIMPLIFIED & FINAL)
# ==============================================================================

import streamlit as st
import pandas as pd
from io import StringIO
import matplotlib.pyplot as plt
import xgboost as xgb
import numpy as np

@st.cache_resource
def load_and_train_models():
    """
    Loads the seed data, generates a large dataset directly, and trains the models.
    """
    # --- Define Degradation Scenarios Directly ---
    degradation_scenarios = [
        {'config': {'Electrode_Material': 'CuO/MnO2@MWCNT', 'Electrolyte_Type': 'RAE', 'Device_Type': 'Coin Cell', 'Current_Density_Ag-1': 1.0}, 'start_cycles': 0, 'end_cycles': 5000, 'start_charge': 192.03, 'end_charge': 173.79, 'start_discharge': 182.89, 'end_discharge': 165.51},
        {'config': {'Electrode_Material': 'CuO/MnO2@MWCNT', 'Electrolyte_Type': 'KOH', 'Device_Type': 'Coin Cell', 'Current_Density_Ag-1': 1.0}, 'start_cycles': 0, 'end_cycles': 5000, 'start_charge': 71.53, 'end_charge': 58.59, 'start_discharge': 68.12, 'end_discharge': 55.80},
        {'config': {'Electrode_Material': 'CuO/CoO@MWCNT', 'Electrolyte_Type': 'RAE', 'Device_Type': 'Assembled_SC', 'Current_Density_Ag-1': 2.75}, 'start_cycles': 0, 'end_cycles': 5000, 'start_charge': 29.03, 'end_charge': 23.89, 'start_discharge': 27.65, 'end_discharge': 22.75},
        {'config': {'Electrode_Material': 'CuO/CoO@MWCNT', 'Electrolyte_Type': 'KOH', 'Device_Type': 'Assembled_SC', 'Current_Density_Ag-1': 2.75}, 'start_cycles': 0, 'end_cycles': 5000, 'start_charge': 13.86, 'end_charge': 10.76, 'start_discharge': 13.20, 'end_discharge': 10.25},
        {'config': {'Electrode_Material': 'CuO@MWCNT', 'Electrolyte_Type': 'RAE', 'Device_Type': 'Assembled_SC', 'Current_Density_Ag-1': 1.5}, 'start_cycles': 0, 'end_cycles': 10000, 'start_charge': 98.22, 'end_charge': 66.02, 'start_discharge': 93.54, 'end_discharge': 62.88},
        {'config': {'Electrode_Material': 'CuO@MWCNT', 'Electrolyte_Type': 'KOH', 'Device_Type': 'Assembled_SC', 'Current_Density_Ag-1': 1.5}, 'start_cycles': 0, 'end_cycles': 10000, 'start_charge': 33.86, 'end_charge': 22.05, 'start_discharge': 32.25, 'end_discharge': 21.00},
        {'config': {'Electrode_Material': 'CuO', 'Electrolyte_Type': 'RAE', 'Device_Type': 'Assembled_SC', 'Current_Density_Ag-1': 0.475}, 'start_cycles': 0, 'end_cycles': 10000, 'start_charge': 12.68, 'end_charge': 7.50, 'start_discharge': 12.08, 'end_discharge': 7.14},
        {'config': {'Electrode_Material': 'CuO', 'Electrolyte_Type': 'KOH', 'Device_Type': 'Assembled_SC', 'Current_Density_Ag-1': 0.375}, 'start_cycles': 0, 'end_cycles': 10000, 'start_charge': 6.87, 'end_charge': 3.80, 'start_discharge': 6.54, 'end_discharge': 3.62},
    ]

    # --- Define Single-Point Scenarios Directly ---
    single_point_scenarios = [
        {'Electrode_Material': 'CuO/MnO2@MWCNT', 'Electrolyte_Type': 'RAE', 'Device_Type': 'Coin Cell', 'Current_Density_Ag-1': 2.0, 'Cycles_Completed': 0, 'Charge_Capacity_mAh_g-1': 175.88, 'Discharge_Capacity_mAh_g-1': 167.50},
        {'Electrode_Material': 'CuO/CoO@MWCNT', 'Electrolyte_Type': 'RAE', 'Device_Type': 'Assembled_SC', 'Current_Density_Ag-1': 4.0, 'Cycles_Completed': 0, 'Charge_Capacity_mAh_g-1': 24.78, 'Discharge_Capacity_mAh_g-1': 23.60},
        {'Electrode_Material': 'CuO/CoO@MWCNT', 'Electrolyte_Type': 'RAE', 'Device_Type': 'Coin Cell', 'Current_Density_Ag-1': 1.5, 'Cycles_Completed': 0, 'Charge_Capacity_mAh_g-1': 132.51, 'Discharge_Capacity_mAh_g-1': 126.20},
        {'Electrode_Material': 'CuO/CoO@MWCNT', 'Electrolyte_Type': 'KOH', 'Device_Type': 'Coin Cell', 'Current_Density_Ag-1': 1.5, 'Cycles_Completed': 0, 'Charge_Capacity_mAh_g-1': 58.79, 'Discharge_Capacity_mAh_g-1': 55.99},
        {'Electrode_Material': 'CuO@MWCNT', 'Electrolyte_Type': 'RAE', 'Device_Type': 'Assembled_SC', 'Current_Density_Ag-1': 2.5, 'Cycles_Completed': 0, 'Charge_Capacity_mAh_g-1': 83.79, 'Discharge_Capacity_mAh_g-1': 79.80},
        {'Electrode_Material': 'CuO@MWCNT', 'Electrolyte_Type': 'RAE', 'Device_Type': 'Coin Cell', 'Current_Density_Ag-1': 1.0, 'Cycles_Completed': 0, 'Charge_Capacity_mAh_g-1': 58.94, 'Discharge_Capacity_mAh_g-1': 56.13},
        {'Electrode_Material': 'CuO@MWCNT', 'Electrolyte_Type': 'KOH', 'Device_Type': 'Coin Cell', 'Current_Density_Ag-1': 1.0, 'Cycles_Completed': 0, 'Charge_Capacity_mAh_g-1': 37.78, 'Discharge_Capacity_mAh_g-1': 35.98},
        {'Electrode_Material': 'CuO', 'Electrolyte_Type': 'RAE', 'Device_Type': 'Coin Cell', 'Current_Density_Ag-1': 0.5, 'Cycles_Completed': 0, 'Charge_Capacity_mAh_g-1': 33.78, 'Discharge_Capacity_mAh_g-1': 32.17},
        {'Electrode_Material': 'CuO', 'Electrolyte_Type': 'KOH', 'Device_Type': 'Coin Cell', 'Current_Density_Ag-1': 0.5, 'Cycles_Completed': 0, 'Charge_Capacity_mAh_g-1': 23.48, 'Discharge_Capacity_mAh_g-1': 22.36},
    ]

    all_data = []
    # Process degradation scenarios
    for scenario in degradation_scenarios:
        charge_drop = scenario['start_charge'] - scenario['end_charge']
        discharge_drop = scenario['start_discharge'] - scenario['end_discharge']
        for cycles in range(0, scenario['end_cycles'] + 1, 250):
            cycle_ratio = cycles / scenario['end_cycles'] if scenario['end_cycles'] > 0 else 0
            charge = scenario['start_charge'] - charge_drop * (cycle_ratio ** 0.9)
            discharge = scenario['start_discharge'] - discharge_drop * (cycle_ratio ** 0.9)
            row_data = scenario['config'].copy()
            row_data['Cycles_Completed'] = cycles
            row_data['Charge_Capacity_mAh_g-1'] = charge
            row_data['Discharge_Capacity_mAh_g-1'] = discharge
            all_data.append(row_data)

    # Add single point scenarios
    all_data.extend(single_point_scenarios)
    df_large = pd.DataFrame(all_data)

    # --- Train Models ---
    df_processed = pd.get_dummies(df_large, columns=['Electrode_Material', 'Electrolyte_Type', 'Device_Type'])
    features_cols = df_processed.drop(columns=['Charge_Capacity_mAh_g-1', 'Discharge_Capacity_mAh_g-1']).columns
    y_charge = df_processed['Charge_Capacity_mAh_g-1']
    y_discharge = df_processed['Discharge_Capacity_mAh_g-1']
    
    charge_model = xgb.XGBRegressor(n_estimators=100, random_state=42).fit(df_processed[features_cols], y_charge)
    discharge_model = xgb.XGBRegressor(n_estimators=100, random_state=42).fit(df_processed[features_cols], y_discharge)
    
    return charge_model, discharge_model, features_cols

# --- Load models ---
charge_model_xgb, discharge_model_xgb, feature_columns = load_and_train_models()

# --- WEB APP INTERFACE ---
st.set_page_config(layout="wide")
st.title("🔋 Supercapacitor Performance Predictor")
st.markdown("A Capstone Project to predict supercapacitor degradation using Machine Learning. Select parameters from the sidebar to generate a prediction.")

st.sidebar.header("Input Parameters")
material_options = ['CuO/MnO2@MWCNT', 'CuO/CoO@MWCNT', 'CuO@MWCNT', 'CuO']
plot_material = st.sidebar.selectbox("1. Select Electrode Material", material_options)
electrolyte_options = ['RAE', 'KOH']
plot_electrolyte = st.sidebar.selectbox("2. Select Electrolyte Type", electrolyte_options)
device_options = ['Coin Cell', 'Assembled_SC']
plot_device = st.sidebar.selectbox("3. Select Device Type", device_options)
plot_current_density = st.sidebar.number_input("4. Enter Current Density (A/g)", min_value=0.1, max_value=5.0, value=1.0, step=0.1)
unit_choice = st.sidebar.radio("5. Select Output Units", ('mAh/g', 'C/g'))
output_format = st.sidebar.radio("6. Select Output Format", ('Simple Prediction', 'Graph', 'Tabular Data'))

def predict_capacity(material, electrolyte, device, current_density, cycles):
    input_data = pd.DataFrame({'Current_Density_Ag-1': [current_density], 'Cycles_Completed': [cycles], 'Electrode_Material': [material], 'Electrolyte_Type': [electrolyte], 'Device_Type': [device]})
    input_encoded = pd.get_dummies(input_data)
    final_input = input_encoded.reindex(columns=feature_columns, fill_value=0)
    charge = charge_model_xgb.predict(final_input)[0]
    discharge = discharge_model_xgb.predict(final_input)[0]
    return float(charge), float(discharge)

if output_format == 'Simple Prediction':
    st.subheader("Simple Prediction for a Single Point")
    selected_cycles = st.slider("Select Number of Cycles to Predict", 0, 10000, 5000, 500)
    charge_pred, discharge_pred = predict_capacity(plot_material, plot_electrolyte, plot_device, plot_current_density, selected_cycles)
    if unit_choice == 'C/g':
        charge_pred *= 3.6
        discharge_pred *= 3.6
    col1, col2 = st.columns(2)
    col1.metric("Predicted Charge Capacity", f"{charge_pred:.2f} {unit_choice}")
    col2.metric("Predicted Discharge Capacity", f"{discharge_pred:.2f} {unit_choice}")

elif output_format == 'Graph':
    st.subheader("Predictive Degradation Graph")
    cycles_to_plot = list(range(0, 10001, 500))
    charges, discharges = [], []
    for cycle in cycles_to_plot:
        charge, discharge = predict_capacity(plot_material, plot_electrolyte, plot_device, plot_current_density, cycle)
        charges.append(charge)
        discharges.append(discharge)
    df_plot = pd.DataFrame({'Cycles': cycles_to_plot, 'Charge Capacity': charges, 'Discharge Capacity': discharges})
    if unit_choice == 'C/g':
        df_plot['Charge Capacity'] *= 3.6
        df_plot['Discharge Capacity'] *= 3.6
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(df_plot['Cycles'], df_plot['Charge Capacity'], marker='o', linestyle='-', markersize=4, label='Predicted Charge Capacity')
    ax.plot(df_plot['Cycles'], df_plot['Discharge Capacity'], marker='s', linestyle='--', markersize=4, label='Predicted Discharge Capacity')
    ax.set_title(f'Prediction for {plot_material} ({plot_electrolyte})', fontsize=16)
    ax.set_xlabel('Number of Cycles Completed', fontsize=12)
    ax.set_ylabel(f'Capacity ({unit_choice})', fontsize=12)
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

elif output_format == 'Tabular Data':
    st.subheader("Predictive Degradation Data Table")
    cycles_to_plot = list(range(0, 10001, 500))
    table_data = []
    for cycle in cycles_to_plot:
        charge, discharge = predict_capacity(plot_material, plot_electrolyte, plot_device, plot_current_density, cycle)
        table_data.append({'Cycles': cycle, 'Charge Capacity': charge, 'Discharge Capacity': discharge})
    df_table = pd.DataFrame(table_data)
    if unit_choice == 'C/g':
        df_table['Charge Capacity'] *= 3.6
        df_table['Discharge Capacity'] *= 3.6
    st.dataframe(df_table.style.format({'Charge Capacity': '{:.2f}', 'Discharge Capacity': '{:.2f}'}))
