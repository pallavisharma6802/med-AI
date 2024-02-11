import streamlit as st
import requests
import pandas as pd
from streamlit_echarts import st_echarts
from ImageFinder import get_images_links as find_image
from PIL import Image

# Define the URL of your FastAPI backend
FASTAPI_URL = "http://127.0.0.1:8000"

def main():
    st.title("Custom Food Recommendation")

    st.sidebar.header('Nutritional values:')
    Calories = st.sidebar.slider('Calories', 0, 2000, 500)
    FatContent = st.sidebar.slider('FatContent', 0, 100, 50)
    SaturatedFatContent = st.sidebar.slider('SaturatedFatContent', 0, 13, 0)
    CholesterolContent = st.sidebar.slider('CholesterolContent', 0, 300, 0)
    SodiumContent = st.sidebar.slider('SodiumContent', 0, 2300, 400)
    CarbohydrateContent = st.sidebar.slider('CarbohydrateContent', 0, 325, 100)
    FiberContent = st.sidebar.slider('FiberContent', 0, 50, 10)
    SugarContent = st.sidebar.slider('SugarContent', 0, 40, 10)
    ProteinContent = st.sidebar.slider('ProteinContent', 0, 40, 10)
    nutrition_input = [Calories, FatContent, SaturatedFatContent, CholesterolContent, SodiumContent, CarbohydrateContent, FiberContent, SugarContent, ProteinContent]
    
    st.sidebar.header('Recommendation options (OPTIONAL):')
    ingredients = st.sidebar.text_input('Specify ingredients to include in the recommendations separated by ";" :',placeholder='Ingredient1;Ingredient2;...')
    st.sidebar.caption('Example: Milk;eggs;butter;chicken...')
    n_neighbors = st.sidebar.slider('Number of recommendations', 5, 20,step=5)

    params = {
        "n_neighbors": n_neighbors,
        "return_distance": False
    }

    if st.sidebar.button("Get Recommendations"):
        # Convert nutrition_input and ingredients to appropriate format
        ingredients = ingredients.split(';')
        # Prepare the request data
        data = {
            "nutrition_input": nutrition_input,
            "ingredients": ingredients,
            "params": params
        }

        # Send POST request to FastAPI backend
        response = requests.post(f"{FASTAPI_URL}/predict/", json=data)

        if response.status_code == 200:
            recommendations = response.json()["output"]
            st.subheader("Recommended Recipes:")
            if recommendations:
                for recipe in recommendations:
                    recipe_name = recipe['Name']
                    hover_text = f"Hovering over '{recipe_name}'"
                    expander = st.expander(recipe_name, expanded=False)
                    with expander:
                        img_link=find_image(recipe_name)
                        recipe_img=f'<div><center><img src={img_link} alt={recipe_name}></center></div>'
                        st.markdown(recipe_img,unsafe_allow_html=True)
                        st.markdown(f'<h5 style="text-align: center;font-family:sans-serif;">Nutritional Values (g):</h5>', unsafe_allow_html=True)  
                        nutrition_df = pd.DataFrame({"Nutrition": ['Calories', 'FatContent', 'SaturatedFatContent', 'CholesterolContent', 'SodiumContent', 'CarbohydrateContent', 'FiberContent', 'SugarContent', 'ProteinContent'], "Value": nutrition_input})
                        st.dataframe(nutrition_df)
                        expander.markdown(f'<h5 style="text-align: center;font-family:sans-serif;">Ingredients:</h5>', unsafe_allow_html=True)
                        for ingredient in recipe['RecipeIngredientParts']:
                            st.markdown(f"- {ingredient}")
                        expander.markdown(f'<h5 style="text-align: center;font-family:sans-serif;">Recipe Instructions:</h5>', unsafe_allow_html=True)    
                        for instruction in recipe['RecipeInstructions']:
                            st.markdown(f"- {instruction}")
                        nutrition_keys = ['Calories', 'FatContent', 'SaturatedFatContent', 'CholesterolContent', 'SodiumContent', 'CarbohydrateContent', 'FiberContent', 'SugarContent', 'ProteinContent']
                        values = [recipe[key] for key in nutrition_keys]
                        chart_options = {
                            "title": {"text": "Nutritional Values", "left": "center"},
                            "tooltip": {"trigger": "item", "formatter": "{a} <br/>{b}: {c}g ({d}%)"},
                            "legend": {"orient": "vertical", "left": 10},
                            "series": [
                                {
                                    "name": "Nutrition values",
                                    "type": "pie",
                                    "radius": ["50%", "70%"],
                                    "avoidLabelOverlap": False,
                                    "label": {"show": False, "position": "center"},
                                    "emphasis": {"label": {"show": True, "fontSize": "30", "fontWeight": "bold"}},
                                    "labelLine": {"show": False},
                                    "data": [{"value": value, "name": key} for key, value in zip(nutrition_keys, values)]
                                }
                            ]
                        }
                        st_echarts(options=chart_options, height="400px", key=hover_text)

        else:
            st.error("Failed to retrieve recommendations. Please try again.")

if __name__ == "__main__":
    main()
