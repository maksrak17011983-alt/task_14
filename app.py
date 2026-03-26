import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# --- 1. Налаштування сторінки ---
st.set_page_config(
    page_title="Система оцінки ризику підприємств",
    page_icon="🛡️",
    layout="wide"
)

# --- 2. Генерація та підготовка даних (імітація CSV) ---
@st.cache_data
def load_company_data():
    # Створюємо набір даних згідно з вимогами завдання (фінансові, податкові, публічні ознаки)
    data = {
        'Назва підприємства': [
            'ТОВ "Техно-Світ"', 'ПП "Агро-Вектор"', 'АТ "Енерго-Холдинг"', 
            'ТОВ "Буд-Гарант"', 'ПАТ "Логістик-Юніон"', 'ФОП Коваленко О.М.'
        ],
        'Фінансовий борг (млн грн)': [0.15, 4.80, 1.20, 9.50, 0.05, 0.40],
        'Податковий борг': [0, 1, 0, 1, 0, 0],  # 1 - наявний, 0 - відсутній
        'Кількість судових справ': [2, 24, 5, 42, 1, 3],
        'Термін діяльності (років)': [12, 3, 8, 1, 15, 6],
        'Публічні згадки (негатив)': [0, 5, 1, 8, 0, 1]
    }
    return pd.DataFrame(data)

df = load_company_data()

# --- 3. Математична модель обчислення інтегрального індексу ризику ---
def calculate_integral_risk(row):
    """
    Обчислює індекс від 0 до 100 балів.
    Чим вищий бал — тим небезпечніше підприємство.
    """
    # Коефіцієнти впливу (ваги)
    f_debt_weight = row['Фінансовий борг (млн грн)'] * 4.5
    tax_weight = row['Податковий борг'] * 35.0
    court_weight = row['Кількість судових справ'] * 1.2
    media_weight = row['Публічні згадки (негатив)'] * 5.0
    experience_bonus = row['Термін діяльності (років)'] * 1.5
    
    # Розрахунок
    total_score = f_debt_weight + tax_weight + court_weight + media_weight - experience_bonus
    
    # Обмеження діапазону [0, 100]
    return int(min(max(total_score, 0), 100))

df['Індекс ризику'] = df.apply(calculate_integral_risk, axis=1)

# --- 4. Головний інтерфейс ---
st.title("🔍 Система інтелектуальної оцінки ризику контрагентів")
st.markdown("""
Даний інструмент дозволяє провести експрес-аналіз підприємства за інтегральним показником ризику, 
враховуючи фінансову стійкість, податкову дисципліну та публічну репутацію.
""")
st.write("---")

# Вибір об'єкта аналізу
selected_name = st.selectbox("Оберіть підприємство для детальної перевірки:", df['Назва підприємства'])
company = df[df['Назва підприємства'] == selected_name].iloc[0]
risk_val = company['Індекс ризику']

# Розбивка на колонки: Шкала та Деталі
col1, col2 = st.columns([1, 1])

with col1:
    # --- 5. Візуалізація: Gauge-chart ---
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = risk_val,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Інтегральний показник", 'font': {'size': 24}},
        gauge = {
            'axis': {'range': [0, 100], 'tickwidth': 1},
            'bar': {'color': "black"},
            'steps': [
                {'range': [0, 40], 'color': "#2ecc71"},   # Низький (Зелений)
                {'range': [40, 70], 'color': "#f1c40f"}, # Середній (Жовтий)
                {'range': [70, 100], 'color': "#e74c3c"} # Високий (Червоний)
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': risk_val
            }
        }
    ))
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("📋 Результати аналізу")
    if risk_val > 70:
        st.error(f"**Статус: КРИТИЧНИЙ РИЗИК ({risk_val}/100)**")
        st.write("Рекомендація: Припинити співпрацю або вимагати 100% передоплату.")
    elif risk_val > 40:
        st.warning(f"**Статус: СЕРЕДНІЙ РИЗИК ({risk_val}/100)**")
        st.write("Рекомендація: Провести розширений юридичний аудит.")
    else:
        st.success(f"**Статус: НАДІЙНИЙ КОНТРАГЕНТ ({risk_val}/100)**")
        st.write("Рекомендація: Робота в штатному режимі.")
    
    # Коротке резюме факторів
    st.info(f"""
    **Ключові показники:**
    - Податковий борг: {'Присутній ❌' if company['Податковий борг'] == 1 else 'Відсутній ✅'}
    - Фінансові зобов'язання: {company['Фінансовий борг (млн грн)']} млн грн
    - Судовий фон: {company['Кількість судових справ']} відкритих проваджень
    """)

# --- 6. Загальний реєстр з підсвіткою ---
st.write("---")
st.subheader("📊 Порівняльний реєстр підприємств")

def color_risk(val):
    if val > 70: return 'background-color: #ffcccc; color: #cc0000; font-weight: bold'
    if val > 40: return 'background-color: #fff4cc'
    return ''

# Відображення таблиці з умовним форматуванням
st.dataframe(
    df.style.applymap(color_risk, subset=['Індекс ризику']),
    use_container_width=True
)

st.caption("Система автоматично підсвічує компанії з високим ризиком у червоний колір.")
