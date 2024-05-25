import streamlit as st
import requests

st.title('House Price Prediction')

house_size = st.number_input('House Size', min_value=0)
bed = st.number_input('Number of Beds', min_value=0)
bath = st.number_input('Number of Baths', min_value=0)
acre_lot = st.number_input('Lot Size (in acres)', min_value=0.0)

if st.button('Predict'):
    data = {
        "house_size": house_size,
        "bed": bed,
        "bath": bath,
        "acre_lot": acre_lot
    }
    response = requests.post('http://137.184.38.218:3000/predict', json=data)
    if response.status_code == 200:
        prediction = response.json().get('prediction')
        st.write(f'Predicted House Price: ${prediction:.2f}')
    else:
        st.write('Error: Unable to get prediction')