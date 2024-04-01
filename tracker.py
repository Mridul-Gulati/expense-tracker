import datetime
import gspread
import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pretty_html_table import build_table

# st.secrets = toml.load("st.secrets.toml")
st.title("Expense Tracker")
st.subheader("Made by Mridul Gulati")

# user = st.selectbox("Select User", ["Mridul", "Rajvi"])
# password = st.text_input("Enter Password", type="password")

# if user == "Mridul" and password == "Mridul18!":
if 'remaining_balance' not in st.session_state:
    st.session_state.remaining_balance = 0
if 'summary' not in st.session_state:
    st.session_state.summary = pd.DataFrame()
if 'amount_to_be_reimbursed' not in st.session_state:
    st.session_state.amount_to_be_reimbursed = pd.DataFrame()
if 'total_amount_to_be_reimbursed' not in st.session_state:
    st.session_state.total_amount_to_be_reimbursed = 0
mode = st.selectbox("Select Mode", ["Incoming", "Outgoing"])
category = [None, "Miscellaneous", "Travel", "Food", "Shopping", "Investment", "Salary","Gift"]
selected_category = st.selectbox("Select the category", category)
reimbursed = st.checkbox("Will be Reimbursed?")
amt = st.number_input("Enter the amount", min_value=0, step=1)
description = st.text_input("Enter a description (optional)")
if mode == "Outgoing":
    amt = -1 * amt

if st.button("Add Transaction"):
    with st.spinner("Adding..."):
        try:
            client = gspread.service_account_from_dict({
                "type": st.secrets["connections"]["gsheets"]["type"],
                "project_id": st.secrets["connections"]["gsheets"]["project_id"],
                "private_key_id": st.secrets["connections"]["gsheets"]["private_key_id"],
                "private_key": st.secrets["connections"]["gsheets"]["private_key"],
                "client_email": st.secrets["connections"]["gsheets"]["client_email"],
                "client_id": st.secrets["connections"]["gsheets"]["client_id"],
                "auth_uri": st.secrets["connections"]["gsheets"]["auth_uri"],
                "token_uri": st.secrets["connections"]["gsheets"]["token_uri"],
                "auth_provider_x509_cert_url": st.secrets["connections"]["gsheets"]["auth_provider_x509_cert_url"],
                "client_x509_cert_url": st.secrets["connections"]["gsheets"]["client_x509_cert_url"]
            })
            spreadsheet_key = st.secrets["connections"]["gsheets"]["spreadsheet"]
            worksheet_index = int(st.secrets["connections"]["gsheets"]["worksheet"])
            sheet = client.open_by_key(spreadsheet_key).get_worksheet(worksheet_index)
        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.stop()
        last_row = len(sheet.col_values(6))
        last_remaining_balance = sheet.cell(last_row, 6).value
        
        remaining_balance = float(last_remaining_balance) if last_remaining_balance != "Remaining Balance" else 5000        
        if mode == "Outgoing" and selected_category != "Investment" and reimbursed == False:
            remaining_balance += amt
        elif mode == "Incoming":
            remaining_balance += 0
        
        if selected_category == "Salary":
            remaining_balance = 5000
            if last_row > 1:
                previous_row_savings = float(sheet.cell(last_row, 6).value)
            else:
                previous_row_savings = 0
                
            row_data = [str(datetime.datetime.now()), mode, selected_category, amt, reimbursed, remaining_balance, description, previous_row_savings]
        else:
            row_data = [str(datetime.datetime.now()), mode, selected_category, amt, reimbursed, remaining_balance, description]
        sheet.append_row(row_data)
        if remaining_balance <= 1000 and remaining_balance > 0:
            st.warning(f"Remaining balance is {remaining_balance}, Be careful!")
        elif remaining_balance <= 0:
            st.error(f"Remaining balance is {remaining_balance}, Overbudget!")
        st.success("Transaction added successfully!")
        st.session_state["remaining_balance"] = remaining_balance

def overwrite_worksheet_with_df(worksheet, df):
    try:
        worksheet.clear()

        values = df.values.tolist()

        worksheet.update("A1", values)
    except Exception as e:
        st.error(f"An error occurred: {e}")

if st.button("Settle Reimbursement"):
    with st.spinner("Settling..."):
        try:
            client = gspread.service_account_from_dict({
                "type": st.secrets["connections"]["gsheets"]["type"],
                "project_id": st.secrets["connections"]["gsheets"]["project_id"],
                "private_key_id": st.secrets["connections"]["gsheets"]["private_key_id"],
                "private_key": st.secrets["connections"]["gsheets"]["private_key"],
                "client_email": st.secrets["connections"]["gsheets"]["client_email"],
                "client_id": st.secrets["connections"]["gsheets"]["client_id"],
                "auth_uri": st.secrets["connections"]["gsheets"]["auth_uri"],
                "token_uri": st.secrets["connections"]["gsheets"]["token_uri"],
                "auth_provider_x509_cert_url": st.secrets["connections"]["gsheets"]["auth_provider_x509_cert_url"],
                "client_x509_cert_url": st.secrets["connections"]["gsheets"]["client_x509_cert_url"]
            })
            spreadsheet_key = st.secrets["connections"]["gsheets"]["spreadsheet"]
            worksheet_index = int(st.secrets["connections"]["gsheets"]["worksheet"])
            sheet = client.open_by_key(spreadsheet_key).get_worksheet(worksheet_index)
        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.stop()
        rows = sheet.get_all_values()
        df = pd.DataFrame(rows[1:], columns=rows[0])
        df_filtered = df[df["Will be Reimbursed?"] != "TRUE"]
        overwrite_worksheet_with_df(sheet, df_filtered)
        st.success("Reimbursement settled successfully!")
if 'clicked' not in st.session_state:
    st.session_state.clicked = False

def click_button():
    st.session_state.clicked = True
if 'summary_but' not in st.session_state:
    st.session_state.summary_but = False

summary_button = st.button("Summary", on_click = click_button)

if summary_button or st.session_state.summary_but:
    st.session_state.summary_but = True
    with st.spinner("Loading..."):
        try:
            client = gspread.service_account_from_dict({
                "type": st.secrets["connections"]["gsheets"]["type"],
                "project_id": st.secrets["connections"]["gsheets"]["project_id"],
                "private_key_id": st.secrets["connections"]["gsheets"]["private_key_id"],
                "private_key": st.secrets["connections"]["gsheets"]["private_key"],
                "client_email": st.secrets["connections"]["gsheets"]["client_email"],
                "client_id": st.secrets["connections"]["gsheets"]["client_id"],
                "auth_uri": st.secrets["connections"]["gsheets"]["auth_uri"],
                "token_uri": st.secrets["connections"]["gsheets"]["token_uri"],
                "auth_provider_x509_cert_url": st.secrets["connections"]["gsheets"]["auth_provider_x509_cert_url"],
                "client_x509_cert_url": st.secrets["connections"]["gsheets"]["client_x509_cert_url"]
            })
            spreadsheet_key = st.secrets["connections"]["gsheets"]["spreadsheet"]
            worksheet_index = int(st.secrets["connections"]["gsheets"]["worksheet"])
            sheet = client.open_by_key(spreadsheet_key).get_worksheet(worksheet_index)
        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.stop()
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        df['Savings'] = pd.to_numeric(df['Savings'], errors='coerce').fillna(0)
        outgoing_transactions = df[df['Amount'] < 0]
        
        reimbursed_transactions = outgoing_transactions[outgoing_transactions['Will be Reimbursed?'] == "TRUE"]
        
        amount_to_be_reimbursed = reimbursed_transactions[['Description','Amount']]
        st.session_state["amount_to_be_reimbursed"] = amount_to_be_reimbursed

        outgoing_transactions = outgoing_transactions[outgoing_transactions['Will be Reimbursed?'] == "FALSE"]
        
        summary = outgoing_transactions.groupby('Category')['Amount'].sum().reset_index()
        st.session_state["summary"] = summary

        total_amount_to_be_reimbursed = amount_to_be_reimbursed['Amount'].sum()
        st.session_state["total_amount_to_be_reimbursed"] = total_amount_to_be_reimbursed
        st.subheader("Summary:")
        st.dataframe(summary)
        
        st.subheader("Transactions to be Reimbursed:")
        st.dataframe(amount_to_be_reimbursed)
        
        st.subheader("Total Amount to be Reimbursed:")
        st.success(-1 * total_amount_to_be_reimbursed)
        st.subheader("Total Savings:")

        df['Created At'] = pd.to_datetime(df['Created At'])

        # Define time frame options including Monthly
        time_frames = ["Monthly", "Quarterly", "Half-Yearly", "Yearly"]

        # Selectbox for choosing time frame
        selected_time_frame = st.selectbox("Select Time Frame", time_frames)

        # Filter rows where category is 'Salary'
        salary_rows = df[df['Category'] == 'Salary']

        # Resampling data based on selected time frame
        if selected_time_frame == "Monthly":
            resampled_data = salary_rows.set_index('Created At').resample('M').sum().reset_index()
            period_offset = pd.DateOffset(months=1)
            x_axis_label = "Month"
        elif selected_time_frame == "Quarterly":
            resampled_data = salary_rows.set_index('Created At').resample('Q').sum().reset_index()
            period_offset = pd.DateOffset(months=3)
            x_axis_label = "Quarter"
        elif selected_time_frame == "Half-Yearly":
            resampled_data = salary_rows.set_index('Created At').resample('6M').sum().reset_index()
            period_offset = pd.DateOffset(months=6)
            x_axis_label = "Half-Year"
        else:
            resampled_data = salary_rows.set_index('Created At').resample('Y').sum().reset_index()
            period_offset = pd.DateOffset(years=1)
            x_axis_label = "Year"

        # Subtracting one period from the 'Created At' date for the resampled data
        resampled_data['Previous Period'] = (resampled_data['Created At'] - period_offset).dt.strftime('%b %Y')

        # Plotting the selected time frame savings
        fig = px.bar(resampled_data, x='Previous Period', y='Savings', title=f"{selected_time_frame} Savings of Previous Period",
                    labels={"Previous Period": x_axis_label, "Savings": "Savings"})
        fig.update_xaxes(title_text=x_axis_label)
        fig.update_yaxes(title_text="Savings")

        # Displaying the plot
        st.plotly_chart(fig)
        st.subheader("Get Invoice on mail:")

if st.session_state.clicked:
    if st.button("Send Invoice"):
        with st.spinner("Sending..."):
            try:
                body = "Invoice Summary:<br><br>"
                summary = st.session_state["summary"]
                amount_to_be_reimbursed = st.session_state["amount_to_be_reimbursed"]
                total_amount_to_be_reimbursed = st.session_state["total_amount_to_be_reimbursed"]
                total_remaining_balance = st.session_state["remaining_balance"]
                summary_table = build_table(summary, 'blue_light')
                transactions_table = build_table(amount_to_be_reimbursed, 'blue_light')
                body += f"Total amount spent per category:\n{summary_table}<br><br>"
                
                body += f"Total transactions to be reimbursed: {transactions_table}<br>"
                body += f"Total amount to be reimbursed: {total_amount_to_be_reimbursed}<br>"
                body += f"Total remaining balance: {total_remaining_balance}<br>"
                # Create the email message
                msg = MIMEMultipart()
                msg['From'] = "mridulgulati18@gmail.com"
                msg['To'] = "mridulgulati18@gmail.com" 
                msg['Subject'] = "Invoice"
                
                # Attach the body as text
                msg.attach(MIMEText(body, "html"))
                
                # Send the email using SMTP
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login("mridulgulati18@gmail.com", "exoc dogl hzug gmdn")
                server.sendmail("mridulgulati18@gmail.com", "mridulgulati18@gmail.com", msg.as_string())
                server.quit()
                
                st.success("Invoice Sent Successfully!")
            except Exception as e:
                st.error(f"An error occurred: {e}")


# if user == "Rajvi" and password == "test123":
#     if 'remaining_balance' not in st.session_state:
#         st.session_state.remaining_balance = 0
#     if 'summary' not in st.session_state:
#         st.session_state.summary = pd.DataFrame()
#     if 'amount_to_be_reimbursed' not in st.session_state:
#         st.session_state.amount_to_be_reimbursed = pd.DataFrame()
#     if 'total_amount_to_be_reimbursed' not in st.session_state:
#         st.session_state.total_amount_to_be_reimbursed = 0
#     mode = st.selectbox("Select Mode", ["Incoming", "Outgoing"])
#     category = [None, "Miscellaneous", "Travel", "Food", "Shopping", "Investment", "Salary","Gift"]
#     selected_category = st.selectbox("Select the category", category)
#     reimbursed = st.checkbox("Will be Reimbursed?")
#     amt = st.number_input("Enter the amount", min_value=0, step=1)
#     description = st.text_input("Enter a description (optional)")
#     if mode == "Outgoing":
#         amt = -1 * amt

#     if st.button("Add Transaction"):
#         with st.spinner("Adding..."):
#             try:
#                 client = gspread.service_account_from_dict({
#                     "type": st.secrets["connections"]["gsheets_user2"]["type"],
#                     "project_id": st.secrets["connections"]["gsheets_user2"]["project_id"],
#                     "private_key_id": st.secrets["connections"]["gsheets_user2"]["private_key_id"],
#                     "private_key": st.secrets["connections"]["gsheets_user2"]["private_key"],
#                     "client_email": st.secrets["connections"]["gsheets_user2"]["client_email"],
#                     "client_id": st.secrets["connections"]["gsheets_user2"]["client_id"],
#                     "auth_uri": st.secrets["connections"]["gsheets_user2"]["auth_uri"],
#                     "token_uri": st.secrets["connections"]["gsheets_user2"]["token_uri"],
#                     "auth_provider_x509_cert_url": st.secrets["connections"]["gsheets_user2"]["auth_provider_x509_cert_url"],
#                     "client_x509_cert_url": st.secrets["connections"]["gsheets_user2"]["client_x509_cert_url"]
#                 })
#                 spreadsheet_key = st.secrets["connections"]["gsheets_user2"]["spreadsheet"]
#                 worksheet_index = int(st.secrets["connections"]["gsheets_user2"]["worksheet"])
#                 sheet = client.open_by_key(spreadsheet_key).get_worksheet(worksheet_index)
#             except Exception as e:
#                 st.error(f"An error occurred: {e}")
#                 st.stop()
#             last_row = len(sheet.col_values(6))
#             last_remaining_balance = sheet.cell(last_row, 6).value
            
#             remaining_balance = float(last_remaining_balance) if last_remaining_balance != "Remaining Balance" else 5000        
#             if mode == "Outgoing" and selected_category != "Investment":
#                 remaining_balance += amt
#             elif mode == "Incoming":
#                 remaining_balance += 0
            
#             if selected_category == "Salary":
#                 remaining_balance = 5000
#                 if last_row > 1:
#                     previous_row_savings = float(sheet.cell(last_row, 6).value)
#                 else:
#                     previous_row_savings = 0
                    
#                 row_data = [str(datetime.datetime.now()), mode, selected_category, amt, reimbursed, remaining_balance, description, previous_row_savings]
#             else:
#                 row_data = [str(datetime.datetime.now()), mode, selected_category, amt, reimbursed, remaining_balance, description]
#             sheet.append_row(row_data)
#             if remaining_balance <= 1000 and remaining_balance > 0:
#                 st.warning(f"Remaining balance is {remaining_balance}, Be careful!")
#             elif remaining_balance <= 0:
#                 st.error(f"Remaining balance is {remaining_balance}, Overbudget!")
#             st.success("Transaction added successfully!")
#             st.session_state["remaining_balance"] = remaining_balance
#     if 'clicked' not in st.session_state:
#         st.session_state.clicked = False

#     def click_button():
#         st.session_state.clicked = True
#     if 'summary_but' not in st.session_state:
#         st.session_state.summary_but = False

#     summary_button = st.button("Summary", on_click = click_button)

#     if summary_button or st.session_state.summary_but:
#         st.session_state.summary_but = True
#         with st.spinner("Loading..."):
#             try:
#                 client = gspread.service_account_from_dict({
#                     "type": st.secrets["connections"]["gsheets_user2"]["type"],
#                     "project_id": st.secrets["connections"]["gsheets_user2"]["project_id"],
#                     "private_key_id": st.secrets["connections"]["gsheets_user2"]["private_key_id"],
#                     "private_key": st.secrets["connections"]["gsheets_user2"]["private_key"],
#                     "client_email": st.secrets["connections"]["gsheets_user2"]["client_email"],
#                     "client_id": st.secrets["connections"]["gsheets_user2"]["client_id"],
#                     "auth_uri": st.secrets["connections"]["gsheets_user2"]["auth_uri"],
#                     "token_uri": st.secrets["connections"]["gsheets_user2"]["token_uri"],
#                     "auth_provider_x509_cert_url": st.secrets["connections"]["gsheets_user2"]["auth_provider_x509_cert_url"],
#                     "client_x509_cert_url": st.secrets["connections"]["gsheets_user2"]["client_x509_cert_url"]
#                 })
#                 spreadsheet_key = st.secrets["connections"]["gsheets_user2"]["spreadsheet"]
#                 worksheet_index = int(st.secrets["connections"]["gsheets_user2"]["worksheet"])
#                 sheet = client.open_by_key(spreadsheet_key).get_worksheet(worksheet_index)
#             except Exception as e:
#                 st.error(f"An error occurred: {e}")
#                 st.stop()
#             data = sheet.get_all_records()
#             df = pd.DataFrame(data)
#             df['Savings'] = pd.to_numeric(df['Savings'], errors='coerce').fillna(0)
#             outgoing_transactions = df[df['Amount'] < 0]
            
#             reimbursed_transactions = outgoing_transactions[outgoing_transactions['Will be Reimbursed?'] == "TRUE"]
            
#             amount_to_be_reimbursed = reimbursed_transactions[['Description','Amount']]
#             st.session_state["amount_to_be_reimbursed"] = amount_to_be_reimbursed

#             outgoing_transactions = outgoing_transactions[outgoing_transactions['Will be Reimbursed?'] == "FALSE"]
            
#             summary = outgoing_transactions.groupby('Category')['Amount'].sum().reset_index()
#             st.session_state["summary"] = summary

#             total_amount_to_be_reimbursed = amount_to_be_reimbursed['Amount'].sum()
#             st.session_state["total_amount_to_be_reimbursed"] = total_amount_to_be_reimbursed
#             st.subheader("Summary:")
#             st.dataframe(summary)
            
#             st.subheader("Transactions to be Reimbursed:")
#             st.dataframe(amount_to_be_reimbursed)
            
#             st.subheader("Total Amount to be Reimbursed:")
#             st.success(-1 * total_amount_to_be_reimbursed)
#             st.subheader("Total Savings:")

#             df['Created At'] = pd.to_datetime(df['Created At'])

#             # Define time frame options including Monthly
#             time_frames = ["Monthly", "Quarterly", "Half-Yearly", "Yearly"]

#             # Selectbox for choosing time frame
#             selected_time_frame = st.selectbox("Select Time Frame", time_frames)

#             # Filter rows where category is 'Salary'
#             salary_rows = df[df['Category'] == 'Salary']

#             # Resampling data based on selected time frame
#             if selected_time_frame == "Monthly":
#                 resampled_data = salary_rows.set_index('Created At').resample('M').sum().reset_index()
#                 period_offset = pd.DateOffset(months=1)
#                 x_axis_label = "Month"
#             elif selected_time_frame == "Quarterly":
#                 resampled_data = salary_rows.set_index('Created At').resample('Q').sum().reset_index()
#                 period_offset = pd.DateOffset(months=3)
#                 x_axis_label = "Quarter"
#             elif selected_time_frame == "Half-Yearly":
#                 resampled_data = salary_rows.set_index('Created At').resample('6M').sum().reset_index()
#                 period_offset = pd.DateOffset(months=6)
#                 x_axis_label = "Half-Year"
#             else:
#                 resampled_data = salary_rows.set_index('Created At').resample('Y').sum().reset_index()
#                 period_offset = pd.DateOffset(years=1)
#                 x_axis_label = "Year"

#             # Subtracting one period from the 'Created At' date for the resampled data
#             resampled_data['Previous Period'] = (resampled_data['Created At'] - period_offset).dt.strftime('%b %Y')

#             # Plotting the selected time frame savings
#             fig = px.bar(resampled_data, x='Previous Period', y='Savings', title=f"{selected_time_frame} Savings of Previous Period",
#                         labels={"Previous Period": x_axis_label, "Savings": "Savings"})
#             fig.update_xaxes(title_text=x_axis_label)
#             fig.update_yaxes(title_text="Savings")

#             # Displaying the plot
#             st.plotly_chart(fig)
#             st.subheader("Get Invoice on mail:")

#     if st.session_state.clicked:
#         if st.button("Send Invoice"):
#             with st.spinner("Sending..."):
#                 try:
#                     body = "Invoice Summary:<br><br>"
#                     summary = st.session_state["summary"]
#                     amount_to_be_reimbursed = st.session_state["amount_to_be_reimbursed"]
#                     total_amount_to_be_reimbursed = st.session_state["total_amount_to_be_reimbursed"]
#                     total_remaining_balance = st.session_state["remaining_balance"]
#                     summary_table = build_table(summary, 'blue_light')
#                     transactions_table = build_table(amount_to_be_reimbursed, 'blue_light')
#                     body += f"Total amount spent per category:\n{summary_table}<br><br>"
                    
#                     body += f"Total transactions to be reimbursed: {transactions_table}<br>"
#                     body += f"Total amount to be reimbursed: {total_amount_to_be_reimbursed}<br>"
#                     body += f"Total remaining balance: {total_remaining_balance}<br>"
#                     # Create the email message
#                     msg = MIMEMultipart()
#                     msg['From'] = "mridulgulati18@gmail.com"
#                     msg['To'] = "rajvimehta775@gmail.com" 
#                     msg['Subject'] = "Invoice"
                    
#                     # Attach the body as text
#                     msg.attach(MIMEText(body, "html"))
                    
#                     # Send the email using SMTP
#                     server = smtplib.SMTP('smtp.gmail.com', 587)
#                     server.starttls()
#                     server.login("mridulgulati18@gmail.com", "exoc dogl hzug gmdn")
#                     server.sendmail("mridulgulati18@gmail.com", "rajvimehta775@gmail.com", msg.as_string())
#                     server.quit()
                    
#                     st.success("Invoice Sent Successfully!")
#                 except Exception as e:
#                     st.error(f"An error occurred: {e}")

    