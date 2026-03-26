import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import plotly.express as px
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta

# 1. Налаштування сторінки
st.set_page_config(page_title="Екологічна аналітика", layout="wide")

# 2. Генерація даних (API/CSV імітація)
@st.cache_data
def get_eco_data():
    locations = {
        'Київ': [50.45, 30.52],
        'Дніпро': [48.46, 35.04],
        'Запоріжжя': [47.83, 35.13],
        'Кривий Ріг': [47.91, 33.39]
    }
    
    data = []
    start_date = datetime.now() - timedelta(days=30)
    
    for city, coords in locations.items():
        for i in range(30):
            date = start_date + timedelta(days=i)
            # Базовий рівень PM2.5 + випадкові коливання
            pm_value = np.random.uniform(10, 80) if city != 'Кривий Ріг' else np.random.uniform(50, 120)
            data.append({
                'Дата': date,
                'Місто': city,
                'lat': coords[0],
                'lon': coords[1],
                'PM2.5': round(pm_value, 2)
            })
    return pd.DataFrame(data)

df = get_eco_data()

# 3. Інтерфейс
st.title("🌱 Моніторинг та прогноз якості повітря (PM2.5)")
st.markdown("---")

# Карта забруднення
st.subheader("📍 Карта поточного забруднення")
latest_data = df[df['Дата'] == df['Дата'].max()]

m = folium.Map(location=[48.5, 31.2], zoom_start=6, tiles="cartodbpositron")

for _, row in latest_data.iterrows():
    # Колір залежно від рівня PM2.5 (ВООЗ рекомендує < 15)
    color = 'green' if row['PM2.5'] < 25 else 'orange' if row['PM2.5'] < 50 else 'red'
    
    folium.CircleMarker(
        location=[row['lat'], row['lon']],
        radius=row['PM2.5']/3,
        popup=f"{row['Місто']}: {row['PM2.5']} µg/m³",
        color=color,
        fill=True,
        fill_opacity=0.6
    ).add_to(m)

st_folium(m, width=1000, height=500)

# 4. Аналіз трендів
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Аналіз трендів")
    selected_city = st.selectbox("Оберіть місто для аналізу:", df['Місто'].unique())
    city_df = df[df['Місто'] == selected_city]
    fig = px.line(city_df, x='Дата', y='PM2.5', title=f"Динаміка PM2.5 у м. {selected_city}")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # 5. Прогноз (Linear Regression)
    st.subheader("🔮 Прогноз рівня PM2.5")
    
    # Готуємо дані для моделі
    city_df['days_from_start'] = (city_df['Дата'] - city_df['Дата'].min()).dt.days
    X = city_df[['days_from_start']].values
    y = city_df['PM2.5'].values
    
    model = LinearRegression().fit(X, y)
    
    # Прогноз на завтра
    next_day = [[city_df['days_from_start'].max() + 1]]
    prediction = model.predict(next_day)[0]
    
    st.metric(label=f"Очікуваний рівень завтра ({selected_city})", 
              value=f"{round(prediction, 2)} µg/m³",
              delta=f"{round(prediction - city_df['PM2.5'].iloc[-1], 2)} від сьогодні")
    
    st.write("Прогноз побудовано за допомогою моделі лінійної регресії на основі даних за останні 30 днів.")
