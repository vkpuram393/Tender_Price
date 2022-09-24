import datetime
from pydoc import cli
import streamlit as st
import pandas as pd
import numpy as np
import datahandling as dh
import pickle
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingRegressor


# Setting Title
st.title("Tender Price Estimation")
# Setting Header
st.header("Prediction Inputs")

#Dataset 
data = pd.read_excel("Model_Final_Data.xlsx",engine="openpyxl",index_col="Unnamed: 0",sheet_name='Sheet1')
top_clients = pd.read_excel("Model_Final_Data.xlsx",engine="openpyxl",sheet_name='Top_clients')
data2 =pd.read_excel("Innovator_Dates.xlsx",engine="openpyxl")[:40]
#innovator_df = pd.read_excel("ModelData.xlsx",engine="openpyxl")
inter_df = pd.read_excel("Standard_dev.xlsx",engine="openpyxl")
tender= {'Tender_Type':['Area Vasta','Locale','Multi Regione','Regionale','Regionale/Locale','Unione Acquisto']}
innovator_df = pd.DataFrame(tender)
#innovator_df['tender_type'].unique()

# Price Prediction
# Evalution 
#Mean absolute error calculation function

def mean_absolute_percentage_error(y_true, y_pred):
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100

# Independent Variables
input_cols = [' Tender_Type','Client', '#Participant','Proximity_Delivery',
       'Tender_Duration', 'Previous_Winning_Price', '#Months_G.E']
X = data[input_cols]
print(X['Client'].unique())
# Target Variable
Y = list(data["Winning_Price"])

#Fitting
#grad_reg = GradientBoostingRegressor(random_state=0)
#grad_reg.fit(X,np.log(Y))
#pickle.dump(grad_reg, open("grad_reg.pickle.dat", "wb"))
#print(mean_absolute_percentage_error(Y,np.exp(grad_reg.predict(X))))

#Interval Estimate
def interval_estimate (prv, std=inter_df):
    if prv < 1:
        return 6*inter_df.iloc[0]["Standard"]*inter_df.iloc[0]["Left"],7*inter_df.iloc[0]["Standard"]*inter_df.iloc[0]["Right"]
    elif prv >=1 and prv<50:
        return 6*inter_df.iloc[1]["Standard"]*inter_df.iloc[1]["Left"],7*inter_df.iloc[1]["Standard"]*inter_df.iloc[1]["Right"]
    else:
        return 6*inter_df.iloc[2]["Standard"]*inter_df.iloc[2]["Left"],7*inter_df.iloc[2]["Standard"]*inter_df.iloc[2]["Right"]

# Win probability model 
Y2 = list(data["DRL_Win_Flag"])
from sklearn.utils.class_weight import compute_class_weight
from sklearn.datasets import make_classification
# calculate class weighting
weighting = compute_class_weight(class_weight = 'balanced',classes = [0,1], y= Y2)
class_model = [0,1]
weight_hue = dict(zip(class_model,weighting))
print(weight_hue)
# log_reg = LogisticRegression(random_state=0,class_weight=weight_hue)
# log_reg.fit(X,Y2)
# pickle.dump(log_reg, open("log_reg.pickle.dat", "wb"))
# Input Interface

#Product Name
product = st.selectbox(
     'Select the name of the product:',
     (data2["Product_Name"]).unique())
#Tender Type
tender_type = st.selectbox(
     'Select type of the Tender:',
     (innovator_df["Tender_Type"]).unique())

if tender_type == 'Regionale':
    tender_type = 1
else:
    tender_type = 0


#Client
client = st.text_input('Client Name', 'ASUR MARCHE')
print(client)
if client in top_clients:
    client = 1
else:
    client = 2

#Participant
participant = st.number_input('Insert the no. of participants')

if participant >= 2:
    participant = 1
else:
    participant = 2


#Tender Submission Date
submission = st.date_input("Tender Submission Date:", datetime.date(2019, 7, 6))
#Proximity Delivery
start = st.date_input("Tender Start Date:", datetime.date(2020, 7, 6))
#Months since first generic entry
end =st.date_input("Tender End Date:", datetime.date(2020, 11, 6))
#Previous Winning Price
prv_win_pr = st.number_input('Insert the previous winning Price')

# Months since generic entry
#dictionary
date_dict = dict(zip(data2["Product_Name"],data2["Generic Entry"]))
date = date_dict.get(product)
#print(date)
#Date format conversion
date = datetime.datetime.strptime(date, "%d-%m-%Y")
date = date.date()


#Encoding
#client = dh.data_processor_client(client)
#tender_type = dh.data_processor_tender_type(tender_type)
#participant = dh.data_processor_participant(participant)
#print(str(end-start))

duration = np.float(str(end-start).split(" ")[0])/365
proximity = np.float(str(start-submission).split(" ")[0])/30
months_ge = np.float(str(submission-date).split(" ")[0])/30
#print(months_ge,proximity,duration,client,tender_type,participant)



#Test Data
X_test = (pd.DataFrame({' Tender_Type':[tender_type],'Client':[client], '#Participant':[participant],
'Proximity_Delivery':[proximity],'Tender_Duration':[duration],
'Previous_Winning_Price':[prv_win_pr], '#Months_G.E':[months_ge]}))

#Outputs
st.subheader("Prediction Outputs")
#Prediction on test data
#Price Prediction
loaded_grad_reg = pickle.load(open("grad_reg.pickle.dat", "rb"))
pred = np.exp(loaded_grad_reg.predict(X_test))
st.write("The predicted price is:",np.round(pred[0],3))

# Interval on test data
#Lower Interval
left , right = interval_estimate(prv_win_pr)
lower = pred - left
upper = pred + right

#print(lower)
st.write("Lower Bound:",np.round(lower[0],3))
st.write("Upper Bound:",np.round(upper[0],3))

# Win Probability prediction
loaded_log_reg = pickle.load(open("log_reg.pickle.dat", "rb"))
win_prob = (loaded_log_reg.predict_proba(X_test)[0])*100
#
st.write("The Predicted Win probability is:",np.round(win_prob[1],2),"%")

### Calculation Price Erosion
for i in range(len(data2)):
    if data2['Product_Name'][i] == product:
        innovator_price = data2['Innovator Price'][i]
price_erosion = innovator_price/pred
upper_interval_erosion = upper/innovator_price
lower_interval_erosion = lower/innovator_price
st.write("Price Erosion:",np.round(price_erosion[0],3),'%')
st.write("Lower Bound Erosion:",np.round(lower_interval_erosion[0],3),'%')
st.write("Upper Bound Erosion:",np.round(upper_interval_erosion[0],3),'%')



