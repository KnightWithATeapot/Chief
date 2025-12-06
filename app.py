import streamlit as st
import asyncio
import traceback

from backend.orchestrator.orchestrator import Orchestrator
from backend.agents.ingredient_agent import IngredientAgent
from backend.agents.recipe_agent import RecipeAgent
from backend.agents.nutrition_agent import NutritionAgent
from backend.agents.validation_agent import ValidationAgent
from backend.llm_client import GroqClient

from APIKey import GROQ_API_KEY


# ─────────────────────────────────────────────────────────────
# Init LLM + Orchestrator
# ─────────────────────────────────────────────────────────────
@st.cache_resource
def load_orchestrator():
    llm = GroqClient(GROQ_API_KEY)
    model = "llama-3.3-70b-versatile"

    return Orchestrator(
        ingredient_agent=IngredientAgent(llm, model),
        recipe_agent=RecipeAgent(llm, model),
        nutrition_agent=NutritionAgent(llm, model),
        validation_agent=ValidationAgent(llm, model),
    )


orch = load_orchestrator()


# ─────────────────────────────────────────────────────────────
# Async handler — создаём собственный локальный loop каждый раз
# ─────────────────────────────────────────────────────────────
def run_async(func, *args, **kwargs):
    """
    Безопасно выполняет async-функцию внутри Streamlit:
    - Не создаёт и не закрывает event loop
    - Работает, даже если Streamlit уже запустил свой loop
    - Избегает 'Event loop is closed'
    """
    coro = func(*args, **kwargs)

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    if loop.is_running():
        return asyncio.run_coroutine_threadsafe(coro, loop).result()

    return loop.run_until_complete(coro)


# ─────────────────────────────────────────────────────────────
# UI
# ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="Chief – AI Recipes", layout="wide")
st.title("👨‍🍳 Chief — умный подбор рецептов по продуктам")

st.write("Загрузи список продуктов — и получи рецепты, которые можно приготовить из того, что есть.")

raw_input = st.text_area(
    "Введите продукты (через запятую)",
    placeholder="Например: яйцо, помидор, сыр, макароны…",
    height=100
)

if st.button("Подобрать рецепты"):
    if not raw_input.strip():
        st.warning("Введите хотя бы один продукт!")
        st.stop()

    with st.spinner("Повар думает… 🧠🍳"):
        try:
            result = run_async(orch.run, raw_input)
        except Exception as e:
            st.error("Произошла ошибка при выполнении пайплайна.")
            st.exception(e)
            # Покажем трассировку для отладки
            st.text("Traceback:")
            st.text(traceback.format_exc())
            st.stop()

    if "error" in result:
        st.error(result["error"])
        st.stop()

    # ─────────────────────────────────────────────────────────
    # Блок 1 — Нормализованные ингредиенты
    # ─────────────────────────────────────────────────────────
    st.subheader("🧂 Нормализованные ингредиенты")
    st.json(result["ingredients"])

    # ─────────────────────────────────────────────────────────
    # Блок 2 — Рецепты
    # ─────────────────────────────────────────────────────────
    st.subheader("🍲 Рецепты")
    recipes = result["recipes"]

    for recipe in recipes:
        with st.expander(recipe.get("title", "Без названия")):
            st.markdown("### Ингредиенты")
            st.write(", ".join(recipe.get("ingredients", [])))

            st.markdown("### Шаги приготовления")
            for step in recipe.get("steps", []):
                st.write(f"- {step}")

            st.markdown("### ⏱ Время")
            st.write(f"{recipe.get('cook_time_minutes', '—')} минут")

            st.markdown("### 🔥 Калорийность")
            st.write(f"{recipe.get('calories', '—')} ккал")

            st.markdown("### ❤️ Полезность")
            st.write(recipe.get("healthiness", "—"))

            st.markdown("### ℹ️ Короткое описание")
            st.write(recipe.get("summary", ""))

    # ─────────────────────────────────────────────────────────
    # Блок 3 — Валидация
    # ─────────────────────────────────────────────────────────
    st.subheader("✔ Проверка корректности")
    val = result.get("validation", {"valid": False, "issues": ["Нет данных"]})

    if val.get("valid"):
        st.success("Все рецепты корректны 🎉")
    else:
        st.error("Обнаружены проблемы:")
        st.json(val.get("issues", []))
