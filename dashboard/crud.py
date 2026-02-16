import streamlit as st
import requests
import pandas as pd
import datetime
import sqlparse


API_URL = "http://127.0.0.1:8000/api/trips/"

st.title("CRUD")

#تابعی برای نشان دادن کوئری
def show_sql_log(response_json):
    if isinstance(response_json, dict) and "sql_query" in response_json:
        formatted_sql = sqlparse.format(response_json["sql_query"], reindent=True, keyword_case='upper')
        st.info("Executed SQL:")
        st.code(formatted_sql, language="sql")


tab1, tab2, tab3, tab4 = st.tabs(["List & Filter", "Create Trip", "Update Status", "Delete Trip"])


with tab1:
    st.header("Trips")
    cust_filter = st.text_input("Enter Customer ID to filter:")

    if st.button("Search"):
        

        params = {}
        if cust_filter:
            params['customer_id'] = cust_filter.strip()
            
        try:
            response = requests.get(API_URL, params=params)
            
            if response.status_code == 200:
                result = response.json()
                
                show_sql_log(result)
                
                trips_list = []
                if isinstance(result, dict) and "data" in result:
                    trips_list = result["data"]
                elif isinstance(result, dict) and "results" in result:
                    trips_list = result["results"]
                elif isinstance(result, list):
                    trips_list = result


                if trips_list:
                    df = pd.DataFrame(trips_list)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.warning("There was no data matching your filter.")
                    
            else:
                st.error(f"Error {response.status_code}: {response.text}")
                
        except Exception as e:
            st.error(f"Error: {e}")
            st.info("DRF must be running.")


#ساخت سفر
with tab2:
    st.header("Create New Trip")
    
    
    with st.form("create_form"):
        col1, col2 = st.columns(2)
        with col1:
            d_date = st.date_input("Date", datetime.date.today())
            d_time = st.time_input("Time", datetime.datetime.now().time())
            vehicle = st.selectbox("Vehicle Type", ["Auto", "Prime Sedan", "Mini", "UberX"])
        with col2:
            pay_method = st.selectbox("Payment Method", ["Cash", "Credit Card", "UPI", "Wallet"])
            cust_rating = st.number_input("Customer Rating", min_value=1.0, max_value=5.0, value=5.0, step=0.1)
            cust_id = st.text_input("Customer ID")
            
        submit = st.form_submit_button("Create Trip")
        
        if submit:
            formatted_time = d_time.strftime("%H:%M:%S")
            payload = {
                "date": str(d_date),
                "time": formatted_time, 
                "vehicle_type": vehicle,
                "payment_method": pay_method,
                "customer_rating": cust_rating,
                "customer_id": cust_id,
                "booking_value": 0,
                "ride_distance": 0
            }
            res = requests.post(API_URL, json=payload)
            
            if res.status_code == 201:
                
                data = res.json()
                st.success(f"Trip created successfully, Generated ID: **{data['data']['booking_id']}**")
                # نمایش کوئری
                show_sql_log(data)
            else:
                st.error(f"Error: {res.text}")

# اپدیت سفر
with tab3:
    st.header("Update Booking Status")
    
    u_id = st.text_input("Enter Booking ID:")
    status_options = ["Cancelled by Driver", "Cancelled by Customer", "Incomplete"]
    new_status = st.selectbox("New Status", status_options)
    
    if st.button("Update"):
        if u_id:
            url = f"{API_URL}{u_id}/"

            update_payload = {"booking_status": new_status}
            
            if new_status == "Cancelled by Driver":
                update_payload["cancelled_rides_by_driver"] = 1
                
            elif new_status == "Cancelled by Customer":
                update_payload["cancelled_rides_by_customer"] = 1
                
            elif new_status == "Incomplete":
                update_payload["incomplete_rides"] = 1
            
            try:
                res = requests.patch(url, json=update_payload)
                
                if res.status_code == 200:
                    st.success(f"Status updated to '{new_status}'")
                    
                    st.write("Updated Fields:", update_payload)
                    
                    # نمایش کوئری SQL
                    show_sql_log(res.json())
                    
                elif res.status_code == 404:
                    st.error("Booking ID not found")
                else:
                    st.error(f"Error: {res.text}")
            except Exception as e:
                st.error(f"Connection Error: {e}")

# حذف سفر
with tab4:
    st.header("Delete Trip")
    
    d_id = st.text_input("Enter Booking ID :", key="del_input")
    
    if st.button("Delete", type="primary"):
        if d_id:
            url = f"{API_URL}{d_id}/"
            res = requests.delete(url)
    
            if res.status_code == 200:
                st.success("Record has been deleted")
                # نمایش کوئری
                show_sql_log(res.json())
            elif res.status_code == 404:
                st.error("Booking ID not found")
            else:
                st.error(f"Error: {res.text}")