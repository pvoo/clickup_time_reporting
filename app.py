import pandas as pd
import streamlit as st
import altair as alt

# File upload
st.header("Upload CSV file")
uploaded_file = st.file_uploader("Choose a file", type="csv")

# Load the CSV file into a Pandas DataFrame
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # Convert the "Start" and "Stop" columns to datetime objects
    df['Start'] = pd.to_datetime(df['Start'], unit='ms')
    df['Stop'] = pd.to_datetime(df['Stop'], unit='ms')

    # Compute the duration of each time entry
    df['Duration'] = df['Stop'] - df['Start']

    # Sort the DataFrame by start time
    df.sort_values(by='Start', inplace=True)

    # Add a column for the date of each time entry
    df['Date'] = df['Start'].dt.date

    # Sidebar controls
    st.sidebar.header("Filter by List")
    lists = df['List Name'].unique()
    selected_list = st.sidebar.selectbox("Select a list", lists)

    # Filter the DataFrame by selected list
    df_filtered = df[df['List Name'] == selected_list]

    # Check for overlapping time entries
    overlapping = []
    for i in range(len(df_filtered)):
        for j in range(i+1, len(df_filtered)):
            if df_filtered.iloc[i]['Stop'] > df_filtered.iloc[j]['Start']:
                overlapping.append((i, j))

    # Print the overlapping time entries
    if overlapping:
        st.write("Overlapping time entries:")
        for i, j in overlapping:
            st.write(df_filtered.iloc[i]['Start'], df_filtered.iloc[i]['Stop'], df_filtered.iloc[i]['Task Name'])
            st.write(df_filtered.iloc[j]['Start'], df_filtered.iloc[j]['Stop'], df_filtered.iloc[j]['Task Name'])
            st.write('')

    # Compute the total time per day
    time_per_day = df_filtered.groupby('Date')['Duration'].sum().reset_index()

    # Visualize the time entries
    fig = alt.Chart(df_filtered).mark_bar().encode(
        x=alt.X('Start:T', title=None),
        x2=alt.X2('Stop:T', title=None),
        y=alt.Y('Task Name:N', title=None),
        color=alt.Color('Duration:Q', title=None, scale=alt.Scale(scheme='blues'))
    ).properties(
        height=500
    ).interactive()

    # Visualize the total time per day
    chart = alt.Chart(time_per_day).mark_bar().encode(
        x=alt.X('Date:T', title='Date'),
        y=alt.Y('Duration:Q', title='Total Time (hours)'),
        tooltip=['Date:T', 'Duration:Q']
    ).properties(
        height=300
    )

    # Display the visualizations
    st.altair_chart(fig, use_container_width=True)
    st.altair_chart(chart, use_container_width=True)
else:
    st.write("Please upload a CSV file.")
