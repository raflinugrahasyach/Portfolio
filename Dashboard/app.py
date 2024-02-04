
import matplotlib
matplotlib.use('Agg')  # Atur backend menjadi 'Agg'

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from matplotlib.colors import ListedColormap
from babel.numbers import format_currency
from matplotlib.figure import Figure


sns.set(style='dark')

# Helper function yang dibutuhkan untuk menyiapkan berbagai dataframe

# Title and Subheader
def main():
    # Title and Subheader
    st.markdown("""
        <style>
            .title {
                font-size: 46pt;
                margin-bottom: 0px;
            }
            .subheader {
                font-size: 28pt;
                margin-bottom: 40px;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<p class='title'>Explanatory Data Analysis</p>", unsafe_allow_html=True)
    st.subheader("Bike Sharing Dataset")

    # Load cleaned data and used data
    df_day_clean = pd.read_csv("Dashboard/df_day_clean.csv")
    df_hour_clean = pd.read_csv("Dashboard/df_hour_clean.csv")
    df_day = pd.read_csv("Dashboard/df_day.csv")
    df_hour = pd.read_csv("Dashboard/df_hour.csv")
    

    # Convert 'dteday' column to datetime
    df_day_clean['dteday'] = pd.to_datetime(df_day_clean['dteday'])
    df_hour_clean['dteday'] = pd.to_datetime(df_hour_clean['dteday'])

    # Sort dataframes by 'dteday'
    df_day_clean.sort_values(by="dteday", inplace=True)
    df_hour_clean.sort_values(by="dteday", inplace=True)

    # Reset index
    df_day_clean.reset_index(inplace=True, drop=True)
    df_hour_clean.reset_index(inplace=True, drop=True)

    df_day_cuaca = df_day_clean[['temp', 'atemp', 'hum', 'windspeed', 'cnt']].copy()


    datetime_columns = ["dteday"]
    df_day_clean.sort_values(by="mnth", inplace=True)
    df_day_clean.reset_index(inplace=True)

    df_hour_clean.sort_values(by="mnth", inplace=True)
    df_hour_clean.reset_index(inplace=True)


    def create_df_hour_book(df):
        df_hour_book = df_hour_clean.copy().groupby(['yr', 'hr']).apply(lambda x: pd.Series({
            'User Terdaftar': x['registered'].sum(),
            'User Tidak Terdaftar': x['casual'].sum(),
            'Total': x['cnt'].sum()})).sort_values(by='Total', ascending=False)
        df_hour_book.reset_index(inplace=True)
        df_hour_book.rename(columns={'yr': 'Tahun', 'hr': 'Jam'}, inplace=True)

        return df_hour_book

    def create_df_hour_book_2011(df):
        df_hour_book_2011 = df_hour_book[df_hour_book['Tahun'].copy() == 2011]
        df_hour_book_2011.sort_values(by='Total', ascending=False)

        return df_hour_book_2011

    def create_df_hour_book_2012(df):
        df_hour_book_2012 = df_hour_book[df_hour_book['Tahun'].copy() == 2012]
        df_hour_book_2012.sort_values(by='Total', ascending=False)

        return df_hour_book_2012

    def create_df_day_book(df):
        df_day_book = df_day_clean.groupby(['weekday'].copy()).apply(lambda x: pd.Series({
    'User Terdaftar': x['registered'].sum(),
    'User Tidak Terdaftar': x['casual'].sum(),
    'Total': x['cnt'].sum()})).sort_values(by='Total', ascending=False)
        df_day_book.reset_index(inplace=True)
        df_day_book.rename(columns={'weekday': 'Hari'}, inplace=True)

        return df_day_book
    
    def create_df_month_book(df):
        df_month_book = df_hour_clean.groupby(['yr', 'mnth'].copy()).apply(lambda x: pd.Series({
            'User Terdaftar': x['registered'].sum(),
            'User Tidak Terdaftar': x['casual'].sum(),
            'Total': x['cnt'].sum()}))
        df_month_book.reset_index(inplace=True)
        df_month_book.rename(columns={'yr': 'Tahun', 'mnth': 'Bulan'}, inplace=True)

        return df_month_book
    
    def create_df_month_book_2011(df):
        df_month_book_2011 = df_month_book[df_month_book['Tahun']==2011]
        df_month_book_2011 = df_month_book_2011.sort_values(by='Bulan', key=lambda x: pd.to_datetime(x, format='%B'))
        df_month_book_2011['Kenaikan/Penurunan User'] = df_month_book_2011['Total'].diff()  
        df_month_book_2011.fillna(0, inplace=True)

        return df_month_book_2011

    def create_df_month_book_2012(df):
        df_month_book_2012 = df_month_book[df_month_book['Tahun']==2012]# Mengurutkan DataFrame df_month_book_2012 berdasarkan bulan
        df_month_book_2012 = df_month_book_2012.sort_values(by='Bulan', key=lambda x: pd.to_datetime(x, format='%B'))
        df_month_book_2012['Kenaikan/Penurunan User'] = df_month_book_2012['Total'].diff()  
        df_month_book_2012.fillna(0, inplace=True)

        return df_month_book_2012
    
    def create_df_novbook_all_year(df):
        df_novbook_all_year = df_hour_clean.copy()[
        (df_hour_clean['dteday'].dt.month.isin([9, 10, 11, 12]))].copy()

        df_novbook_all_year = df_novbook_all_year.copy().groupby(['yr', 'mnth']).apply(lambda x: pd.Series({
            'Musim': x['season'].unique(),
            'Total': x['cnt'].sum()
        })).sort_values(by=['yr', 'mnth'], ascending=[True, False])
        df_novbook_all_year.reset_index(inplace=True)
        df_novbook_all_year.rename(columns={'mnth': 'Bulan', 'yr':'Tahun'}, inplace=True)

        return df_novbook_all_year
    
    def create_df_season(df):
        df_season = df_day_clean.copy().groupby(by='season').apply(lambda x: pd.Series({
            'User Terdaftar': x['registered'].sum(),
            'User Tidak Terdaftar': x['casual'].sum(),
            'Total': x['cnt'].sum()})).sort_values(by='Total', ascending=False)
        df_season.reset_index(inplace=True)
        df_season.rename(columns={'season': 'Musim'}, inplace=True)
        
        return df_season
            
    def create_df_weather(df):
        df_weather = df_day_clean.copy().groupby(by='weathersit').apply(lambda x: pd.Series({
            'Terdaftar': x['registered'].sum(),
            'Tidak Terdaftar': x['casual'].sum(),
            'Total': x['cnt'].sum()
        })).sort_values(by='Total', ascending=False)
        df_weather.reset_index(inplace=True)
        df_weather.rename(columns={'weathersit': 'Cuaca'}, inplace=True)

        return df_weather
    
    def create_df_cuaca_corr(df):
        df_cuaca_corr = df_hour.copy()[['temp', 'atemp', 'hum', 'windspeed', 'cnt']]
        df_cuaca_corr = df_cuaca_corr.rename(columns={'temp': 'Suhu', 
                                              'atemp': 'Suhu Terasa', 
                                              'hum': 'Kelembaban', 
                                              'windspeed': 'Kecepatan Angin', 
                                              'cnt': 'Total Penyewaan Sepeda'})

        # Menghitung matriks korelasi
        return df_cuaca_corr
    

    
    for column in datetime_columns:
        df_day_clean[column] = pd.to_datetime(df_day_clean[column])
        df_hour_clean[column] = pd.to_datetime(df_hour_clean[column])

    # Filter data
    min_date = df_day_clean["dteday"].min()
    max_date = df_day_clean["dteday"].max()

    with st.sidebar:
        # Menambahkan Gambar
        st.image("https://www.green.it/wp-content/uploads/2014/08/Hubway-Reopens-for-Spring-Offering-1100-Communal-Bicycles.jpg")
        
        # Mengambil start_date & end_date dari date_input
        start_date, end_date = st.date_input(
            label='Rentang Waktu',min_value=min_date,
            max_value=max_date,
            value=[min_date, max_date]
        )

    main_df = df_day_clean[(df_day_clean["dteday"] >= str(start_date)) & 
                    (df_day_clean["dteday"] <= str(end_date))]

    # st.dataframe(main_df)

    # # Menyiapkan berbagai dataframe
    df_hour_book = create_df_hour_book(main_df)
    df_hour_book_2011 = create_df_hour_book_2011(main_df)
    df_hour_book_2012 = create_df_hour_book_2012(main_df)
    df_day_book = create_df_day_book(main_df)
    df_month_book = create_df_month_book(main_df)
    df_month_book_2011 = create_df_month_book_2011(main_df)
    df_month_book_2012 = create_df_month_book_2012(main_df)
    df_novbook_all_year = create_df_novbook_all_year(main_df)
    df_season = create_df_season(main_df)
    df_weather = create_df_weather(main_df)
    df_season = create_df_season(main_df)
    df_cuaca_corr = create_df_cuaca_corr(main_df)


    # Penyewaan Menurut Jam
    
    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 6))

    color_1 = ['#72BCD4' if i in [8, 17, 18] else '#D3D3D3' for i in range(len(df_hour_book_2011))]
    color_2 = ['#72BCD4' if i in [8, 17, 18] else '#D3D3D3' for i in range(len(df_hour_book_2011))]

    # Plot untuk Tahun 2011
    sns.barplot(x="Jam",
                y="Total",
                data=df_hour_book_2011,
                palette=color_1,
                ax=ax[0])
    ax[0].set_ylabel('Jumlah Sewa')
    ax[0].set_xlabel('Jam')
    ax[0].set_title("Jumlah Penyewaan Tertinggi Menurut Jam pada Tahun 2011", loc="center", fontsize=20)
    ax[0].tick_params(axis ='y', labelsize=16)
    ax[0].set_ylim(0, df_hour_book_2012['Total'].max() + 10000)

    # Plot untuk Tahun 2012
    sns.barplot(x="Jam",
                y="Total",
                data=df_hour_book_2012,
                palette=color_2,
                ax=ax[1],
                )
    ax[1].set_ylabel('Jumlah Sewa')
    ax[1].set_xlabel('Jam')
    ax[1].set_title("Jumlah Penyewaan Tertinggi Menurut Jam pada Tahun 2012", loc="center", fontsize=20)
    ax[1].tick_params(axis ='y', labelsize=16)
    ax[1].set_ylim(0, df_hour_book_2012['Total'].max() + 10000)

    ax[0].patch.set_facecolor('white')
    ax[1].patch.set_facecolor('white')

    st.set_option('deprecation.showPyplotGlobalUse', False)
    # Menampilkan plot Matplotlib di Streamlit
    st.pyplot()
    
    # customer demographic
    st.subheader("Penyewaan Berdasarkan Hari")

    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    # Konversi kolom 'Hari' menjadi tipe data kategori dengan urutan hari yang benar
    df_day_book['Hari'] = pd.Categorical(df_day_book['Hari'], categories=day_order, ordered=True)

    df_day_book = df_day_book.sort_values(by='Hari')

    # Membuat objek Figure
    fig, ax = plt.subplots(figsize=(12, 6))


    color_day = ['#D3D3D3' if total != df_day_book['Total'].max() else '#72BCD4' for total in df_day_book['Total']]

    # Plot bar
    sns.barplot(
        y="Total",
        x="Hari",
        data=df_day_book.sort_values(by="Total", ascending=False),
        palette=color_day,
        ax=ax
    )

    ax.set_facecolor('white')


    plt.title("Jumlah Penyewaan Menurut Hari pada Tahun 2011-2012", loc="center", fontsize=15)
    plt.ylabel(None)
    plt.xlabel(None)
    plt.tick_params(axis='x', labelsize=12)

    st.pyplot(fig)


    st.subheader("Jumlah Penyewaan Tertinggi Menurut Bulan pada Tahun 2011-2012")

    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 6))

    # Plot untuk Tahun 2011
    sns.lineplot(x="Bulan",
                y="Total",
                data=df_month_book_2011,
                marker='o',
                color='#72BCD4',
                ax=ax[0])
    ax[0].set_ylabel('Jumlah Sewa', fontsize=12, fontweight='bold')
    ax[0].set_xlabel('Bulan', fontsize=12, fontweight='bold')
    ax[0].set_title("Jumlah Penyewaan Tertinggi Menurut Bulan pada Tahun 2011", loc="center", fontsize=15)
    ax[0].tick_params(axis='y', labelsize=12)
    ax[0].set_xticklabels(ax[0].get_xticklabels(), rotation=30)
    ax[0].set_ylim(0, df_month_book_2012['Total'].max() + 20000)

    # Menonjolkan poin tertinggi dengan warna hijau
    max_value_index_2011 = df_month_book_2011['Total'].idxmax()
    ax[0].scatter(df_month_book_2011.loc[max_value_index_2011, 'Bulan'],
                df_month_book_2011.loc[max_value_index_2011, 'Total'],
                color='green', s=180, label='Penyewaan Tertinggi 2011')

    # Menonjolkan garis yang menurun drastis dengan warna merah
    ax[0].axvline(df_month_book_2011.iloc[10]['Bulan'], color='red', linestyle='--', alpha=0.5, label='Penurunan Drastis')

    ax[0].legend(loc='upper left', fontsize='10')
    ax[0].set_facecolor('white')

    # Plot untuk Tahun 2012
    sns.lineplot(x="Bulan",
                y="Total",
                data=df_month_book_2012,
                marker='o',
                color='#72BCD4',
                ax=ax[1])
    ax[1].set_ylabel('Jumlah Sewa', fontsize=12, fontweight='bold')
    ax[1].set_xlabel('Bulan', fontsize=12, fontweight='bold')
    ax[1].set_title("Jumlah Penyewaan Tertinggi Menurut Bulan pada Tahun 2012", loc="center", fontsize=15)
    ax[1].tick_params(axis='y', labelsize=12)
    ax[1].set_xticklabels(ax[1].get_xticklabels(), rotation=30)
    ax[1].set_ylim(0, df_month_book_2012['Total'].max() + 20000)

    # Menonjolkan poin tertinggi dengan warna hijau
    max_value_index_2012 = df_month_book_2012['Total'].idxmax()
    ax[1].scatter(df_month_book_2012.loc[max_value_index_2012, 'Bulan'],
                df_month_book_2012.loc[max_value_index_2012, 'Total'],
                color='green', s=180, label='Penyewaan Tertinggi 2012')

    # Menonjolkan garis yang menurun drastis dengan warna merah
    ax[1].axvline(df_month_book_2011.iloc[10]['Bulan'], color='red', linestyle='--', alpha=0.5, label='Penurunan Drastis')

    ax[1].legend(loc='upper left', fontsize='10')

    ax[1].set_facecolor('white')

    # Menampilkan plot Matplotlib di Streamlit
    st.set_option('deprecation.showPyplotGlobalUse', False)
    st.pyplot(fig)


    # Penyewaan Berdasarkan Musim
    st.subheader("Penyewaan Berdasarkan Musim")

    fig, ax = plt.subplots(figsize=(12, 6))

    color_season = ['#D3D3D3' if total != df_season['Total'].max() else '#72BCD4' for total in df_season['Total']]

    sns.barplot(
        y="Total",
        x="Musim",
        data=df_season.sort_values(by="Total", ascending=False),
        palette=color_season,
        ax=ax
    )    
    ax.set_facecolor('white')

    plt.title("Jumlah Penyewaan Menurut Musim pada Tahun 2011-2012", loc="center", fontsize=15)
    plt.ylabel(None)
    plt.xlabel(None)
    plt.tick_params(axis='x', labelsize=12)


    # Menampilkan plot Matplotlib di Streamlit
    st.pyplot()


    # Visualisasi Musim pada tahun 2011 dan 2012
    st.subheader("Penyewaan Berdasarkan Cuaca")

    fig, ax = plt.subplots(figsize=(12, 6))

    color_weather = ['#D3D3D3' if total != df_weather['Total'].max() else '#72BCD4' for total in df_weather['Total']]

    sns.barplot(
        y="Total",
        x="Cuaca",
        data=df_weather.sort_values(by="Total", ascending=False),
        palette=color_weather,
        hue='Cuaca',
        ax=ax
    )

    ax.set_facecolor('white')

    # Membuat palet
    legend_palette = ListedColormap(color_weather)

    # Membuat legend dengan palet
    legend_labels = {'1': '1: Clear, Few clouds, Partly cloudy',
                    '2': '2: Mist + Cloudy, Mist + Broken clouds, Mist + Few clouds, Mist',
                    '3': '3: Light Snow, Light Rain + Thunderstorm + Scattered clouds, Light Rain + Scattered clouds'}
    legend_elements = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=legend_palette.colors[i], markersize=10, label=label) for i, label in enumerate(legend_labels.values())]
    plt.legend(handles=legend_elements, title="Cuaca", loc="upper right", fontsize=6)

    plt.title("Jumlah Penyewaan Menurut Cuaca pada Tahun 2011-2012", loc="center", fontsize=12)
    plt.ylabel('Jumlah Sewa')
    plt.xlabel('Cuaca')
    plt.tick_params(axis='x', labelsize=12)

    st.set_option('deprecation.showPyplotGlobalUse', False)
    # Menampilkan plot Matplotlib di Streamlit
    st.pyplot()


    st.subheader("Hubungan Variabel Suhu, Kelembaban, Kecepatan Angin, dan Penyewaan Sepeda")

    # Calculate the aspect ratio
    aspect_ratio = 16 / 9

    # Create a figure with appropriate size based on the aspect ratio
    fig, axs = plt.subplots(2, 2, figsize=(14, 14 / aspect_ratio))

    plt.subplots_adjust(wspace=10, hspace=10) # Mengatur jarak antar subplot

    # Set the facecolor of all subplots to white for a clean background
    for ax in axs.flatten():
        ax.set_facecolor('white')

    # Plot Scatter plot for each variable pair
    sns.scatterplot(data=df_day_cuaca, x='temp', y='cnt', ax=axs[0, 0])
    axs[0, 0].set_title('Suhu vs Penyewaan Sepeda', fontsize=12, fontweight='bold')
    axs[0, 0].set_xlabel('Suhu', fontsize=10, labelpad=10)
    axs[0, 0].set_ylabel('Jumlah Penyewaan Sepeda', fontsize=10, labelpad=10)

    sns.scatterplot(data=df_day_cuaca, x='atemp', y='cnt', ax=axs[0, 1])
    axs[0, 1].set_title('Suhu Terasa vs Penyewaan Sepeda', fontsize=12, fontweight='bold')
    axs[0, 1].set_xlabel('Suhu Terasa', fontsize=10, labelpad=10)
    axs[0, 1].set_ylabel('Jumlah Penyewaan Sepeda', fontsize=10, labelpad=10)

    sns.scatterplot(data=df_day_cuaca, x='hum', y='cnt', ax=axs[1, 0])
    axs[1, 0].set_title('Kelembaban vs Penyewaan Sepeda', fontsize=12, fontweight='bold')
    axs[1, 0].set_xlabel('Kelembaban', fontsize=10, labelpad=10)
    axs[1, 0].set_ylabel('Jumlah Penyewaan Sepeda', fontsize=10, labelpad=10)

    sns.scatterplot(data=df_day_cuaca, x='windspeed', y='cnt', ax=axs[1, 1])
    axs[1, 1].set_title('Kecepatan Angin vs Penyewaan Sepeda', fontsize=12, fontweight='bold')
    axs[1, 1].set_xlabel('Kecepatan Angin', fontsize=10, labelpad=10)
    axs[1, 1].set_ylabel('Jumlah Penyewaan Sepeda', fontsize=10, labelpad=10)

    # Adjust the layout to improve readability
    fig.tight_layout()

    # Display the plot in Streamlit
    st.pyplot()
     # Menampilkan plot Matplotlib di Streamlit

    st.caption('Copyright © Rafli Nugrahasyach 2024')
    # Call the main function to display the Streamlit app
if __name__ == '__main__':
    main()
