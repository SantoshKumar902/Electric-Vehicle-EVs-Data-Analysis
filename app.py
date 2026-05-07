import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="EV Data Analysis", page_icon="⚡", layout="wide")

st.title("⚡ Electric Vehicle Data Analysis")
st.write("Washington State EV Registration Data — Interactive Dashboard")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("EV_Data_Analysis.csv")
    df = df.drop_duplicates()
    df = df.dropna(subset=['County', 'City', 'Make', 'Model'])
    return df

df = load_data()

# KPI Cards
st.divider()
col1, col2, col3, col4 = st.columns(4)
col1.metric("🚗 Total EVs", f"{len(df):,}")
col2.metric("🏭 Unique Makes", df['Make'].nunique())
col3.metric("📍 Counties", df['County'].nunique())
col4.metric("📅 Year Range", f"{int(df['Model Year'].min())} - {int(df['Model Year'].max())}")
st.divider()

# Sidebar filters
st.sidebar.header("🔍 Filters")
selected_year = st.sidebar.multiselect(
    "Model Year",
    sorted(df['Model Year'].unique(), reverse=True),
    default=[]
)
selected_county = st.sidebar.multiselect(
    "County",
    sorted(df['County'].dropna().unique()),
    default=[]
)
selected_type = st.sidebar.multiselect(
    "EV Type",
    df['Electric Vehicle Type'].unique(),
    default=[]
)

# Apply filters
filtered_df = df.copy()
if selected_year:
    filtered_df = filtered_df[filtered_df['Model Year'].isin(selected_year)]
if selected_county:
    filtered_df = filtered_df[filtered_df['County'].isin(selected_county)]
if selected_type:
    filtered_df = filtered_df[filtered_df['Electric Vehicle Type'].isin(selected_type)]

st.write(f"**Showing {len(filtered_df):,} records**")

# Row 1 - Top Makes & Year Growth
col1, col2 = st.columns(2)

with col1:
    st.subheader("🏆 Top 10 EV Manufacturers")
    top_makes = filtered_df['Make'].value_counts().head(10).reset_index()
    top_makes.columns = ['Make', 'Count']
    fig1 = px.bar(top_makes, x='Count', y='Make', orientation='h',
                  color='Count', color_continuous_scale='Blues',
                  title="Top 10 EV Makes")
    fig1.update_layout(yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("📈 EV Adoption by Year")
    year_count = filtered_df['Model Year'].value_counts().sort_index().reset_index()
    year_count.columns = ['Year', 'Count']
    fig2 = px.line(year_count, x='Year', y='Count',
                   title="Year-on-Year EV Growth",
                   markers=True, color_discrete_sequence=['#00CC96'])
    st.plotly_chart(fig2, use_container_width=True)

# Row 2 - County & EV Type
col3, col4 = st.columns(2)

with col3:
    st.subheader("📍 Top 10 Counties")
    top_counties = filtered_df['County'].value_counts().head(10).reset_index()
    top_counties.columns = ['County', 'Count']
    fig3 = px.bar(top_counties, x='County', y='Count',
                  color='Count', color_continuous_scale='Greens',
                  title="EV Registrations by County")
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.subheader("🔋 BEV vs PHEV Distribution")
    ev_type = filtered_df['Electric Vehicle Type'].value_counts().reset_index()
    ev_type.columns = ['Type', 'Count']
    ev_type['Type'] = ev_type['Type'].str.replace('Battery Electric Vehicle', 'BEV').str.replace('Plug-in Hybrid Electric Vehicle', 'PHEV')
    fig4 = px.pie(ev_type, values='Count', names='Type',
                  title="EV Type Distribution",
                  color_discrete_sequence=['#636EFA', '#EF553B'])
    st.plotly_chart(fig4, use_container_width=True)

# Row 3 - Top Models & Electric Range
col5, col6 = st.columns(2)

with col5:
    st.subheader("🚘 Top 5 EV Models")
    top_models = filtered_df.groupby(['Make', 'Model']).size().reset_index(name='Count')
    top_models = top_models.sort_values('Count', ascending=False).head(5)
    top_models['Make_Model'] = top_models['Make'] + ' ' + top_models['Model']
    fig5 = px.bar(top_models, x='Count', y='Make_Model', orientation='h',
                  color='Count', color_continuous_scale='Oranges',
                  title="Top 5 Most Popular EV Models")
    fig5.update_layout(yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig5, use_container_width=True)

with col6:
    st.subheader("⚡ Electric Range Distribution")
    range_df = filtered_df[filtered_df['Electric Range'] > 0]
    fig6 = px.histogram(range_df, x='Electric Range', nbins=40,
                        title="Distribution of Electric Range (miles)",
                        color_discrete_sequence=['#AB63FA'])
    st.plotly_chart(fig6, use_container_width=True)

# Key Insights
st.divider()
st.subheader("🔍 Key Insights")
col_a, col_b, col_c = st.columns(3)

with col_a:
    top_make = filtered_df['Make'].value_counts().idxmax()
    top_make_pct = round(filtered_df['Make'].value_counts().max() / len(filtered_df) * 100, 1)
    st.info(f"🏆 **{top_make}** dominates with **{top_make_pct}%** of all EVs")

with col_b:
    top_county = filtered_df['County'].value_counts().idxmax()
    top_county_count = filtered_df['County'].value_counts().max()
    st.success(f"📍 **{top_county} County** leads with **{top_county_count:,}** registrations")

with col_c:
    bev_pct = round(filtered_df['Electric Vehicle Type'].str.contains('Battery').sum() / len(filtered_df) * 100, 1)
    st.warning(f"🔋 **{bev_pct}%** of vehicles are fully electric **(BEV)**")

st.divider()
st.caption("Data Source: Washington State Department of Licensing | Built with Streamlit & Plotly")
