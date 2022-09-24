# Importing the libraries
from click import option
import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# Loading the data
data = pd.read_excel("Model_Final_Data.xlsx",engine="openpyxl",index_col="Unnamed: 0")
print(data.columns)
# Setting Title
st.title("Tender Price Estimation")
# Setting Header
st.header("Visualisation")
st.write("This page contains all the visualisation details of the data.")

#Density Plots
#options
option = st.radio("Select the Field:",('Proximity_Delivery','Tender_Duration', 'Previous_Winning_Price', '#Months_G.E'))
# Plots
st.header("Density plot")
st.write(option)

# Density Plot Function
def linePlot(option):
    fig = plt.figure(figsize=(10, 4))
    sns.kdeplot(data[option])
    st.pyplot(fig)

linePlot(option)
# Correlation Plot

st.header("Correlation Plot")
st.write("This graph depicts the relation among the independent variables.")
X = data[['Form', 
       'Client'," Tender_Type" ,'#Participant','Proximity_Delivery',
       'Tender_Duration', 'Previous_Winning_Price', '#Months_G.E']]

def corr_plot(df):
    fig = plt.figure(figsize=(5,5))
    sns.heatmap(df.corr(),cmap="YlGnBu",annot=True)
    st.pyplot(fig)

corr_plot(X)
