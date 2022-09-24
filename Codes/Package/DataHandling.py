import pandas as pd
import numpy as np
import plotly.express as px
import os
import glob
import warnings
warnings.filterwarnings('ignore')
import matplotlib.pyplot as plt
import seaborn as sns

## Product Name Fetching

def product_name(df):
    """
    Utility: 
    =========
    
    Fetches the Product Name and the Strength , Product Form
    Arguements:
    ===========
    
    df: Raw_datafrom which it needs to be processed.
    """
    # Fetches the product description from the raw data and splits the data from the blank spaces.
    product_desc = list(df.iloc[0])[0].split(" ")
    #Fetches the Name of the Product
    name = list(df.iloc[0])[0].split(" ")[1]
    try:
        name = name.split("-")[0]
    except:
        name = name
    #Fetches the Strength of the Product
    try:
        power = product_desc[-3].replace(",",".")
    except:
        power = product_desc[-3]
    #Gets the form as injectable if fiale(vial in english) is present else Osd.
    if list(df.iloc[0])[0].find("OS")>0:
        form = "OSD"
    elif list(df.iloc[0])[0].find("ORODISP")>0:
        form = "OSD"
    else:
        form = "INJECTABLE"
    return name.upper()+" "+power,form

## Final column
def data_clean(df):
    """
    Utility:
    ========
    Creates the clear data from the unstructured data.
    
    Arguments:
    ==========
    1. df: The dataset that needs to be cleaned.
    
    Functions used at backend : product_name (lib : DataHandling)
    """
    #list of the columns that have been considered for Model Data in the Raw_Format
    cols_raw = ["ID pratica","Ambito","Cliente","Reg.","Data IF","Data FF (con proroga)","Data rif.","Ditta agg.","Ditta conc.","Pr.Agg",
             "Pr.Conc.","Q. Annua"]
    cols_raw2 = ["ID pratica","Ambito","Cliente","Reg.","Data IF","Data FF (con proroga)",9,"Ditta agg.","Ditta conc.","Pr.Agg",
             "Pr.Conc.","Q. Annua"]
    #List of the translation of the Italian column names -> English column Names 
    cols_model = ["Tender_Id","Tender_Type","Client","Region","Start_Date","End_Date","Tender_Submission_Date","Winner","Loser",
                  "Winning_Price","Losing_Price","Annual_Quantity"]
    #Cleaning of the Raw Data unnecessary rows and converting to English equivalent rows 
    try:
        df_new = df[cols_raw]
    except:
        df_new = df[cols_raw2]
    df_new.columns = cols_model
    #Droping the columns with null values aimed for clearing the rows containg the product Names
    df_new = df_new.dropna(thresh = 8)
    # Extracting the name and the form of the product and creating necessary columns
    pr ,form = product_name(df)
    df_new["Product_Name"]=pr
    df_new["Form"] = form
    df_new["Annual_Quantity"]=df_new["Annual_Quantity"].fillna(method="backfill")
    return df_new[["Product_Name","Form","Tender_Id","Tender_Type","Client","Region","Start_Date","End_Date","Tender_Submission_Date","Winner","Loser",
                  "Winning_Price","Losing_Price","Annual_Quantity"]]


######### Folder Clean

def folder_model_clean(path,file_type="xlsx",save=False,name=None):
    """
    Utility:
    =========
    Cleans and concatenates all the raw files into a single file present in the Target folder.
    Arguements:
    """
    file_path = path+"/*."+file_type
    files = glob.glob(file_path)
    df_raw = pd.DataFrame()
    for i in files:
        print(i)
        try:
            df = pd.read_excel(i, sheet_name="Raw Data",header=1,engine="openpyxl")
        except:
            try:
                df = pd.read_excel(i, sheet_name="Raw data",header=1,engine="openpyxl")
            except:
                df = pd.read_excel(i, sheet_name="Raw ",header=1,engine="openpyxl")
        df_new = data_clean(df)
        #print(df)
        df_raw = pd.concat([df_raw,df_new])
    if save:
        file_name = "/Processed/"+name+".xlsx"
        df_raw.to_excel(path+file_name)
    return df_raw

# Data collector

def df_collector(path,file_type="xlsx",save=False):
    """
    Utility: 
    ===========
    Raw file Concatenation in a given folder and if required saves the concatenated files in the given folder destination
    Arguements:
    ===========
    1. path: The path of the folder where the files are residing
    2. file type: xlsx or csv
    3. save : True or False
    """
    # Getting file paths that need to be collected of the specified 
    if file_type =="xlsx":
        file_paths = glob.glob(path+"/*."+file_type)
    else:
        file_paths = glob.glob(path+"/*.csv")
    #reading the files
    df_final = pd.DataFrame()
    for j in file_paths:
        try:
            df = pd.read_excel(j, sheet_name="Raw Data",header=1,engine="openpyxl")
        except:
            try:
                df = pd.read_excel(j, sheet_name="Raw data",header=1,engine="openpyxl")
            except:
                df = pd.read_excel(j, sheet_name="Raw",header=1,engine="openpyxl")
        #tracks the index of the Products file information
        track = []
        #Lists down the Names of the Products present in the Raw file
        name_list=[]
        for i in range(len(df)):
            #Confezione->Product Name
            if str(list(df.iloc[i])[0]).find("Confezione")==0:
                track.append(i)
                product_desc = str(list(df.iloc[i])[0]).split(" ")
                name = list(df.iloc[0])[0].split(" ")[1]
                #Gets the Name,Strength and Form of the Product 
                try:
                    name = name.split("-")[0]
                except:
                    name = name
                try:
                    power = product_desc[-3].replace(",",".")
                except:
                    power = product_desc[-3]
                if list(df.iloc[0])[0].find("OS")>0:
                    form = "OSD"
                elif list(df.iloc[0])[0].find("ORODISP")>0:
                    form = "OSD"
                else:
                    form = "INJECTABLE"
                name_list.append(name.upper()+" "+power)
        track.append(len(df))
        print("No of Potential Products in file:",len(track)-1)
        print(name_list)
        #Gets each sub product name from the raw file reads and fetches information.
        df_1=pd.DataFrame()
        for i in range(len(track)-1):
            df_new = df[track[i]:track[i+1]]
            df_new = data_clean(df_new)
            df_1=pd.concat([df_1,df_new])
        df_1["Tender_Id"]=list(df_1["Tender_Id"].convert_dtypes(int))
        df_final=pd.concat([df_final,df_1])
    return df_final


### Model Data

def model_data(df):
    """
    Arguements:
    1. df - The target Dataframe
    ===========
    Utility: This function takes the target data frame and adds the winner and the winning price of the tenders.
    """
    # collecys the winner names and loser names
    comp =list(df["Winner"].unique()) 
    comp.extend(list(df["Loser"].unique()))
    comp=(list(set(comp)))
    comp_clean = [x for x in comp if x==x] # cleans the duplicates
    df2 = df
    df2=df2["Tender_Id"]
    #print(df2.shape)
    for i in comp_clean:
        # Gets the subset of the dataset where i is the winner
        comp_df_win=df[df["Winner"]==i]
        comp_df_win[i]=comp_df_win["Winning_Price"] # winning price of the winners
        comp_df_lose =df[df["Loser"]==i] #similarly for the ith company when it is the loser 
        comp_df_lose[i] = comp_df_lose["Losing_Price"] # the losing peice
        comp_df = pd.concat([comp_df_win,comp_df_lose]) #combines the dataframe
        comp_df.drop_duplicates(subset=["Tender_Id"],inplace=True) # drop the duplicate Tender Id
        #Participant Status formulation
        status_col = i+"Pr.Status"
        comp_df[status_col]=1 
        comp_df = comp_df[["Tender_Id",i,status_col]]
        df2 = pd.merge(df2,comp_df,how="outer",on="Tender_Id")
    df_final=pd.merge(df,df2,how="outer",on=["Tender_Id"])
    df_final.fillna(0,inplace=True)# filling the places with zero where it has not participated
    #test
    df_final.drop_duplicates(subset=["Tender_Id"],inplace=True)
    return df_final,comp_clean

#### Model df_collector

def model_df_collector(df,save=False,path=None):
    """
    Arguements: 
    1. df - target data
    2. save - if True then saves the data
    3. path - provides the path where to be saved with the file name.
    """
    product_names = df["Product_Name"].unique() # getting the unique product names
    df_final = pd.DataFrame()
    comp = []
    for i in product_names:
        df_prod = df[df["Product_Name"]==i] #subsetting the total product
        df_prod_clean,comp_clean = model_data(df_prod) # calling the model_data function for the further cleaning
        comp.extend(comp_clean)
        df_final = pd.concat([df_final, df_prod_clean], axis=0, ignore_index=True)# concatening it for the above product
    df_final.drop(["Loser","Losing_Price"],axis=1,inplace = True)# droping the losers and the losing price
    win = list(df_final["Winner"])
    comp = [x for x in comp if x==x]
    for j in comp:
        # Win status formulation
        win_status = [1 if x==j else 0 for x in win]
        col = j+"_Win_status"
        df_final[col]=win_status
    df_final.fillna(0,inplace=True)#filling up the places with zero where the company has no win
    df_final["Proximity_Delivery"]= (df_final['Start_Date'] - df_final['Tender_Submission_Date']).dt.days #finding the proximity delivery and converting its datatypes into days
    df_final["Start_End_Date_Diff"] = (df_final['End_Date'] - df_final['Start_Date']).dt.days # tender duration formulation
    par_col=[]
    for i in df_final.columns:
        #findng the participation status columns
        if i.find("Pr.Status")>=0:
            par_col.append(i)
    df_final["#Participant"] =  df_final[par_col].astype(int).sum(axis=1)# summing up all the participant status columns to get the total number of participants in the tenders
    if save:
        #saving
        file_path = path+"/CombinedTestModelData.xlsx"
        df_final.to_excel(file_path,index=False)
    return df_final

#Analyse functions

def DRL_analyse(df,group_col):
    """
    Arguements:
    ===========
    1. df - The target dataframe
    2. group_col - The variable on which we want to run the analysis
    
    Utility:
    ========
    To structure a dataset for the univariate analysis formulation
    """
    df_ana = df.groupby(group_col).aggregate({group_col:len,"Dr Reddys S.r.l.Pr.Status":sum,"Dr Reddys S.r.l._Win_status":sum})
    df_ana.columns = ["#Tender","#DRL Participation","#DRL Win"]
    return df_ana[["#Tender","#DRL Participation","#DRL Win"]].fillna(0)



#Clubbing Functions

#Proximity Clubbing
def proximity_coding(s):
    if s<=2:
        return "low"
    elif s<=7:
        return "mid"
    else:
        return "high"
    
    
#Participant clubbing
def participant_clubbing(s):
    if s<=2:
        return "Low Competition"
    else:
        return "High Competition"
    
    
#Entry clubbing
def entry_clubbing(s):
    if s<=6:
        return "High"
    if s<=12:
        return "Mid"
    else:
        return "Low"
    
    
#Duration clubbing
def Tender_duration_club(s):
    if s<=3:
        return "Short"
    else:
        return "Long"
    
#client clubbing
def client_clubbing(s):
    top_comp = ["INTERCENT-ER","REGIONE SICILIANA - ASSESSORATO DELLA SALUTE","SO.RE.SA. SpA",
                "ARCA S.p.A.- Azienda Regionale Centrale Acquisti - CHIUSO VEDI ARIA SPA",
                "Società di Committenza Regione Piemonte SpA - SCR Piemonte SpA",
                "INNOVAPUGLIA SPA","UMBRIA SALUTE E SERVIZI S.C.A.R.L.",
                "REGIONE LAZIO","REGIONE VENETO - NON USARE VEDI AZIENDA ZERO",
               "REGIONE SARDEGNA"]
    if s in top_comp:
        return "Top10"
    else:
        return "Normal"

#All club-in compact function
def encoded_df(df):
    encoded_df = df
    encoded_df["Participant_Club"]=encoded_df["#Participant"].apply(participant_clubbing)
    encoded_df["Genric_Entry_Club"] = (encoded_df["#Months_G.E"]/30).apply(entry_clubbing)
    encoded_df["Proximity_Club"] = (encoded_df["Proximity_Delivery"]/30).apply(proximity_coding)
    encoded_df["Client_Club"] = encoded_df["Client"].apply(client_clubbing)
    encoded_df["Tender_Duration_Club"] = (encoded_df["Start_End_Date_Diff"]/365).apply(Tender_duration_club)
    encoded_df["Identifier"] = identity(encoded_df)
    return encoded_df

#Identifier Function
def identity(encode_model_data):
    """
    Arguements: encoded target data
    ===========
    Utility:
    ========
    To form the unique identifiers for the dataset.
    """
    iden = []
    for i in range(len(encode_model_data)):
        pr = list(encode_model_data["Product_Name"])
        id_no = list(encode_model_data["Tender_Id"])
        iden.append(pr[i]+str(id_no[i]))
    return iden

#Previous winning price function

def previous_winning_price(df1):
    """
    Arguements:The dataframe for which the previous winning price can be devised
    ==========
    Utility:
    ========
    To find the previous winning price for each of the tenders
    """
    df=df1
    prod_names = df["Product_Name"].unique()
    df_w=pd.DataFrame()
    for i in prod_names:
        prod_df = df[df["Product_Name"]==i]
        winning_pr = list(prod_df["Winning_Price"])
        prev_win_pr = [np.nan]
        for i in range(len(winning_pr)-1):
            prev_win_pr.append(winning_pr[i])
        prod_df["Previous_Winning_Price"]=prev_win_pr
        df_w = pd.concat([df_w,prod_df])
    return df_w

#Model Data Processing
def data_processor_form(s):
    """
    Utility: finds the dosage form of the products and encodes it as 1 if OSD and 2 if Injectables.
    """
    if s=="OSD":
        return 1
    else:
        return 2
    
def data_processor_tender_type(s):
    """
    Utility : encodes the tender type column of the data as 1 if regionale else 0.
    """
    if s=="Regionale":
        return 1
    else:
        return 2
def data_processor_client(s):
    """
    Utility: encodes the client as 1 if it is in top 10 else 0.
    """
    top_comp = ["INTERCENT-ER","REGIONE SICILIANA - ASSESSORATO DELLA SALUTE","SO.RE.SA. SpA",
                "ARCA S.p.A.- Azienda Regionale Centrale Acquisti - CHIUSO VEDI ARIA SPA",
                "Società di Committenza Regione Piemonte SpA - SCR Piemonte SpA",
                "INNOVAPUGLIA SPA","UMBRIA SALUTE E SERVIZI S.C.A.R.L.",
                "REGIONE LAZIO","REGIONE VENETO - NON USARE VEDI AZIENDA ZERO",
               "REGIONE SARDEGNA"]
    if s in top_comp:
        return 1
    else:
        return 2
    
def data_processor_participant(s):
    """
    Utility: Encodes as 1 if there are less than or equal to 2 participants else 2
    """
    if s<=2:
        return 1
    else:
        return 2

def data_processor_region(s):
    """
    Utility: Encodes the regions into four groups based on the univariate study.
    """
    grp_1=['Sicilia', 'Toscana', 'Campania','Emilia Romagna','Puglia']
    grp_2=['Piemonte','Veneto','Friuli Venezia Giulia','Umbria','Lazio','Liguria','Abruzzo',
           'Sardegna','Marche','Basilicata','Calabria']
    if s=="'Lombardia'":
        return 1
    elif s in grp_1:
        return 2
    elif s in grp_2:
        return 3
    else:
        return 4
    


## Win Probability Predictor

def visualise_winprob(df):
    """
    Arguements: The target dataframe
    Utility: Visulaisation of all the density plots of the continuous variables
    """
    fig, axes = plt.subplots(2, 2,figsize=(10,10))
    #create kdeplot in each subplot
    axes[0,0].set_title("Months Since first Participant Entry")
    sns.kdeplot(df["#Months_G.E"], ax=axes[0,0])
    axes[0,1].set_title("Tender Duration")
    sns.kdeplot(df["Tender_Duration"], ax=axes[0,1])
    axes[1,0].set_title("Previous Winning Price")
    sns.kdeplot(df["Previous_Winning_Price"], ax=axes[1,0])
    axes[1,1].set_title("Proximty of Delivery")
    sns.kdeplot(df["Proximity_Delivery"], ax=axes[1,1])
    plt.show()

    
def winprob_data_processor(df,inclusion_exclusion = True,DRL_Participation=False,visualize_numeric=False):
    """
    Arguements: 
    1. df - the target dataframe
    2. inclusion_exclusion - if true applies the inclusion exclusion criteras during the data formation
    3. DRL_Participation - if true concentrates only on the subset of the data where there is only DRL participation
    4. visulaise_numeric - if true adds the visulaisation of the continuous variables alongwith.
    ===========
    Utility: Formation of the model data for win probability analysis
    """
    data = encoded_df(df) # calling the encoded_df finction over the target data to get the model specific encodings.
    if DRL_Participation:
        data = df[df["Dr Reddys S.r.l.Pr.Status"]==1] # getting the dataset subset where DRl participation is positive.
    if inclusion_exclusion:
        data = data[(data["Proximity_Delivery"]>0) &(data["#Months_G.E"]>0)] # specific cleaning on the basis of inclusion exclusion criteras.
    data = data.fillna(0) # filling up the na values with zero.
    model_col = ["Identifier","Dr Reddys S.r.l._Win_status","Form","Region","Tender_Type","Client","#Participant",
            "Proximity_Delivery","Start_End_Date_Diff","Previous_Winning_Price","#Months_G.E"] #specifing the columns necessary for modelling
    data = data[model_col]
    # Apllyong all the data processing using the pre-defined data processing critereas
    data["Region"] = data["Region"].apply(data_processor_region)
    data["Client"] = data["Client"].apply(data_processor_client)
    data["Tender_Type"] = data["Tender_Type"].apply(data_processor_tender_type)
    data["Form"] = data["Form"].apply(data_processor_form)
    data["#Participant"] = data["#Participant"].apply(data_processor_participant)
    data["Proximity_Delivery"] = (data["Proximity_Delivery"]/30)# conversion of days into months
    data["Start_End_Date_Diff"] = (data["Start_End_Date_Diff"]/365)# conversion of days into years
    data["#Months_G.E"] = (data["#Months_G.E"]/30) # conversion of days into months
    data.columns=["Identifier","DRL_Win_Flag","Form","Region"," Tender_Type","Client","#Participant",
            "Proximity_Delivery","Tender_Duration","Previous_Winning_Price","#Months_G.E"]#renaming the columns specifically
    if visualize_numeric:
        visualise_winprob(data)
    print(data.shape)#print the shape of the data
    return data

def previous_winning_price(df1):
    """
    Arguements: The dataframe for which the previous winning price has to be found.
    Utility: Getting the previous winning price of the tenders in the data.
    """
    df=df1
    prod_names = df["Product_Name"].unique()
    df_w=pd.DataFrame()
    for i in prod_names:
        prod_df = df[df["Product_Name"]==i]
        winning_pr = list(prod_df["Winning_Price"])
        prev_win_pr = [np.nan]
        for i in range(len(winning_pr)-1):
            prev_win_pr.append(winning_pr[i])
        prod_df["Previous_Winning_Price"]=prev_win_pr
        df_w = pd.concat([df_w,prod_df])
    return df_w

def price_data_processor(df,inclusion_exclusion = True,DRL_Participation=False,DRL_Win=False,visualize_numeric=False):
    """
    Arguements: 
    1. df - the target dataframe
    2. inclusion_exclusion - if true applies the inclusion exclusion criteras during the data formation
    3. DRL_Participation - if true concentrates only on the subset of the data where there is only DRL participation
    4. visulaise_numeric - if true adds the visulaisation of the continuous variables alongwith.
    ===========
    Utility: Formation of the model data for price prediction data
    """
    data = dh.encoded_df(df)# calling the encoded_df finction over the target data to get the model specific encodings.
    if DRL_Participation:
        data = df[df["Dr Reddys S.r.l.Pr.Status"]==1]# getting the dataset subset where DRl participation is positive.
    if DRL_Win:
        data = df[df["Dr Reddys S.r.l._Win_status"]==1]
    if inclusion_exclusion:
        data = data[(data["Proximity_Delivery"]>0) &(data["#Months_G.E"]>0)]# specific cleaning on the basis of inclusion exclusion criteras.
    data = data.fillna(0)# filling up the na values with zero.
    model_col = ["Identifier","Dr Reddys S.r.l._Win_status","Form","Region","Tender_Type","Client","#Participant","Winning_Price",
            "Proximity_Delivery","Start_End_Date_Diff","Previous_Winning_Price","#Months_G.E"]#specifing the columns necessary for modelling
    data = data[model_col]
    # Apllyong all the data processing using the pre-defined data processing critereas
    data["Region"] = data["Region"].apply(dh.data_processor_region)
    data["Client"] = data["Client"].apply(dh.data_processor_client)
    data["Tender_Type"] = data["Tender_Type"].apply(dh.data_processor_tender_type)
    data["Form"] = data["Form"].apply(dh.data_processor_form)
    data["#Participant"] = data["#Participant"].apply(dh.data_processor_participant)
    data["Proximity_Delivery"] = (data["Proximity_Delivery"]/30)# conversion of days into months
    data["Start_End_Date_Diff"] = (data["Start_End_Date_Diff"]/356)# conversion of days into years
    data["#Months_G.E"] = (data["#Months_G.E"]/30) # conversion of days into months
    data.columns=["Identifier","DRL_Win_Flag","Form","Region"," Tender_Type","Client","#Participant","Winning_Price",
            "Proximity_Delivery","Tender_Duration","Previous_Winning_Price","#Months_G.E"]#renaming the columns specifically
    if visualize_numeric:
        visualise_winprob(data)
    print(data.shape)#getting the datset name
    return data