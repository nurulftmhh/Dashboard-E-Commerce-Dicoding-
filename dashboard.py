import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import datetime as dt
from babel.numbers import format_currency
sns.set(style='dark')

def create_daily_order_items_df(df):
    daily_order_items_df = df.resample(rule='D', on='order_purchase_timestamp').agg({
        "order_id" : "nunique"
    })

    daily_order_items_df = daily_order_items_df.reset_index()
    daily_order_items_df.rename(columns={
        "order_id":"order_count"
    }, inplace=True)

    return daily_order_items_df

def create_most_order_df(df):
    most_order_df = df.groupby("product_category_name")["order_id"].count().sort_values(by="order_id", ascending=False)

    most_order_df.rename(
        columns={"order_id": "sum_category_product"}, inplace=True
    )

    return most_order_df  


all_df = pd.read_csv("data/all_data.csv")
orders_df = pd.read_csv("data/orders_df.csv")
combined2_df = pd.read_csv("data/combined2_df.csv")
combined1_df = pd.read_csv("data/combined1_df.csv")
datetime_columns = ["order_purchase_timestamp", "order_estimated_delivery_date"]
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(inplace=True)
 
for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()
 
with st.sidebar:
    # Menambahkan logo perusahaan
    # st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )   

main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) & 
                (all_df["order_purchase_timestamp"] <= str(end_date))]     

daily_order_items_df = create_daily_order_items_df(main_df)
most_order_df = create_daily_order_items_df(main_df)

st.header('E-Commerce Data Analysis')

total_orders = daily_order_items_df.order_count.sum()
st.metric("Total orders", value=total_orders)

def number_orders(data):
    data['order_purchase_timestamp'] = pd.to_datetime(data['order_purchase_timestamp'])
    data.set_index('order_purchase_timestamp', inplace=True)
    monthly_orders_df = data.resample(rule='M').agg({'order_id':'nunique'})
    monthly_orders_df.index = monthly_orders_df.index.strftime('%Y-%m')
    # monthly_orders_df = monthly_orders_df.reset_index()
    monthly_orders_df.rename(columns={"order_id": "order_count"}, inplace=True)
    
    st.text('Menampilkan banyaknya pesanan tiap bulannya')
    st.dataframe(monthly_orders_df)

    st.write("### Monthly Orders Plot")
    st.text('Menampilkan visualisasi dari jumlah customer melakukan pemesanan tiap bulannya')
    fig, ax = plt.subplots(figsize=(15, 7))
    ax.plot(
        monthly_orders_df.index,
        monthly_orders_df["order_count"],
        marker='o',
        linewidth=2,
        color="#72BCD4"
    )

    ax.set_title("Number of Orders (Monthly)", loc="center", fontsize=20, pad=15)
    ax.set_xlabel("Year-Month", fontsize=12)
    ax.set_ylabel("Order Count", fontsize=12)
    plt.xticks(rotation=45)
    st.pyplot(fig)


def most_ordered(data):
    count_category_name = pd.DataFrame(data.groupby("product_category_name")["order_id"].count())
    count_category_name = count_category_name.sort_values(by="order_id", ascending=False)
    count_category_name.rename(columns={"order_id": "sum_category_product"}, inplace=True)

    # Ambil top 5 data
    top_5_data = count_category_name.nlargest(5, "sum_category_product")

    # Plot menggunakan Seaborn
    plt.figure(figsize=(17, 8))
    colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
    sns.barplot(
        x="product_category_name",
        y="sum_category_product",
        data=top_5_data,
        palette=colors
    )
    plt.title("Top 5 Most Ordered Product Categories", loc="center", fontsize=20, pad=20)
    plt.ylabel(None)
    plt.xlabel(None)
    plt.tick_params(axis='x', labelsize=12)
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)

    st.pyplot(plt) 

def top_rated_product_categories(data):
    product_category_names = data['product_category_name'].unique()
    average_review_scores = []
    category_data = []

    for category_name in product_category_names:
        category_reviews = data[data['product_category_name'] == category_name]
        average_review_score = np.mean(category_reviews['review_score'])
        average_review_scores.append(average_review_score)
        category_data.append((category_name, average_review_score))

    category_score_dict = dict(zip(product_category_names, average_review_scores))

    results_df = pd.DataFrame(category_data, columns=['product_category_name', 'Average Review Score'])
    results_df = results_df.sort_values('Average Review Score', ascending=False)
    top_5_data = results_df.nlargest(5, "Average Review Score")

    plt.figure(figsize=(20, 8))
    colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
    sns.barplot(
        x="product_category_name",
        y="Average Review Score",
        data=top_5_data,
        palette=colors
    )
    plt.title("5 Top-Rated Product Categories", loc="center", fontsize=20, pad=20)
    plt.ylabel(None)
    plt.xlabel(None)
    plt.tick_params(axis='x', labelsize=12)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)

    st.pyplot(plt)

def main():
    st.subheader('Monthly Orders')
    number_orders(orders_df)

    st.subheader("Top 5 Most Ordered Product Categories")
    st.text('Menampilkan 5 kategori produk yang paling banyak dipesan oleh customer')
    most_ordered(combined1_df)

    st.subheader("5 Top-Rated Product Categories")
    st.text('Menampilkan 5 kategori produk yang memiliki rata-rata skor revie tertinggi')    
    top_rated_product_categories(combined2_df)


main()