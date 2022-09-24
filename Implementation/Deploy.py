# Importing the libraries
import streamlit as st
import pandas as pd
import numpy as np

#Setting up the title
st.title('Tender Price Prediction')
st.header("Model Data One View")
st.text("This page contains the Model One View Data which has been taken for modelling.")

#Form Relator
def form_relator(s):
    if s==1:
        return "Oral Solids"
    else:
        return "Injectables"
#CLient Relator
def client_relator(s):
    if s==1:
        return "Top 10 Clients"
    else:
        return "Bottom Left Clients"

st.header("Data Slicer options")
# adding a Radio buttond to get the data slicer
#Form
form = st.radio("Select the Doage Form:",("All","Oral Solids","Injectables"))
#Price
price = st.radio("Select the price variant",("All","Less than 1", "Between 1 to 100"))

@st.cache
#Loading the dataset
def load_data(name,form,price):
    data = pd.read_excel(name,engine="openpyxl",index_col="Unnamed: 0")
    data["Form"] = data["Form"].apply(form_relator) 
    data["Client"] = data["Client"].apply(client_relator)
    #form slicing
    if form == "All":
        data = data
    else:
        data = data[data["Form"]==form]
    #price slicing
    if price == "All":
        data = data
    elif price =="Less than 1":
        data = data[data["Previous_Winning_Price"]<1]
    else:
        data = data[data["Previous_Winning_Price"]>1]
    return data

data = load_data("Model_Final_Data.xlsx",form,price)

# Showing Data through the web page
st.subheader("Model Data Information")
st.write("The data has rows:",data.shape[0])
st.write("The data has columns:",data.shape[1])
st.write(data[['Identifier','Form', 
       'Client', '#Participant','Proximity_Delivery',
       'Tender_Duration', 'Previous_Winning_Price', '#Months_G.E','Winning_Price']])
