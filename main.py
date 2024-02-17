import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as gen_ai
import matplotlib.pyplot as plt
import numpy as np

# Load environment variables
load_dotenv()

# Configure Streamlit page settings
st.set_page_config(
    page_title="MediChat & CalorEase",
    page_icon=":brain:",  # Favicon emoji
    layout="wide",  # Page layout option
)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Set up Google Gemini-Pro AI model
gen_ai.configure(api_key=GOOGLE_API_KEY)
model = gen_ai.GenerativeModel('gemini-pro')

# Function to translate roles between Gemini-Pro and Streamlit terminology
def translate_role_for_streamlit(user_role):
    if user_role == "model":
        return "assistant"
    else:
        return user_role

# Initialize chat session in Streamlit if not already present
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

# Function to calculate BMR
def calculate_bmr(weight, height, age, sex):
    if sex == "male":
        bmr = 13.397 * weight + 4.799 * height - 5.677 * age + 88.362
    else:
        bmr = 9.247 * weight + 3.098 * height - 4.330 * age + 447.593
    return bmr

# Function to calculate daily calories
def calculate_daily_calories(bmr, activity_level):
    if activity_level == "sedentary":
        calories = bmr * 1.2
    elif activity_level == "lightly active":
        calories = bmr * 1.375
    elif activity_level == "moderately active":
        calories = bmr * 1.55
    else:
        calories = bmr * 1.725
    return calories

# Function to build nutritional values
def build_nutritional_values(weight, calories):
    protein_calories = weight * 4
    res_calories = calories - protein_calories
    carb_calories = calories / 2.
    fat_calories = calories - carb_calories - protein_calories
    res = {'Protein Calories': protein_calories, 'Carbohydrates Calories': carb_calories, 'Fat Calories': fat_calories}
    return res

# Function to extract grams from nutritional values
def extract_gram(table):
    protein_grams = table['Protein Calories'] / 4.
    carbs_grams = table['Carbohydrates Calories'] / 4.
    fat_grams = table['Fat Calories'] / 9.
    res = {'Protein Grams': protein_grams, 'Carbohydrates Grams': carbs_grams, 'Fat Grams': fat_grams}
    return res

# Streamlit UI
st.title("MediChat & Calorie Tracker")

# Create tabs
tabs = ["MediChat", "Calorie Tracker"]
selected_tab = st.radio("Choose Option", tabs)

if selected_tab == "MediChat":
    # Display MediChat tab
    st.title("👩‍⚕️- MediChat(Your personal medical assistant)")
    
    # Display the chat history
    for message in st.session_state.chat_session.history:
        with st.chat_message(translate_role_for_streamlit(message.role)):
            st.markdown(message.parts[0].text)

    # Input field for user's message
    user_prompt = st.chat_input("Ask medichat...")
    if user_prompt:
        # Add user's message to chat and display it
        st.chat_message("user").markdown(user_prompt)

        # Send user's message to Gemini-Pro and get the response
        gemini_response = st.session_state.chat_session.send_message(user_prompt)

        # Display Gemini-Pro's response
        with st.chat_message("assistant"):
            st.markdown(gemini_response.text)

elif selected_tab == "Calorie Tracker":
    # Display Calorie Tracker tab
    st.title("Holistic Calorie Tracker")

    # User input without default values
    weight_str = st.text_input("Enter your weight in KGs:")
    height_str = st.text_input("Enter your height in Cms:")
    age_str = st.text_input("Enter your age:")
    sex = st.radio("Select your sex:", options=["male", "female"])
    activity_level = st.selectbox(
        "Select your activity level:",
        options=["sedentary", "lightly active", "moderately active", "very active"],
    )

    # Convert input values to float if not empty
    weight = float(weight_str) if weight_str else None
    height = float(height_str) if height_str else None
    age = float(age_str) if age_str else None

    # Calculate BMR and Daily Calories
    if weight is not None and height is not None and age is not None:
        bmr = calculate_bmr(weight, height, age, sex)
        calories = calculate_daily_calories(bmr, activity_level)

        # Display BMR and Daily Calories
        st.subheader("Your Daily Calorie Needs:")
        st.write(f"Basal Metabolic Rate (BMR): {bmr:.2f} calories")
        st.write(f"Daily Caloric Needs: {calories:.2f} calories")

        # Build Nutritional Values and Extract Grams
        nutritional_values = build_nutritional_values(weight, calories)
        gram_info = extract_gram(nutritional_values)

        # Display Nutritional Information
        st.subheader("Nutritional Information:")
        st.write(f"Protein Grams: {gram_info['Protein Grams']:.2f}g")
        st.write(f"Carbohydrates Grams: {gram_info['Carbohydrates Grams']:.2f}g")
        st.write(f"Fat Grams: {gram_info['Fat Grams']:.2f}g")

        # Bar Plot for Nutritional Information
        fig, ax = plt.subplots(figsize=(8, 6))
        nutrients = ["Protein", "Carbohydrates", "Fat"]
        values = [gram_info["Protein Grams"], gram_info["Carbohydrates Grams"], gram_info["Fat Grams"]]
        ax.bar(nutrients, values, color=["green", "orange", "red"])
        ax.set_ylabel("Grams")
        ax.set_title("Nutritional Information (Grams)")
        st.subheader("Nutritional Information (Grams):")
        st.pyplot(fig)

        # Doughnut Chart for Calorie Distribution
        labels = ["Protein", "Carbohydrates", "Fat"]
        sizes = [nutritional_values["Protein Calories"], nutritional_values["Carbohydrates Calories"], nutritional_values["Fat Calories"]]
        colors = ["green", "orange", "red"]
        explode = (0.1, 0, 0)

        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, autopct="%1.1f%%", colors=colors, startangle=90, explode=explode)
        ax.axis("equal")
        ax.set_title("Calorie Distribution")
        st.subheader("Calorie Distribution:")
        st.pyplot(fig)

# Ensure you're closing the plots to avoid potential issues
plt.close("all")
