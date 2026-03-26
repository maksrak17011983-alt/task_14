import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="GitHub Monitor", layout="wide")

# 1. Отримання даних з API
def get_github_data(user):
    url = f"https://api.github.com/users/{user}/repos"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

st.title("📊 Моніторинг проєктів у GitHub")
username = st.text_input("Введіть нікнейм користувача GitHub:", value="streamlit")

if username:
    data = get_github_data(username)
    
    if data:
        # Перетворюємо дані в таблицю
        df = pd.DataFrame(data)
        
        # Вибираємо потрібні колонки
        df_display = df[['name', 'stargazers_count', 'forks_count', 'open_issues_count']]
        df_display.columns = ['Назва проєкту', 'Зірки ⭐', 'Форки 🍴', 'Issues 🛠']

        # --- БЛОК 1: Рейтинг за зірками ---
        st.subheader("🏆 Рейтинг проєктів за зірками")
        fig_stars = px.bar(df_display.sort_values('Зірки ⭐', ascending=False).head(10), 
                           x='Зірки ⭐', y='Назва проєкту', orientation='h',
                           color='Зірки ⭐', color_continuous_scale='Viridis')
        st.plotly_chart(fig_stars, use_container_width=True)

        # --- БЛОК 2: Граф активності (Issues vs Forks) ---
        st.subheader("📈 Граф активності та популярності")
        fig_activity = px.scatter(df_display, x='Зірки ⭐', y='Issues 🛠', 
                                  size='Форки 🍴', hover_name='Назва проєкту',
                                  title="Співвідношення популярності та відкритих задач")
        st.plotly_chart(fig_activity, use_container_width=True)

        # --- БЛОК 3: Аналіз динаміки (Таблиця) ---
        st.subheader("📋 Аналіз динаміки розробки")
        st.dataframe(df_display.sort_values('Issues 🛠', ascending=False), use_container_width=True)
        
        st.info(f"Всього знайдено репозиторіїв для {username}: {len(df)}")
    else:
        st.error("Користувача не знайдено або перевищено ліміт запитів API.")
