import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
from ai import get_sql_response
import chromadb

st.title("Uber")

@st.cache_data
def load_data():
    
    db_connection_str = 'postgresql://uber_user:pass@localhost:5432/uber_db'
    db_connection = create_engine(db_connection_str)
    
    
    query = 'SELECT * FROM "gold"."dataset"'
    df = pd.read_sql(query, db_connection)
    df['date'] = pd.to_datetime(df['date'])
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Error connecting to database: {e}")
    st.stop()


tab1, tab2, tab3 = st.tabs(["Analytics Data", "AI Assistant", "Semantic Search"])

with tab1:
    

    min_date = df['date'].min()
    max_date = df['date'].max()


    st.markdown("Filters")
    col_fil1, col_fil2 = st.columns(2)


    with col_fil1:
        all_vehicles = df['vehicle_type'].unique()
        selected_vehicles = st.multiselect(
            "Select Vehicle Type to filter",
            options=all_vehicles,
            default=all_vehicles
        )


    with col_fil2:
        date_input = st.date_input(
            "Select Date Range to filter",
            value=[min_date, max_date],
            min_value=min_date,
            max_value=max_date
        )


    if len(date_input) == 2:
        start_date, end_date = date_input
    else:
        start_date, end_date = date_input[0], date_input[0]


    start_ts = pd.to_datetime(start_date)
    end_ts = pd.to_datetime(end_date)
    
    filtered_df = df[
        (df['date'] >= start_ts) &
        (df['date'] <= end_ts) &
        (df['vehicle_type'].isin(selected_vehicles))
    ]

    st.markdown("---")


    if filtered_df.empty:
        st.warning("No data available based on current filters!")
    else:
        st.subheader("KPIs")
        col1, col2, col3, col4 = st.columns(4)

        total_bookings = len(filtered_df)
        successful_bookings = len(filtered_df[filtered_df['booking_status'] == 'Completed'])
        

        total_revenue = filtered_df['booking_value'].sum()
        success_rate = (successful_bookings / total_bookings * 100) if total_bookings > 0 else 0

        col1.metric("Total Bookings", f"{total_bookings:,}")
        col2.metric("Successful Trips", f"{successful_bookings:,}")
        col3.metric("Total Revenue", f"${total_revenue:,.2f}")
        col4.metric("Success Rate", f"{success_rate:.2f}%")


        st.markdown("---")

        st.subheader("Pie Charts")
        col_pie1, col_pie2 = st.columns(2)
        with col_pie1:
            st.subheader("Cancellation Reasons")
            cancelled_df = filtered_df[filtered_df['unified_cancellation_reason'].notnull()]
            if not cancelled_df.empty:
                fig_cancel = px.pie(cancelled_df, names='unified_cancellation_reason', hole=0.3)
                st.plotly_chart(fig_cancel, use_container_width=True)
            else:
                st.info("No cancellations found.")

        with col_pie2:
            st.subheader("Payment Methods")
            payment_met = filtered_df[filtered_df['payment_method'].notnull()]
            fig_payment = px.pie(payment_met, names='payment_method', hole=0.3)
            st.plotly_chart(fig_payment, use_container_width=True)

        st.markdown("---")


        st.subheader("Bar Charts")
        col_bar1, col_bar2 = st.columns(2)
        with col_bar1:
            st.subheader("Trips by Vehicle Type")

            completed_trips = filtered_df[filtered_df['booking_status'] == 'Completed']
            vehicle_counts = completed_trips['vehicle_type'].value_counts().reset_index()
            
            vehicle_counts.columns = ['vehicle_type', 'count']
            fig_vehicle = px.bar(vehicle_counts, x='vehicle_type', y='count', color='count')
            st.plotly_chart(fig_vehicle, use_container_width=True)

        with col_bar2:
            st.subheader("Average Ratings")
            avg_ratings = filtered_df.groupby('vehicle_type')[['driver_ratings', 'customer_rating']].mean().reset_index()
            avg_ratings_melted = avg_ratings.melt(id_vars='vehicle_type', var_name='Rating Type', value_name='Score')
            fig_rating = px.bar(avg_ratings_melted, x='vehicle_type', y='Score', color='Rating Type', barmode='group')
            st.plotly_chart(fig_rating, use_container_width=True)

        st.markdown("---")


        st.subheader("Linear Charts")
        col_line1, col_line2 = st.columns(2)
        with col_line1:
            day_order = ['Saturday', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
            daily_counts = filtered_df['day_of_week'].value_counts().reindex(day_order).reset_index()
            daily_counts.columns = ['Day', 'Trips']
            fig_days = px.line(daily_counts, x='Day', y='Trips', markers=True, title='Trips per Day of Week')
            st.plotly_chart(fig_days, use_container_width=True)

        with col_line2:
            if filtered_df['time'].dtype == 'object':
                filtered_df['hour'] = pd.to_datetime(filtered_df['time'].astype(str)).dt.hour
            else:
                filtered_df['hour'] = filtered_df['time'].apply(lambda x: x.hour if x else None)
            
            hourly_counts = filtered_df['hour'].value_counts().sort_index().reset_index()
            hourly_counts.columns = ['Hour', 'Trips']
            fig_hours = px.line(hourly_counts, x='Hour', y='Trips', markers=True, title='Peak Hours (0-23)')
            st.plotly_chart(fig_hours, use_container_width=True)


with tab2:
    st.header("Text to SQL")
    st.markdown("Ask your question.")
    

    user_query = st.text_input("", placeholder="Example: Show me top 5 trips with highest value")
    generate_btn = st.button("  Go  ", type="primary", )

    if generate_btn and user_query:

        raw_sql = get_sql_response(user_query)
            

        cleaned_sql = raw_sql.replace("```sql", "").replace("```", "").strip()

        
        st.info("Generated SQL:")
        st.code(cleaned_sql, language="sql")


        if "SELECT" in cleaned_sql.upper() and "DROP" not in cleaned_sql.upper():
            try:
                
                db_str = 'postgresql://uber_user:pass@localhost:5432/uber_db'
                engine = create_engine(db_str)
                    

                result_df = pd.read_sql(cleaned_sql, engine)

                st.success("Results:")

                st.dataframe(result_df, use_container_width=True)
                

                
            except Exception as e:
                st.error("Error executing query:")
                st.error(e)
        else:
            st.warning("You don't have permission.")
            

with tab3:
    
    

    search_query = st.text_input("Enter the cancellation reason:", placeholder="Example: Car broken")
    search_btn = st.button("Search", type="primary")

    if search_btn and search_query:
        
            try:
                import os
                
                current_dir = os.getcwd() 
                chroma_path = os.path.join(current_dir, "dashboard", "chroma_db")
                

                if not os.path.exists(chroma_path):
                     chroma_path = os.path.join(current_dir, "chroma_db")

                client = chromadb.PersistentClient(path=chroma_path)
                collection = client.get_collection(name="cancellation_reasons")


                results = collection.query(
                    query_texts=[search_query],
                    n_results=5
                )


                if not results['ids'] or not results['ids'][0]:
                     st.warning("No similar records found.")
                else:
                    top_ids = results['ids'][0]        
                    top_documents = results['documents'][0] 
                    
                    ids_tuple = tuple(top_ids)
                    

                    if len(ids_tuple) == 1:
                
                        sql_query = f"SELECT * FROM gold.dataset WHERE booking_id = '{ids_tuple[0]}'"
                    else:
                        sql_query = f"SELECT * FROM gold.dataset WHERE booking_id IN {ids_tuple}"

                    db_str = 'postgresql://uber_user:pass@localhost:5432/uber_db'
                    pg_engine = create_engine(db_str)
                    full_details_df = pd.read_sql(sql_query, pg_engine)

                    
                    
                    st.dataframe(
                        full_details_df, 
                        use_container_width=True,  
                        hide_index=True            
                    )
            except Exception as e:
                st.error(f"Error: {e}")
                