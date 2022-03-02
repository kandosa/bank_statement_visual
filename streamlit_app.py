import sys

import pandas as pd
import streamlit as st
import tabula  # PDF table extra package
import plotly.express as px

# setup streamlit page title, side bar and file uploader
st.title("Bank Statement Visualization")
st.subheader("Please upload bank statement pdf file through the sidebar")
st.write("")
st.sidebar.subheader("Visualization Settings")
upload_file = st.sidebar.file_uploader(label="Drop Bank Statement PDF file", type=['pdf'])

@st.cache

global df_final

if upload_file is not None:
    print(upload_file)
    try:
        df_list = tabula.read_pdf(upload_file, stream=True, pages=[3,4], guess=False)
        df = pd.DataFrame(df_list[0])
        df.rename(columns={'Unnamed: 0': 'PURCHASES', 'ONLINE PHONE': 'MERCHANT CATEGORY', 'Unnamed: 1': 'AMOUNT'}
                  , inplace=True)
        df = df[['PURCHASES', 'MERCHANT CATEGORY', 'AMOUNT']]
        df = df.dropna()
        df = df.iloc[1:, :]
        df = df.reset_index(drop=True)
        df['DATE'] = df['PURCHASES'].str[:5]
        df['PURCHASES'] = df['PURCHASES'].str[5:]

        df_1 = pd.DataFrame(df_list[1])
        df_1.rename(columns={'DISCOVER IT® CARD ENDING IN 1994': 'PURCHASES', 'Unnamed: 0': 'MERCHANT CATEGORY',
                             'Unnamed: 1': 'AMOUNT'}, inplace=True)
        df_1 = df_1[['PURCHASES', 'MERCHANT CATEGORY', 'AMOUNT']]
        df_1 = df_1.dropna()
        df_1 = df_1.loc[(df_1['PURCHASES'].str.contains('/'))]
        df_1 = df_1.reset_index(drop=True)
        df_1['DATE'] = df_1['PURCHASES'].str[:5]
        df_1['PURCHASES'] = df_1['PURCHASES'].str[5:]

        df_final = pd.concat([df, df_1])
        df_final = df_final.reset_index(drop= True)
        df_final = df_final[['DATE', 'PURCHASES', 'MERCHANT CATEGORY', 'AMOUNT']]
        df_final.AMOUNT = df_final.AMOUNT.apply(lambda x: float(x[1:]))
    except Exception as e:
        print('The Error is', e)

try:
    st.write(df_final)
    st.text("")
    st.text("")
except Exception as e:
    print('The Error is', e)

chart_select = st.sidebar.selectbox(
    label="Select Pie Plot or statistic Table",
    options=['Pie Plot', 'Statistic Table', "Download as CSV"]
)    
    
if chart_select == 'Pie Plot':
    try:
        plot = px.pie(df_final, values="AMOUNT", names="MERCHANT CATEGORY", width=800, height= 800)
        plot.update_traces(textposition="inside", textinfo= 'percent+label')
        st.plotly_chart(plot)
        st.subheader("Table of total cost in each category")
        stat_t = df_final.groupby(by='MERCHANT CATEGORY')['AMOUNT'].sum()
        st.dataframe(stat_t)
    except Exception as e:
        print('The Error is', e)
elif chart_select == 'Statistic Table':
    try:
        st.subheader("Table of total cost in each category")
        stat_t = df_final.groupby(by='MERCHANT CATEGORY')['AMOUNT'].sum()
        st.dataframe(stat_t)
        st.write("")
        total_cost = df_final['AMOUNT'].sum()
        st.subheader("Total Cost of this Month is:  ${}".format(total_cost))
    except Exception as e:
        print('The Error is', e)
elif chart_select == 'Download as CSV':
    try:
        @st.cache
        def convert_df(df):
            return df.to_csv(index= False).encode('utf-8')
        csv = convert_df(df_final)
        st.download_button(
            "Press to Download",
            csv,
            "file.csv",
            "text/csv",
            key='download-csv'
        )
    except Exception as e:
        print('The Error is', e)
