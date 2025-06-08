# Import Python packages
import streamlit as st
import pandas as pd
import requests
from snowflake.snowpark.functions import col

# App title and description
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Create Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# Input: Smoothie name
name_on_order = st.text_input('Smoothie Name:')
st.write('Name of your Smoothie will be:', name_on_order)

# Get fruit options from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options") \
                      .select(col('FRUIT_NAME'), col('SEARCH_ON'))
pd_df = my_dataframe.to_pandas()

# Input: Multiselect fruit ingredients
ingredients_list = st.multiselect(
    'Choose up to five ingredients:',
    pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

# If user selects ingredients
if ingredients_list:
    ingredients_string = ''
    
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        # Lookup search slug safely
        search_rows = pd_df.loc[pd_df['FRUIT_NAME'].str.lower() == fruit_chosen.lower(), 'SEARCH_ON']
        if not search_rows.empty:
            search_on = search_rows.iloc[0].strip().lower()
            st.subheader(f"{fruit_chosen} Nutrition Information")
            
            # Fetch data from external API
            try:
                response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
                response.raise_for_status()
                st.dataframe(data=response.json(), use_container_width=True)
            except requests.RequestException as e:
                st.error(f"Error fetching nutrition info for {fruit_chosen}: {e}")
        else:
            st.warning(f"No search key found for {fruit_chosen}")

    # Insert order into Snowflake if button is clicked
    if st.button('Submit Order'):
        insert_stmt = f"""
            INSERT INTO smoothies.public.orders(ingredients, name_on_order)
            VALUES ('{ingredients_string.strip()}', '{name_on_order}')
        """
        session.sql(insert_stmt).collect()
        st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")
