# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col


# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
  """Choose the fruits you want in your custom Smoothie!
  """)

# Create Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

name_on_order = st.text_input('Smoothie Name:')
st.write('Name of your Smoothie will be:', name_on_order)

# Get fruit options from the table
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

# Multiselect input
ingredients_list = st.multiselect(
    'Choose upto five ingredients:', 
    my_dataframe,
    max_selections=5
)

# Handle selection
if ingredients_list:
    ingredients_string = ' '.join(ingredients_list)
    st.write(ingredients_string)
    
    my_insert_stmt = f"""insert into smoothies.public.orders(ingredients, name_on_order)
                         values ('{ingredients_string}', '{name_on_order}')"""

    time_to_insert = st.button('Submit Order')
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")

    
import requests
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
st.text(smoothiefroot_response)
