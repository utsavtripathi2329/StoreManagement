import streamlit as st
from datetime import date
import pandas as pd
from google.oauth2 import service_account
from gsheetsdb import connect

# Create a connection object.
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
    ],
)
conn = connect(credentials=credentials)

sheet_url = st.secrets["private_gsheets_url"]
rows = run_query(f'SELECT * FROM "{sheet_url}"')

for row in rows:
    st.write(f"{row.name} has a :{row.pet}:")

date = date.today()

dateStr = date.strftime("%d-%m-%Y")

inventory = pd.read_excel('./files/Inventory.xlsx')

sale = pd.read_excel('./files/Sales.xlsx')

st.title('Utsav\'s Store')

st.header('_Inventory & Sales_')

st.write(f'Today\'s Date: {dateStr}')

with st.form("sales",clear_on_submit = True):
    st.write("Input Sales Data")
    item_code = int(st.number_input("Enter Item Code:", value = 0, format='%d'))
    item_qty = int(st.number_input("Enter Item Quantity:", value = 0, format='%d'))
    
    Item_Code = inventory.iloc[item_code][0]
    Item = inventory.iloc[item_code][1]
    Price = inventory.iloc[item_code][3]
    Amount = item_qty * Price
    
    submitted = st.form_submit_button("Submit")
    if submitted:
        sale_var = pd.DataFrame([[dateStr, Item_Code, Item, item_qty, Price, Amount]],columns=sale.columns)
        sale = sale.append(sale_var)

        curr_qty = inventory['Quantity'][Item_Code]
        inv_upd = pd.DataFrame({'Quantity': [curr_qty - item_qty]}, index=[Item_Code])
        inventory.update(inv_upd)

inventory.to_excel('./files/Inventory.xlsx', index=False)

st.sidebar.write('Inventory')
st.sidebar.dataframe(inventory.loc[:,'Item':'Price'])

sale.to_excel('./files/Sales.xlsx', index=False)

st.subheader(f'Sale Summary for {dateStr}:')

sale_summary = pd.read_excel('./files/Sales.xlsx')

sale_summary_today = sale_summary[sale_summary['Date']==dateStr]
st.dataframe(sale_summary_today.loc[:,'Item Code':'Amount'])
Total_Sales = sale_summary['Amount'].sum(axis=0)
st.sidebar.subheader(f'Total Sales: INR {Total_Sales}/-')
Total_Sales_Today = sale_summary_today['Amount'].sum(axis=0)
st.sidebar.subheader(f'Today\'s Total Sales: INR {Total_Sales_Today}/-')
