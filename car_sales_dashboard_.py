##############################################
#import library
##############################################

import pandas as pd
import streamlit as st
import altair as alt

##############################################
#import dataset/config/clean
##############################################

st.set_page_config(page_title="Car Sales Dashboard", layout="wide")
st.title("📈 Car Sales Dashboard")
st.markdown('##')

@st.cache_data
def load_data():
    db_orders = pd.read_csv("orders_cleaned.csv", index_col=0)
    return db_orders

db_orders = load_data()

#rename the vehicle_key column

db_orders = db_orders.rename(columns={"vehicle_key":"vehicle"})

##############################################
#add sidebar
##############################################

st.sidebar.header("Please Filter Here")
showroom = st.sidebar.multiselect(
   "Select the Showroom:",
   options=db_orders['showroom'].unique(),
   default=db_orders['showroom'].unique()
)



##############################################
#Complete/Pending sidebar
##############################################

order_status = st.sidebar.radio(
       "Select the Order Status:",
       options = db_orders['order_status'].unique()
)

##############################################
#Payment Sidebar
##############################################

order_type = st.sidebar.multiselect(
      "Select the Payment Type",
      options = db_orders['order_type'].unique(),
      default = db_orders['order_type'].unique()
)

##############################################
#main page
##############################################

db_select = db_orders.query(
    "showroom== @showroom & order_status ==@order_status & order_type ==@order_type"
)


#if selection is not available, then stop
if db_select.empty:
   st.warning("No data available based on the current filter settings")
   st.stop() #halt st run

##############################################
#calculate KPI's
##############################################

st.subheader("📊 Sales Summary")
col1, col2, col3 = st.columns(3)

total_sales = db_select['sale_amount'].sum()
total_orders = len(db_select)
completed_orders = db_select[db_select['order_status'] == "Complete"].shape[0]

col1.metric("Total Sales (€)", f"{total_sales:,.2f}")
col2.metric("Total Orders", f"{total_orders:,}")
col3.metric("Completed Orders", f"{completed_orders:,}")

st.divider()

##############################################
#Monthly Sales Trend
##############################################

st.subheader("📈 Monthly Sales Trend")

db_select["order_date"] = pd.to_datetime(db_select["order_date"])

sales_over_time = db_select.groupby(pd.Grouper(key='order_date', freq='M')).sum(numeric_only=True).reset_index()
line_chart = alt.Chart(sales_over_time).mark_line(point=True).encode(
    x=alt.X('order_date:T', title='Month'),
    y=alt.Y('sale_amount:Q', title='Total Sales (€)', axis=alt.Axis(format=",d")),
    tooltip=['order_date:T', alt.Tooltip('sale_amount:Q', format=',')]
).properties(
    width=700,
    height=300
)
st.altair_chart(line_chart, use_container_width=True)


##############################################
#plot bar chart to show price per showroom
##############################################

st.subheader("💶 Sales per Showroom (€)")

# Aggregate
showroom_sales = db_select.groupby("showroom")[["sale_amount"]].sum().reset_index()

# Color scale to highlight bigger sales
color_scale = alt.Scale(scheme='blues')

# Build chart
showroom_chart = alt.Chart(showroom_sales).mark_bar(
    cornerRadiusTopLeft=5,
    cornerRadiusTopRight=5
).encode(
    x=alt.X("sale_amount:Q", title="Sale Amount (€)", axis=alt.Axis(format=",d")),
    y=alt.Y("showroom:N", sort='-x', title="Showroom"),
    color=alt.Color("sale_amount:Q", scale=color_scale, legend=None),
    tooltip=[
        alt.Tooltip("showroom:N", title="Showroom"),
        alt.Tooltip("sale_amount:Q", title="Total Sales (€)", format=",")
    ]
).properties(
    width=400,
    height=300
)

# Add text labels on bars
text = showroom_chart.mark_text(
    align='left',
    baseline='middle',
    dx=3
).encode(
    text=alt.Text('sale_amount:Q', format=",")
)

# Combine bars + labels
final_showroom_chart = showroom_chart + text

st.altair_chart(final_showroom_chart, use_container_width=True)

##############################################
#plot bar chart to show price per vehicle
##############################################

st.subheader("💶 Most Expensive Vehicles (€)")

price_per_vehicle = db_select.groupby("vehicle")[["sale_amount"]].sum().reset_index()

vehicle_chart = alt.Chart(price_per_vehicle).mark_bar(
    cornerRadiusTopLeft=5,
    cornerRadiusTopRight=5
).encode(
    x=alt.X("vehicle:N", sort='-y', title="Vehicle"),
    y=alt.Y("sale_amount:Q", title="Sale Amount (€)", axis=alt.Axis(format=",d")),
    color=alt.Color("sale_amount:Q", scale=alt.Scale(scheme='greens'), legend=None),
    tooltip=[
        alt.Tooltip("vehicle:N", title="Vehicle"),
        alt.Tooltip("sale_amount:Q", title="Total Sales (€)", format=",")
    ]
).properties(
    width=600,
    height=300
)

# Text labels
text_v = vehicle_chart.mark_text(
    align='center',
    baseline='bottom',
    dy=-2
).encode(
    text=alt.Text('sale_amount:Q', format=",")
)

final_vehicle_chart = vehicle_chart + text_v

st.altair_chart(final_vehicle_chart, use_container_width=True)

st.divider()

##############################################
# --- Data Table ---
##############################################

with st.expander("🧾 View Filtered Data Table"):
    st.dataframe(db_select, height=400)


