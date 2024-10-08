import streamlit as st
import pandas as pd
import plotly.express as px
import base64
from io import StringIO, BytesIO
import tkinter as tk
import numpy as np

def generate_html_download_link(fig):
    towrite = StringIO()
    fig.write_html(towrite, include_plotlyjs="cdn")
    towrite = BytesIO(towrite.getvalue().encode())
    b64 = base64.b64encode(towrite.read()).decode()
    href = f'<a href="data:text/html;charset=utf-8;base64, {b64}" download="plot.html">Download</a>'
    return st.markdown(href, unsafe_allow_html=True)

def np_moving_range(array, fill_val = None):
   return np.r_[fill_val, np.abs(np.diff(array))]

st.set_page_config(page_title='IAQ Analysis Plotter')
st.title('IAQ Analysis Plotter')
st.subheader('Upload Data from Dashboard')

uploaded_file=st.file_uploader('Choose an Excel file',type='csv')
if uploaded_file:
    st.markdown('---')
    df=pd.read_csv(uploaded_file, parse_dates=["time"])
    df = df.iloc[1:-1,:]
    df.temp = (9/5)*df.temp+32
    df.rename(columns={'temp': 'Temperature (˚F)', 'co2': 'CO2 (ppm)','humidity': 'Humidity (%)',
                       'massPm1': 'PM1.0 (µg/m3)','massPm25': 'PM2.5 (µg/m3)','massPm4': 'PM4.0 (µg/m3)',
                       'massPm10': 'PM10.0 (µg/m3)', 'tvoc': 'VOC (ppb)','mic': 'Noise (dBA)',
                       'time':'Time'}, inplace=True)
    groupby_column = st.selectbox(
        'What would you like to analyse?',
        ('Temperature (˚F)','VOC (ppb)','PM1.0 (µg/m3)','PM2.5 (µg/m3)',
         'PM4.0 (µg/m3)','PM10.0 (µg/m3)','Humidity (%)','CO2 (ppm)','Noise (dBA)'),
        index=None,placeholder="Select measurement to analyse...",)
    output_columns=['Date & Time']
    groupby_column_time = st.selectbox(
        'When was the air solution operational?',df.Time,index=None,
            placeholder="Select date & time...",)
    
    if groupby_column_time!=None:
        idx_install = df[(df.Time == groupby_column_time)].iloc[0].name
        if idx_install > 2:
            subset_before = df.loc[:idx_install-1]
            subset_after = df.loc[idx_install:]
            subset_before_mean = subset_before.mean(axis=0)
            subset_after_mean = subset_after.mean(axis=0)
            #subset_before=subset_before.iloc[:,1:]
            clean_data = st.selectbox(
                'Would you like to remove the spikes?',('Yes','No'),index=None,
                placeholder="Choose your answer...",)
            if clean_data=='Yes':
                subset_before_movingrange = subset_before.apply(np_moving_range, fill_val = None)
                subset_after_movingrange = subset_after.apply(np_moving_range, fill_val = None)
                subset_before__movingrange_mean = subset_before_movingrange.mean(axis=0)
                subset_after__movingrange_mean = subset_after_movingrange.mean(axis=0)
                subset_before_UCL = subset_before_mean.iloc[1:] + 2.66*subset_before__movingrange_mean
                subset_after_UCL = subset_after_mean.iloc[1:] + 2.66*subset_after__movingrange_mean
                #subset_before_UCL
                #subset_after_UCL
                if groupby_column == 'PM1.0 (µg/m3)':
                    subset_before_clean = subset_before[subset_before['PM1.0 (µg/m3)'] < subset_before_UCL['PM1.0 (µg/m3)']]
                    subset_after_clean = subset_after[subset_after['PM1.0 (µg/m3)'] < subset_after_UCL['PM1.0 (µg/m3)']]
                elif groupby_column == 'PM2.5 (µg/m3)':
                    subset_before_clean = subset_before[subset_before['PM2.5 (µg/m3)'] < subset_before_UCL['PM2.5 (µg/m3)']]
                    subset_after_clean = subset_after[subset_after['PM2.5 (µg/m3)'] < subset_after_UCL['PM2.5 (µg/m3)']]
                elif groupby_column == 'PM4.0 (µg/m3)':
                    subset_before_clean = subset_before[subset_before['PM4.0 (µg/m3)'] < subset_before_UCL['PM4.0 (µg/m3)']]
                    subset_after_clean = subset_after[subset_after['PM4.0 (µg/m3)'] < subset_after_UCL['PM4.0 (µg/m3)']]
                elif groupby_column == 'PM10.0 (µg/m3)':
                    subset_before_clean = subset_before[subset_before['PM10.0 (µg/m3)'] < subset_before_UCL['PM10.0 (µg/m3)']]
                    subset_after_clean = subset_after[subset_after['PM10.0 (µg/m3)'] < subset_after_UCL['PM10.0 (µg/m3)']]
                elif groupby_column == 'Temperature (˚F)':
                    subset_before_clean = subset_before[subset_before['Temperature (˚F)'] < subset_before_UCL['Temperature (˚F)']]
                    subset_after_clean = subset_after[subset_after['Temperature (˚F)'] < subset_after_UCL['Temperature (˚F)']]
                elif groupby_column == 'CO2 (ppm)':
                    subset_before_clean = subset_before[subset_before['CO2 (ppm)'] < subset_before_UCL['CO2 (ppm)']]
                    subset_after_clean = subset_after[subset_after['CO2 (ppm)'] < subset_after_UCL['CO2 (ppm)']]
                elif groupby_column == 'Humidity (%)':
                    subset_before_clean = subset_before[subset_before['Humidity (%)'] < subset_before_UCL['Humidity (%)']]
                    subset_after_clean = subset_after[subset_after['Humidity (%)'] < subset_after_UCL['Humidity (%)']]
                elif groupby_column == 'VOC (ppb)':
                    subset_before_clean = subset_before[subset_before['VOC (ppb)'] < subset_before_UCL['VOC (ppb)']]
                    subset_after_clean = subset_after[subset_after['VOC (ppb)'] < subset_after_UCL['VOC (ppb)']]
                elif groupby_column == 'Noise (dBA)':
                    subset_before_clean = subset_before[subset_before['Noise (dBA)'] < subset_before_UCL['Noise (dBA)']]
                    subset_after_clean = subset_after[subset_after['Noise (dBA)'] < subset_after_UCL['Noise (dBA)']]

                #subset_before_clean
                #subset_after_clean


                subset_clean = pd.concat([subset_before_clean,subset_after_clean])
                #subset_clean

                if groupby_column!=None:
                        fig = px.bar(
                            subset_clean,
                            x='Time',
                            y=groupby_column,
                            color=groupby_column,
                            color_continuous_scale=['green','yellow','red'],
                            template='plotly_white',
                            title=f'<b>Measurement by {groupby_column}</b>'
                            )
                        st.subheader('Download Graphs:')
                        generate_html_download_link(fig)

                        st.plotly_chart(fig)
                        st.dataframe(subset_clean)

            elif clean_data=='No':

                if groupby_column!=None:
                        fig = px.bar(
                            df,
                            x='Time',
                            y=groupby_column,
                            color=groupby_column,
                            color_continuous_scale=['green','yellow','red'],
                            template='plotly_white',
                            title=f'<b>Measurement by {groupby_column}</b>'
                            )
                        st.subheader('Download Graphs:')
                        generate_html_download_link(fig)

                        st.plotly_chart(fig)
                        st.dataframe(df)
    

    
    
