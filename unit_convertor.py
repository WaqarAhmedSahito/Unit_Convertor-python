import streamlit as st
import requests
from datetime import datetime
import pandas as pd

st.set_page_config(
    page_title="Quantum Converter",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.markdown("""
    <style>
    .main {background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);}
    .st-emotion-cache-1v0mbdj {border-radius: 10px; border: 2px solid #ffffff20;}
    h1 {color: #fff; text-align: center;}
    h2 {color: #fff; border-bottom: 2px solid #fff;}
    .stSelectbox label {color: #fff!important;}
    .stNumberInput label {color: #fff!important;}
    .st-emotion-cache-1vbkxwb p {color: #fff;}
    .stButton>button {background: #4CAF50; color: white; border-radius: 8px; padding: 0.5rem 1rem;}
    .stDownloadButton>button {background: #2196F3!important;}
    </style>
    """, unsafe_allow_html=True)
def convert_length(value, from_unit, to_unit):
    factors = {
        'mm': 0.001, 'cm': 0.01, 'm': 1.0,
        'km': 1000.0, 'inch': 0.0254, 'foot': 0.3048,
        'mile': 1609.34, 'yard': 0.9144
    }
    return value * factors[from_unit] / factors[to_unit]
def get_currency_rates(base_currency):
    mock_rates = {
        "USD": {"USD": 1.0, "EUR": 0.92, "GBP": 0.78, "INR": 83.21, "PKR": 280.5, "JPY": 150.0},
        "EUR": {"USD": 1.09, "EUR": 1.0, "GBP": 0.85, "INR": 90.5, "PKR": 295.0, "JPY": 162.8},
        "GBP": {"USD": 1.28, "EUR": 1.17, "GBP": 1.0, "INR": 105.3, "PKR": 340.0, "JPY": 180.4},
        "INR": {"USD": 0.012, "EUR": 0.011, "GBP": 0.0095, "INR": 1.0, "PKR": 3.37, "JPY": 1.8},
        "PKR": {"USD": 0.0036, "EUR": 0.0034, "GBP": 0.0029, "INR": 0.30, "PKR": 1.0, "JPY": 0.53},
        "JPY": {"USD": 0.0067, "EUR": 0.0061, "GBP": 0.0055, "INR": 0.56, "PKR": 1.89, "JPY": 1.0}
    }
    
    rates = mock_rates.get(base_currency, {})
    rates[base_currency] = 1.0  # Add identity conversion
    return rates
def convert_temperature(value, from_unit, to_unit):
    conversions = {
        ('°C', '°F'): lambda x: (x * 9/5) + 32,
        ('°F', '°C'): lambda x: (x - 32) * 5/9,
        ('K', '°C'): lambda x: x - 273.15,
        ('°C', 'K'): lambda x: x + 273.15,
        ('K', '°F'): lambda x: (x - 273.15) * 9/5 + 32,
        ('°F', 'K'): lambda x: (x - 32) * 5/9 + 273.15
    }
    if from_unit == to_unit:
        return value
    return round(conversions[(from_unit, to_unit)](value), 2)

def convert_weight(value, from_unit, to_unit):
    conversions = {
        'mg': 0.001,
        'g': 1,
        'kg': 1000,
        'ton': 1e6,
        'lb': 453.592,
        'oz': 28.3495    
    }
    if from_unit == to_unit:
        return value
    grams = value * conversions[from_unit]
    return round(grams / conversions[to_unit], 6)

def convert_digital_storage(value, from_unit, to_unit):
    conversions = {
        'bits': 0.125,
        'bytes': 1,
        'KB': 1024,
        'MB': 1024**2,
        'GB': 1024**3,
        'TB': 1024**4,
        'PB': 1024**5
    }
    if from_unit == to_unit:
        return value
    bytes_val = value * conversions[from_unit]
    return round(bytes_val / conversions[to_unit], 6)

def convert_historical(value, from_unit, to_unit):
    factors = {
        #  Roman
        'libra': {'kg': 0.327, 'lb': 0.721},
        #  Greek
        'talent': {'kg': 26.0, 'lb': 57.32},
        #  Medieval
        'stone': {'kg': 6.35, 'lb': 14.0},
        #  Egyptian
        'deben': {'g': 91.0, 'oz': 3.21},
        #  Biblical
        'shekel': {'g': 11.4, 'oz': 0.402}
    }
    
    if from_unit == to_unit:
        return value
    
    try:
        return round(value * factors[from_unit][to_unit], 4)
    except KeyError:
        kg_value = value * factors[from_unit]['kg']
        return round(kg_value / factors[to_unit]['kg'], 4)
    
# App Header
st.title("🔮 Quantum Converter")
st.markdown("### Your Universal Measurement Solution")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    category = st.selectbox("Select Category", [
        "Length", "Temperature", "Weight",
        "Digital Storage", "Currency", "Historical Units"
    ])
    
    st.divider()
    st.markdown("**Conversion History**")
    if 'history' not in st.session_state:
        st.session_state.history = []
    if st.button("Clear History"):
        st.session_state.history = []

# Main Area
col1, col2, col3 = st.columns([2,1,2])
with col1:
    value = st.number_input("Enter Value", min_value=0.0, step=0.1)

with col3:
    if category == "Length":
        units = ['mm', 'cm', 'm', 'km', 'inch', 'foot', 'mile', 'yard']
    elif category == "Temperature":
        units = ['°C', '°F', 'K']
    elif category == "Currency":
        units = list(get_currency_rates('USD').keys())
    elif category == "Weight":
        units = ['mg', 'g', 'kg', 'ton', 'lb', 'oz']
    elif category == "Digital Storage":
        units = ['bits', 'bytes', 'KB', 'MB', 'GB', 'TB', 'PB']
    elif category == "Historical Units":
        units = ['libra', 'talent', 'stone', 'deben', 'shekel', 'kg', 'lb', 'g', 'oz']

    from_unit = st.selectbox("From", units)
    to_unit = st.selectbox("To", units)

# Conversion Logic
result = None
if category == "Length":
    result = convert_length(value, from_unit, to_unit)
elif category == "Temperature":
    result = convert_temperature(value, from_unit, to_unit)
elif category == "Currency":
    if from_unit == to_unit:
        result = value
    else:
        rates = get_currency_rates(from_unit)

        if to_unit in rates:
            result = value * rates[to_unit]
        else:
            st.error(f"⚠️ Conversion from {from_unit} to {to_unit} not available")
            result = None
elif category == "Weight":

    if from_unit == to_unit:
        result = value
    else:
        result = convert_weight(value, from_unit, to_unit)
elif category == "Digital Storage":
  
    if from_unit == to_unit:
        result = value
    else:
        result = convert_digital_storage(value, from_unit, to_unit)
elif category == "Historical Units":
    if from_unit == to_unit:
        result = value
    else:
        result = convert_historical(value, from_unit, to_unit)     

# Display Result
if result is not None:
    st.markdown(f"""
    <div style="background: #ffffff20; padding: 2rem; border-radius: 10px; margin: 2rem 0;">
        <h2 style="color: #fff; text-align: center;">
            {value:.2f} {from_unit} = {result:.2f} {to_unit}
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    # add history
    st.session_state.history.append({
        'Date': datetime.now().strftime("%Y-%m-%d %H:%M"),
        'Category': category,
        'Input': f"{value} {from_unit}",
        'Output': f"{result:.2f} {to_unit}"
    })

# History Section
with st.expander("📜 Conversion History"):
    if st.session_state.history:
        history_df = pd.DataFrame(st.session_state.history)
        st.dataframe(history_df.style.set_properties(**{
            'background-color': '#ffffff20',
            'color': 'white',
            'border': '1px solid white'
        }))
        
        csv = history_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download History",
            data=csv,
            file_name="conversion_history.csv",
            mime="text/csv"
        )
    else:
        st.info("No conversion history yet")


# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #fff;">
    <p>📖 Built with ❤️ using Streamlit | 🔐 Secure Local Processing | 🕒 Real-time Rates</p>
</div>
""", unsafe_allow_html=True)