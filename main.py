import streamlit as st
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter
import seaborn as sns
import numpy as np
import pandas as pd
import get_df 
import emoji
import zipfile

st.title("Whats app chat analyzer")
text = ''
#sidebar
st.sidebar.title("Upload chat in text format")
uploaded_zip = st.sidebar.file_uploader("Upload your ZIP file", type='zip')
if uploaded_zip is not None:
    with zipfile.ZipFile(uploaded_zip, 'r') as zip_ref:
        file_list = zip_ref.namelist()

        txt_files = [f for f in file_list if f.endswith('.txt')]

        if txt_files:
            with zip_ref.open(txt_files[0]) as file:
                text = file.read().decode('utf-8')
        else:
            st.warning("No .txt file found in the ZIP.")

if text :
    df = get_df.preprocess(text)  
    users = list(df['user'].unique())
    years = list(df['year'].unique())
    years = [int(i) for i in years]
    users.insert(0, "All")
    years.insert(0, "All")
    selected_user = st.sidebar.selectbox('select user' , users)
    selected_year = st.sidebar.selectbox('select year' , years)
    if selected_user != "All" :
        df = df[df["user"] == selected_user]
    if selected_year != "All" :
        df = df[df['year'] == selected_year]

    #stats
    col1 , col2 , col3 , col4 , col5 = st.columns([1.1 , 1,1,1 , 1])
    with col1:
        st.header("Total Messages")
        st.header(df["msg"].shape[0])
    with col2:
        st.header("Total Words")
        st.header( df["msg"].apply(lambda x:len( x.split(" "))).sum() )
    with col3:
        st.header("Media Shared")
        st.header(df[df['msg']=='<Media omitted>'].shape[0])
    with col4:
        st.header("Links Shared")
        st.header(df[df['msg'].apply(lambda x: x.startswith("https://"))].shape[0])
    with col5:
        st.header("Messages Deleted")
        st.header(df[df["msg"]== "This message was deleted"].shape[0])


    df = df[df["msg"]!= "This message was deleted"]
    


    #montly timeline
    monthly_time = df.groupby(['year' , 'month']).count()['msg'].reset_index()
    time = []
    for i in range(monthly_time.shape[0]):
        time.append(monthly_time['month'][i] + "-" + str(monthly_time['year'][i]))

    monthly_time['time'] = time

    st.header("Monthly Timeline")
    fig , ax = plt.subplots()
    ax.plot(monthly_time['time'] , monthly_time['msg'])
    plt.xlabel("Month")
    plt.ylabel("Messages")
    plt.xticks(rotation='vertical')
    st.pyplot(fig)

    #weekly timeline
    weekly_time = df.groupby([ "year",'week']).count()['msg'].reset_index()
    weekly = []
    for i in range(weekly_time.shape[0]):
        weekly.append(str(weekly_time['week'][i]) + "-" + str(weekly_time['year'][i]))

    weekly_time['weeks'] = weekly
    st.header("Weekly Timeline")
    fig , ax = plt.subplots()
    ax.plot(weekly_time['weeks'] , weekly_time['msg'])
    if len(weekly_time["weeks"]) > 20:
        step = len(weekly_time["weeks"]) // 20
        plt.xticks(ticks=range(0, len(weekly_time["weeks"]), step), labels=weekly_time["weeks"][::step], rotation="vertical")

    plt.xlabel("Weeks")
    plt.ylabel("Messages")
    st.pyplot(fig)

    #daily timeline
    daily_time = df.groupby(['date']).count()['msg'].reset_index()
    st.header("Daily Timeline")
    fig, ax = plt.subplots(figsize=(7.5, 7.5), dpi=120)  # 7.5 * 120 = 900 pixels
    ax.plot(daily_time['date'] , daily_time['msg'])
    plt.xlabel("Dates")
    plt.ylabel("Messages")
    plt.xticks(rotation='vertical')
    st.pyplot(fig)
  
  #Activity
    st.title("Activity")
    #daily activity
    daily_activity = df['day_name'].value_counts()
    st.header("Most Busy Day")
    fig , ax = plt.subplots()
    ax = plt.bar(daily_activity.index , daily_activity.values)
    plt.xticks(rotation='vertical')
    st.pyplot(fig)

    #weekly activity
    week_activity = df['week'].value_counts()
    st.header("Most Busy Week")
    fig , ax = plt.subplots()
    ax = plt.bar(week_activity.index , week_activity.values)
    plt.xticks(rotation='vertical')
    st.pyplot(fig)

    #Monthly activity
    Month_activity = df['month'].value_counts()
    st.header("Most Busy Month")
    fig , ax = plt.subplots()
    ax = plt.bar(Month_activity.index , Month_activity.values)
    plt.xticks(rotation='vertical')
    st.pyplot(fig)
   
   #weekly heatmap
    st.header("Weekly Heatmap")
    week_heat = df.pivot_table(index='day_name' , values='msg' , columns="period" ,aggfunc="count" , fill_value=0)
    fig , ax = plt.subplots()
    ax = sns.heatmap(week_heat)
    plt.xticks(rotation='vertical')
    st.pyplot(fig)

    #most messages
    st.header("Most Messages By User")
    most_msg = df["user"].value_counts()
    percent = round((most_msg / df.shape[0]) * 100, 2)
    msg_summary = pd.DataFrame({
        "Count": most_msg,
        "Percent": percent
    })

    most_msg_col , df_col = st.columns([2,1])

    with most_msg_col:
        # st.header
        fig , ax = plt.subplots()
        ax = plt.bar(most_msg.index , most_msg.values)
        plt.xticks(rotation='vertical')
        st.pyplot(fig)
    
    with df_col:
        st.write(msg_summary)
    
    #wordcloud
    st.header("Word Cloud")
    df = df[df['msg'] != '<Media omitted>']
    wordcloud = WordCloud(width=500, height=500, background_color='white').generate(df['msg'].str.cat(sep = " "))
    fig, ax = plt.subplots(figsize=(15, 15))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')  # Hide axes
    st.pyplot(fig)
   
    #most Used Words
    st.header("Word Cloud")
    most_words = df['msg'].str.cat(sep = " ").split(" ")
    most_common = pd.DataFrame(Counter(most_words).most_common(20))
    fig, ax = plt.subplots()
    ax.barh(most_common[0] , most_common[1])
    st.pyplot(fig)

    #emoji analysis
    st.header("Emoji Analysis")

    emoji_df_col , emoji_chart_col = st.columns([1,2]) 

    plt.rcParams['font.family'] = 'Segoe UI Emoji'
    emojis = []
    for message in df['msg']:
        emojis.extend([c for c in message if c in emoji.EMOJI_DATA ])

    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis)))).head(10)
    emoji_df.columns = ['Emoji', 'Count']

    with emoji_df_col:
        st.write(emoji_df)
    with emoji_chart_col:
        fig , ax = plt.subplots()
        ax = plt.pie( emoji_df['Count'],labels=emoji_df['Emoji'], autopct="%0.2f%%") 
        st.pyplot(fig)
        plt.show()


   

