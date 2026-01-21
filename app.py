import streamlit as st
import yaml
from fpdf import FPDF
import base64

# --- LOAD CONFIGURATION ---
def load_config():
    with open('config.yaml', 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)

config = load_config()

# --- define core classes and functions ---
class ShipmentCalculator:
    def __init__(self, mileage, rate):
        self.mileage = mileage
        self.rate = rate

    def calculate_total(self):
        base_cost = self.mileage * self.rate

        # use YAML to read config values
        if self.mileage > config['surcharge_threshold']:
            surcharge = base_cost * config['high_surcharge_rate']
        else:
            surcharge = base_cost * config['low_surcharge_rate']

        return base_cost + surcharge
    
# --- PDF GENERATION ---
def create_pdf(driver_name, plate, mileage, total_cost):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt=f"Service Agreement - {config['company_name']}", ln=1, align='C')
    pdf.ln(10) # line break
    pdf.cell(200, 10, txt=f"Driver: {driver_name}", ln=1)
    pdf.cell(200, 10, txt=f"License Plate: {plate}", ln=1)
    pdf.cell(200, 10, txt=f"Mileage: {mileage}", ln=1)
    pdf.cell(200, 10, txt=f"Total Agreed Cost: ${total_cost:.2f}", ln=1)
    pdf.cell(200, 10, txt="Signed: _______________________", ln=1)

    return pdf.output(dest='S').encode('latin-1') # return as byte string

# --- STREAMLIT UI ---
st.title("Logistics Service Agreement Generator")   

st.sidebar.header("Input Shipment Details")
driver_name = st.sidebar.text_input("Driver Name")
plate_num = st.sidebar.text_input("License Plate Number")
mileage = st.sidebar.number_input("Mileage", min_value=0.01)
custom_rate = st.sidebar.number_input("Rate per Mile", min_value=0.01, value=config['base_rate'])

if st.button("Generate Agreement"):
    if driver_name and mileage > 0:
        # Calculate total cost
        calc = ShipmentCalculator(mileage, custom_rate)
        total = calc.calculate_total()

        st.success(f"Calculated Successfully! Total Cost: ${total:.2f}")
        
        # Generate PDF
        pdf_bytes = create_pdf(driver_name, plate_num, mileage, total)

        # Provide download_button
        st.download_button(
            label="Download Agreement PDF",
            data=pdf_bytes,
            file_name="service_agreement.pdf",
            mime="application/pdf"
        )
    else:
        st.error("Please enter all required details.")