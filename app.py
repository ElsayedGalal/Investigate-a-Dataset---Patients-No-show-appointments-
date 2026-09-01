import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Medical Appointment No-Show Analytics", page_icon="🏥", layout="wide")
st.title("🏥 Medical Appointment No-Show Analytics Dashboard")

@st.cache_data
def load_data():
    df = pd.read_csv("medical_noshow.csv")
    df['ScheduledDay'] = pd.to_datetime(df['ScheduledDay'])
    df['AppointmentDay'] = pd.to_datetime(df['AppointmentDay'])
    df['WaitDays'] = (df['AppointmentDay'] - df['ScheduledDay']).dt.days
    df['Status'] = df['No-show'].apply(lambda x: 'Missed' if x == 'Yes' else 'Attended')
    return df

df = load_data()

# القائمة الجانبية للفلاتر
st.sidebar.header("🔍 Clinical Filters")
gender_filter = st.sidebar.multiselect("Select Gender", options=df['Gender'].unique(), default=df['Gender'].unique())
neighbourhood_filter = st.sidebar.multiselect("Select Neighbourhood", options=df['Neighbourhood'].unique(), default=df['Neighbourhood'].unique())
sms_filter = st.sidebar.radio("SMS Notification", options=["All", "Received SMS", "No SMS"])
age_range = st.sidebar.slider("Patient Age Range", min_value=int(df['Age'].min()), max_value=int(df['Age'].max()), value=(0, 95))

# تطبيق الفلاتر
filtered_df = df[
    (df['Gender'].isin(gender_filter)) &
    (df['Neighbourhood'].isin(neighbourhood_filter)) &
    (df['Age'].between(age_range[0], age_range[1]))
]

if sms_filter == "Received SMS":
    filtered_df = filtered_df[filtered_df['SMS_received'] == 1]
elif sms_filter == "No SMS":
    filtered_df = filtered_df[filtered_df['SMS_received'] == 0]

# 1. المؤشرات التشغيلية (Executive KPIs)
total_appts = len(filtered_df)
no_show_count = len(filtered_df[filtered_df['Status'] == 'Missed'])
no_show_rate = (no_show_count / total_appts * 100) if total_appts > 0 else 0
avg_wait = filtered_df['WaitDays'].mean() if total_appts > 0 else 0

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Total Appointments", f"{total_appts:,}")
kpi2.metric("Missed Appointments", f"{no_show_count:,}")
kpi3.metric("No-Show Rate", f"{no_show_rate:.1f}%")
kpi4.metric("Avg Waiting Days", f"{avg_wait:.1f} days")

st.markdown("---")

# 2. الرسوم البيانية التفاعلية
col1, col2 = st.columns(2)

with col1:
    st.subheader("📲 Impact of SMS Reminders on Attendance")
    sms_summary = filtered_df.groupby(['SMS_received', 'Status']).size().reset_index(name='Count')
    sms_summary['SMS_Label'] = sms_summary['SMS_received'].map({1: 'SMS Sent', 0: 'No SMS'})
    fig_sms = px.bar(sms_summary, x='SMS_Label', y='Count', color='Status', barmode='group',
                     color_discrete_map={'Attended': '#2a9d8f', 'Missed': '#e76f51'}, template="plotly_white")
    st.plotly_chart(fig_sms, use_container_width=True)

with col2:
    st.subheader("👥 Attendance Rate by Age Distribution")
    fig_age = px.histogram(filtered_df, x='Age', color='Status', nbins=20, barmode='stack',
                           color_discrete_map={'Attended': '#2a9d8f', 'Missed': '#e76f51'}, template="plotly_white")
    st.plotly_chart(fig_age, use_container_width=True)

st.markdown("---")

col3, col4 = st.columns(2)

with col3:
    st.subheader("🩺 Chronic Conditions Breakdown")
    conditions = {
        'Hypertension': filtered_df[filtered_df['Hipertension'] == 1]['Status'].value_counts().to_dict(),
        'Diabetes': filtered_df[filtered_df['Diabetes'] == 1]['Status'].value_counts().to_dict(),
        'Alcoholism': filtered_df[filtered_df['Alcoholism'] == 1]['Status'].value_counts().to_dict()
    }
    cond_df = pd.DataFrame(conditions).fillna(0).T.reset_index().rename(columns={'index': 'Condition'})
    if 'Missed' in cond_df.columns and 'Attended' in cond_df.columns:
        fig_cond = px.bar(cond_df, x='Condition', y=['Attended', 'Missed'], barmode='stack',
                          color_discrete_map={'Attended': '#2a9d8f', 'Missed': '#e76f51'}, template="plotly_white")
        st.plotly_chart(fig_cond, use_container_width=True)

with col4:
    st.subheader("📍 No-Show Rate Across Neighbourhoods")
    neigh_stats = filtered_df.groupby('Neighbourhood')['No-show'].apply(lambda x: (x == 'Yes').mean() * 100).reset_index(name='NoShowRate')
    neigh_stats = neigh_stats.sort_values(by='NoShowRate', ascending=True)
    fig_neigh = px.bar(neigh_stats, x='NoShowRate', y='Neighbourhood', orientation='h', template="plotly_white",
                       color='NoShowRate', color_continuous_scale='Blues')
    st.plotly_chart(fig_neigh, use_container_width=True)

# 3. جدول استعراض البيانات
st.markdown("---")
if st.checkbox("🔍 Inspect Raw Records"):
    st.dataframe(filtered_df.head(50), use_container_width=True)