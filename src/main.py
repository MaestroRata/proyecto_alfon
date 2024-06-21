import os
import json
import pandas as pd
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage


def keyword_link(product, keywords):
    # """
    # This function takes in a product and a list of keywords and returns a
    # string with the corresponding keywords for the product.
    # """
    chat = ChatOpenAI(model="gpt-3.5-turbo")
    messages = [
        SystemMessage(
            content="""
            You are an Amazon SEO expert. I will provide you with the name and 
            categories of several products, as well as a bunch of keywords. You
            need to deduce which keywords correspond to each product and create a response.
            Always response in the following JSON format: {"keywords": <response>} 
            """
        ),
        HumanMessage(content=f"keywords: {keywords}\n" f"products: {product}\n"),
    ]
    response = chat.invoke(messages)
    json_resp = json.loads(
        response.content
    )  # Parse output into a valid str to insert into df
    product_keywords = json_resp["keywords"]
    string = ""
    count = 0
    for item in product_keywords:
        if count == 0:
            string = string + item
            count = count + 1
        else:
            string = string + ", " + item
    return {string}


def getNproducts(df, N=5):
    # hardcoded method to get a list of products from the df
    # for testing porpouses only iterates 'n' times
    count = 0
    max_iterations = N
    products = []
    for row in df.itertuples(index=False):  # Iterate over the rows of the dataframe
        categories = [
            row.COLORES,
            row.USUARIO,
            row.TEMA,
        ]
        product_str = f"Name: {row.DESCRIPCION}\n"
        categories_str = f"Categories: {', '.join(str(v) for v in categories)}"
        products.append(product_str + categories_str)
        count += 1
        if count >= max_iterations:
            break
    return products


def insertIn_df(df, product_keywords, index):
    if "Keywords" not in df.columns:
        df["Keywords"] = None  # Initialize the column with None values
    df.at[index, "Keywords"] = product_keywords
    return True


def main():
    # ----------------------------------------------------------------------------------
    # Linking keywords to products
    # ----------------------------------------------------------------------------------

    load_dotenv("../.env")
    # getKeywords(), while not having this method we create a list of keywords
    keywords = "Disfraz Adulto, Carnaval, Disfraz Halloween, Disfraces chulos, Disfraces para fiestas"
    # getdf(), while not having this methos we take the file from the docs folder
    df = pd.read_excel(
        "../docs/ARTICULOS ANTIGUOS GUIRCA_ESP.xlsx",
        sheet_name="Hoja1",
        engine="openpyxl",
    )
    # clean the df
    df_cleaned = df[["DESCRIPCION", "COLORES", "USUARIO", "TEMA"]]
    # copy the df
    df_duplicate = df_cleaned.copy()
    products = getNproducts(df_cleaned, 3)
    # Link keywords and insert them into a new df
    index = 0
    for product in products:
        product_keywords = keyword_link(product, keywords)
        insertIn_df(df_duplicate, product_keywords, index)
        index = index + 1

    # ----------------------------------------------------------------------------------
    # Creating Titles
    # ----------------------------------------------------------------------------------
