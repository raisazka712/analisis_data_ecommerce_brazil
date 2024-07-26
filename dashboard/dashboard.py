import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

# Load data
df_filtered = pd.read_csv('dashboard/df_filtered.csv')
product_sales_info = pd.read_csv('dashboard/product_sales_info.csv')
df_customers_orders = pd.read_csv('dashboard/df_customers_orders.csv')
df_filtered2 = pd.read_csv("dashboard/df_filtered2.csv")
df_order_reviews = pd.read_csv("dashboard/df_order_reviews.csv")
orders_with_payments = pd.read_csv("dashboard/orders_with_payments.csv")

# Konversi kolom 'order_purchase_timestamp' ke datetime jika belum
datetime_columns = ["order_purchase_timestamp"]
df_filtered.sort_values(by="order_purchase_timestamp", inplace=True)
df_filtered.reset_index(inplace=True)

for column in datetime_columns:
    df_filtered[column] = pd.to_datetime(df_filtered[column])
    df_filtered2[column] = pd.to_datetime(df_filtered2[column])

# ---- streamlit -----
# Mengambil tanggal minimum dan maksimum
min_date = df_filtered['order_purchase_timestamp'].min().date()  # Convert to datetime.date
max_date = df_filtered['order_purchase_timestamp'].max().date()  # Convert to datetime.date

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("../assets/olist_store.png", use_column_width=True)
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu', min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

    # Filter for Best & Worst Performing Product
    st.subheader("Filter Best & Worst Product")
    top_n_products = st.slider("Number of Products", min_value=1, max_value=20, value=5)

    # Filter for Customer Distribution
    st.subheader("Filter Customer Demographics")
    top_n_cities = st.slider("Number of Cities", min_value=1, max_value=20, value=10)
    top_n_states = st.slider("Number of States", min_value=1, max_value=20, value=10)

    # Filter for time range in specific visualizations
    # st.subheader("Filter Time Range for RFM")
    # min_rfm_date = st.date_input(
    #     label='Start Date for RFM Analysis', min_value=min_date,
    #     max_value=max_date, value=min_date
    # )
    # max_rfm_date = st.date_input(
    #     label='End Date for RFM Analysis', min_value=min_date,
    #     max_value=max_date, value=max_date
    # )

main_df = df_filtered[(df_filtered["order_purchase_timestamp"] >= pd.to_datetime(start_date)) & 
                (df_filtered["order_purchase_timestamp"] <= pd.to_datetime(end_date))]

st.write(
    """
    # Olist Store Dashboard :sparkles:
    """
)

# ------- Tren Penjualanan Bulanan -----------
st.subheader('Tren Penjualan Bulanan')

col1, col2 = st.columns(2)

with col1:
    total_orders = main_df.order_item_id.sum()
    st.metric("Total orders", value=total_orders)

with col2:
    total_revenue = format_currency(main_df.payment_value.sum(), "BR", locale='es_CO') 
    st.metric("Total Revenue", value=total_revenue)

# Menghitung total penjualan
main_df['year_month'] = main_df['order_purchase_timestamp'].dt.to_period('M')
monthly_sales = main_df.groupby('year_month')['payment_value'].sum().reset_index()
monthly_sales['year_month'] = monthly_sales['year_month'].astype(str)

# --------- visualisasi Tren Penjualanan Bulanan  -------------
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(monthly_sales['year_month'], 
        monthly_sales['payment_value'], 
        marker='o', 
        linestyle='-', 
        color='b')
ax.set_xticks(monthly_sales['year_month'])
ax.set_xticklabels(monthly_sales['year_month'], rotation=45)
ax.set_xlabel(None)
ax.set_ylabel(None)
ax.tick_params(axis='x', labelsize=20)
ax.tick_params(axis='y', labelsize=20)
ax.set_title('Tren Penjualan Olist Store (2016-2018)', fontsize=30)
ax.grid(True)
plt.tight_layout()
# Menampilkan plot di Streamlit
st.pyplot(fig)

# ----- Best & Worst Product --------
st.subheader("Best & Worst Performing Product")

# Mengurutkan data berdasarkan nilai pembayaran
best_products = product_sales_info.sort_values(by="payment_value", ascending=False)
worst_products = product_sales_info.sort_values(by="payment_value", ascending=True)

# Buat dua plot terpisah untuk produk terlaris dan produk kurang laris
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))

# Tentukan warna untuk jumlah baris yang sesuai
best_colors = ["#72BCD4"] + ["#D3D3D3"] * (len(best_products.head(top_n_products)) - 1)
worst_colors = ["#72BCD4"] + ["#D3D3D3"] * (len(worst_products.head(top_n_products)) - 1)

# Plot produk terlaris
sns.barplot(x="payment_value", y="product_category_name", hue="product_category_name",
            data=best_products.head(top_n_products), palette=best_colors, ax=ax[0])
ax[0].set_xlabel("Number of Sales", fontsize=35)
ax[0].set_ylabel(None)
ax[0].set_title("Best Performing Product", loc="center", fontsize=45)
ax[0].tick_params(axis='x', labelsize=40)
ax[0].tick_params(axis='y', labelsize=40)

# Plot produk kurang laris
sns.barplot(x="payment_value", y="product_category_name", hue="product_category_name",
            data=worst_products.head(top_n_products), palette=worst_colors, ax=ax[1])
ax[1].set_xlabel("Number of Sales", fontsize=35)
ax[1].set_ylabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Performing Product", loc="center", fontsize=45)
ax[1].tick_params(axis='x', labelsize=40)
ax[1].tick_params(axis='y', labelsize=40)
plt.suptitle("Best and Worst Performing Product by Number of Sales", fontsize=60)
# Tampilkan plot di Streamlit
st.pyplot(fig)

# ----- Demografi Pengguna --------
st.subheader("Customer Demographics")


df_customers_orders['customer_city'] = df_customers_orders['customer_city'].astype('str')
df_customers_orders['customer_state'] = df_customers_orders['customer_state'].astype('str')

# Distribusi berdasarkan kota
city_distribution = df_customers_orders['customer_city'].value_counts().reset_index()
city_distribution.columns = ['city', 'count']

# Distribusi berdasarkan negara bagian
state_distribution = df_customers_orders['customer_state'].value_counts().reset_index()
state_distribution.columns = ['state', 'count']


# Streamlit layout
# Fungsi untuk membuat barplot
def create_barplot(data, x_col, y_col, title):
    plt.figure(figsize=(12, 6))
    sns.barplot(x=x_col, y=y_col, data=data)
    plt.title(title, fontsize=16)
    plt.xlabel(None)
    plt.ylabel(None)
    plt.xticks(rotation=45)
    st.pyplot(plt)

# Menampilkan grafik distribusi berdasarkan kota
st.subheader('Customer Distribution by City')
create_barplot(city_distribution.head(top_n_cities), 'city', 'count', 'Customer Distribution by City')

# Menampilkan grafik distribusi berdasarkan negara bagian
st.subheader('Customer Distribution by State')
create_barplot(state_distribution.head(top_n_states), 'state', 'count', 'Customer Distribution by State')

# ----- Total Sales per City --------
st.subheader("Total Sales in Brazil")
st.subheader("Total Sales per City")

# Hitung total penjualan per kota
# city_sales = df_filtered2.groupby('customer_city')['payment_value'].sum().reset_index()

city_sales = df_filtered2[(df_filtered2['order_purchase_timestamp'] >= pd.to_datetime          (start_date)) & 
                           (df_filtered2['order_purchase_timestamp'] <= pd.to_datetime(end_date))].groupby('customer_city')['payment_value'].sum().reset_index()
city_sales = city_sales.rename(columns={'payment_value': 'total_sales'})
top_cities = city_sales.sort_values(by='total_sales', ascending=False).head(top_n_cities)

# Membuat barplot untuk penjualan per kota
fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(x='total_sales', y='customer_city', data=top_cities, ax=ax)
ax.set_title('Total Sales per City', fontsize=16)
ax.set_xlabel(None)
ax.set_ylabel(None)
st.pyplot(fig)

# ----- Total Sales per State --------
st.subheader("Total Sales per State")

# Hitung total penjualan per negara bagian
# state_sales = df_filtered2.groupby('customer_state')['payment_value'].sum().reset_index()

state_sales = df_filtered2[(df_filtered2['order_purchase_timestamp'] >= pd.to_datetime          (start_date)) & 
                           (df_filtered2['order_purchase_timestamp'] <= pd.to_datetime(end_date))].groupby('customer_state')['payment_value'].sum().reset_index()
state_sales = state_sales.rename(columns={'payment_value': 'total_sales'})
top_states = state_sales.sort_values(by='total_sales', ascending=False).head(top_n_states)

# Membuat barplot untuk penjualan per negara bagian
fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(x='total_sales', y='customer_state', data=top_states, ax=ax)
ax.set_title('Total Sales per State', fontsize=16)
ax.set_xlabel(None)
ax.set_ylabel(None)
st.pyplot(fig)

# ----- Sentimen Pelanggan --------
st.subheader("Customer Sentiment towards Olist Store")

# Membuat histogram untuk distribusi skor ulasan
fig, ax = plt.subplots(figsize=(10, 6))
sns.histplot(df_order_reviews['review_score'], bins=5, kde=False, color='skyblue', ax=ax)
ax.set_title('Distribution of Review Scores', fontsize=16)
ax.set_xlabel(None)
ax.set_ylabel(None)
ax.set_xticks(range(1, 6))
st.pyplot(fig)

# ----- Hitung Metrik RFM --------
# Pastikan kolom 'order_purchase_timestamp' bertipe datetime
orders_with_payments['order_purchase_timestamp'] = pd.to_datetime(orders_with_payments['order_purchase_timestamp'])

# Mengelompokkan berdasarkan 'customer_id' dan mencari tanggal pembelian terakhir
last_purchase_per_customer = orders_with_payments.groupby('customer_id')['order_purchase_timestamp'].max().reset_index()

# Mencari tanggal pembelian terakhir dari seluruh pelanggan
latest_purchase_date = last_purchase_per_customer['order_purchase_timestamp'].max()

# asumsikan today adalah hari terakhir pembelian dari seluruh pelanggan
today = pd.to_datetime(latest_purchase_date)

# Menghitung Recency, Frequency, dan Monetary
rfm = orders_with_payments[(orders_with_payments['order_purchase_timestamp'] >= pd.to_datetime          (start_date)) & 
                           (orders_with_payments['order_purchase_timestamp'] <= pd.to_datetime(end_date))].groupby('customer_id').agg({
    'order_purchase_timestamp': lambda x: (today - x.max()).days,  # Recency
    'order_id': 'count',  # Frequency
    'payment_value': 'sum'  # Monetary
}).reset_index()

rfm.columns = ['customer_id', 'recency', 'frequency', 'monetary']

# ----- Visualisasi RFM --------
st.subheader("Best Customer Based on RFM Parameters")

col1, col2, col3 = st.columns(3)

with col1:
    avg_recency = round(rfm.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)

with col2:
    avg_frequency = round(rfm.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)

with col3:
    avg_monetary = format_currency(rfm.monetary.mean(), "BR", locale='es_CO') 
    st.metric("Average Monetary", value=avg_monetary)

# Membuat visualisasi RFM
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(50, 20))

# Plot Recency
sns.barplot(y="recency", x="customer_id", data=rfm.sort_values(by="recency", ascending=True).head(5), ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Customer ID", fontsize=35)
ax[0].set_title("By Recency (days)", loc="center", fontsize=60)
ax[0].tick_params(axis='y', labelsize=40)
ax[0].tick_params(axis='x', labelsize=35)

# Plot Frequency
sns.barplot(y="frequency", x="customer_id", data=rfm.sort_values(by="frequency", ascending=False).head(5), ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Customer ID", fontsize=35)
ax[1].set_title("By Frequency", loc="center", fontsize=60)
ax[1].tick_params(axis='y', labelsize=40)
ax[1].tick_params(axis='x', labelsize=35)

# Plot Monetary
sns.barplot(y="monetary", x="customer_id", data=rfm.sort_values(by="monetary", ascending=False).head(5), ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel("Customer ID", fontsize=35)
ax[2].set_title("By Monetary", loc="center", fontsize=60)
ax[2].tick_params(axis='y', labelsize=40)
ax[2].tick_params(axis='x', labelsize=35)

plt.suptitle("Best Customer Based on RFM Parameters (customer_id)", fontsize=60)

# Tampilkan plot di Streamlit
st.pyplot(fig)

st.caption('Copyright (c) Raisazka 2024')