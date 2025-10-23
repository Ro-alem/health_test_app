import streamlit as st
import pandas as pd
from io import BytesIO
from fpdf import FPDF
from datetime import datetime

st.set_page_config(page_title="Когнитивная диагностика", layout="centered")

# Тесты по возрасту
tests_by_age = {
    0: [
        {"key": "Bayley Scales (BSID-III)", "min": 0, "max": 150},
        {"key": "ASQ-3 (проценты)", "min": 0, "max": 100},
        {"key": "M-CHAT-R/F", "min": 0, "max": 20}
    ],
    5: [
        {"key": "NEPSY-II (stens)", "min": 0, "max": 20},
        {"key": "KABC-II (IQ)", "min": 40, "max": 160},
        {"key": "CARS-2", "min": 0, "max": 60},
        {"key": "Conners EC (T)", "min": 0, "max": 100},
        {"key": "Stroop (секунды)", "min": 0, "max": 120},
        {"key": "WPPSI-IV (IQ)", "min": 40, "max": 160},
        {"key": "Vineland Adaptive", "min": 0, "max": 150}
    ],
    10: [
        {"key": "WISC-V (IQ)", "min": 40, "max": 160},
        {"key": "Stroop (секунды)", "min": 0, "max": 120},
        {"key": "CPT (ошибки %)", "min": 0, "max": 100},
        {"key": "TMT A (сек)", "min": 0, "max": 300},
        {"key": "TMT B (сек)", "min": 0, "max": 300},
        {"key": "SRS-2 (T)", "min": 0, "max": 120},
        {"key": "RAVLT (слов)", "min": 0, "max": 15},
        {"key": "Tower of London (категории)", "min": 0, "max": 6},
        {"key": "Digit Span (цифры)", "min": 0, "max": 9}
    ],
    15: [
        {"key": "WCST (категории)", "min": 0, "max": 6},
        {"key": "TMT B (сек)", "min": 0, "max": 180},
        {"key": "RAVLT (слов)", "min": 0, "max": 15},
        {"key": "PHQ-A (баллы)", "min": 0, "max": 27},
        {"key": "CPT-II (ошибки %)", "min": 0, "max": 100},
        {"key": "Tower of Hanoi (ходы)", "min": 0, "max": 25},
        {"key": "Emotional Stroop (разница сек)", "min": 0, "max": 120}
    ],
    18: [
        {"key": "MoCA (баллы)", "min": 0, "max": 30},
        {"key": "WAIS-IV (IQ)", "min": 40, "max": 160},
        {"key": "WCST (категории)", "min": 0, "max": 6},
        {"key": "TMT B (сек)", "min": 0, "max": 180},
        {"key": "Stroop (секунды/ошибки)", "min": 0, "max": 120},
        {"key": "GAD-7 (баллы)", "min": 0, "max": 21},
        {"key": "BDI-II (баллы)", "min": 0, "max": 63},
        {"key": "RAVLT (слов)", "min": 0, "max": 15}
    ]
}

# Рекомендации
recommendations = {
    0: {
        "Норма": "Развитие соответствует возрасту. Сенсорные игры, общение, массаж.",
        "Риск": "Лёгкие задержки речи или моторики. Рекомендуется консультация логопеда и невролога.",
        "Отклонение": "Выраженные признаки задержки. Требуется срочная диагностика у специалистов."
    },
    5: {
        "Норма": "Ребёнок справляется с заданиями. Рекомендуются развивающие игры и чтение.",
        "Риск": "Есть трудности с вниманием. Уменьшите экранное время и обратитесь к нейропсихологу.",
        "Отклонение": "Явные отклонения. Нужна индивидуальная коррекция с логопедом и психологом."
    },
    10: {
        "Норма": "Когнитивные функции в норме. Продолжайте умственные тренировки.",
        "Риск": "Есть проблемы с вниманием. Рекомендуется работа с психологом.",
        "Отклонение": "Серьёзные трудности. Нужна диагностика у невролога и психиатра."
    },
    15: {
        "Норма": "Подросток в норме. Важно развивать самоконтроль и планирование.",
        "Риск": "Есть тревожность. Посоветуйтесь с психологом.",
        "Отклонение": "Выраженные нарушения. Срочная консультация психиатра."
    },
    18: {
        "Норма": "Когнитивные функции взрослого в норме. Поддерживайте активность.",
        "Риск": "Есть стресс или тревожность. Поможет психолог.",
        "Отклонение": "Выраженная депрессия. Нужна медицинская помощь."
    }
}

# Вычисление результата
def compute_overall_level(age, entered):
    tests = tests_by_age[age]
    total_percent = 0.0
    for val, test in zip(entered, tests):
        maxv = test["max"]
        if maxv == 0:
            continue
        name = test["key"].lower()
        if any(x in name for x in ("m-chat", "cars", "gad", "bdi", "phq", "cpt", "stroop", "tmt")):
            pct = max(0.0, (maxv - val) / maxv) * 100.0
        else:
            pct = max(0.0, val / maxv) * 100.0
        total_percent += pct
    avg_percent = total_percent / len(tests) if tests else 0
    if avg_percent >= 75:
        return "Норма", avg_percent
    elif avg_percent >= 50:
        return "Риск", avg_percent
    else:
        return "Отклонение", avg_percent

# Интерфейс
st.title("🧠 Когнитивная диагностика по возрастам")

age = st.selectbox("Возраст (лет):", [0, 5, 10, 15, 18])

entered_values = []
cols = st.columns(2)
for i, test in enumerate(tests_by_age[age]):
    value = cols[i % 2].number_input(
        f"{test['key']} (от {test['min']} до {test['max']})",
        min_value=test['min'], max_value=test['max'], value=test['min'], step=1
    )
    entered_values.append(value)

if st.button("Рассчитать результат"):
    level, avg_percent = compute_overall_level(age, entered_values)

    color = {"Норма": "#28a745", "Риск": "#ffc107", "Отклонение": "#dc3545"}[level]
    st.markdown(f"<h3 style='color:{color}'>Итог: {level}</h3>", unsafe_allow_html=True)
    st.write(f"Средний результат: {avg_percent:.1f}%")
    st.write("**Рекомендация:**", recommendations[age][level])

    df = pd.DataFrame([
        {"Тест": t["key"], "Результат": v, "Максимум": t["max"]}
        for t, v in zip(tests_by_age[age], entered_values)
    ])
    st.dataframe(df)

    # PDF отчёт
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Отчёт по когнитивной диагностике", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Возраст: {age} лет", ln=True)
    pdf.cell(0, 10, f"Итог: {level}", ln=True)
    pdf.cell(0, 10, f"Средний процент: {avg_percent:.1f}%", ln=True)
    pdf.multi_cell(0, 8, f"Рекомендации: {recommendations[age][level]}")
    pdf.ln(5)
    for row in df.to_dict(orient="records"):
        pdf.cell(0, 8, f"{row['Тест']}: {row['Результат']} / {row['Максимум']}", ln=True)

    buffer = BytesIO()
    pdf.output(buffer)
    st.download_button(
        label="📄 Скачать PDF отчёт",
        data=buffer.getvalue(),
        file_name=f"report_age_{age}.pdf",
        mime="application/pdf"
    )
