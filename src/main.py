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


def getNproducts(df, N=5, brand=False):
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
        # If brand is True, add the brand and the keywords to the product string
        # This is created for the title_create function
        if brand == True:
            keywords = f"Keywords: {row.Keywords}\n"
            product_brand = "Brand: Guirca\n"
            products.append(
                f"{product_brand} {product_str} {keywords} {categories_str}"
            )
        else:
            products.append(f"{product_str} {categories_str}")
        count += 1
        if count >= max_iterations:
            break
    return products


def insertIn_df(df, product_keywords, index):
    # This function takes in a dataframe, a list of keywords and an index and inserts the keywords into the dataframe.
    if "Keywords" not in df.columns:
        df["Keywords"] = None  # Initialize the column with None values
    df.at[index, "Keywords"] = product_keywords
    return True


def title_create(product, language="spanish"):
    # """
    # This function takes in a product and returns a string with the corresponding title.
    # """
    chat = ChatOpenAI(model="gpt-3.5-turbo")
    messages = [
        SystemMessage(
            content="""
            You are an Amazon SEO expert. I will provide you with the brand, name, keywords and
            categories of several products. You need to deduce a title for each product 
            and create a structured response.
            Always response in the following JSON format: {"title": <response>}
            """
        ),
        HumanMessage(
            content=f"Deduce a title for this product: {product}\n Write your response in {language}"
            + """ You need to follow several rules:
            - The title should start with the brand name.
            - The title must contain between 150-200 characters.
            - All the parts of the title must contain keywords.
            - Format the product name so it's not all in uppercase.
            - Do not include the keywords rawly, but rather use them to create a coherent title.
            - After the brand and name, you must include (if possible) the variant of the product between brackets.
            Here is an example:
            Brand: Kaffe
            Name: Large French Press Coffee Maker 34oz/1L
            Keywords: Coffee, French Press, Large, Matte Black, Free Plastic, Camping, Travel
            Categories: Matte Black, Borosilicate Glass, Camping, 3 Level Filter
            The title should be: Kaffe Large French Press Coffee Maker (34oz / 1L) - Thick Borosilicate Glass and BPA-Free Plastic Coffee Press - Matte Black - Lightweight Travel & Camping Coffee Maker - 3 Level Filter French Press
            """
        ),
    ]
    response = chat.invoke(messages)
    json_resp = json.loads(
        response.content
    )  # Parse output into a valid str to insert into df
    product_title = json_resp["title"]
    return product_title


def main():
    # ----------------------------------------------------------------------------------
    # Linking keywords to products
    # ----------------------------------------------------------------------------------

    load_dotenv("../.env")
    # getKeywords(), while not having this method we create a list of keywords
    keywords = "Disfraz Adulto, Carnaval, Disfraz Halloween, Disfraces chulos, Disfraces para fiestas"
    # getdf(), while not having this methos we take the file from the docs folder
    # For interactive jupyter notebook use the following path
    # df = pd.read_excel(
    #    "C:/Users/alexa/OneDrive/Escritorio/AI Agency Project/GenAI/proyecto_alfon/docs/articulos_guirca.xlsx",
    # )
    df = pd.read_excel(r"docs\articulos_guirca.xlsx")
    # clean the df to only have the columns we need
    df_cleaned = df[["DESCRIPCION", "COLORES", "USUARIO", "TEMA"]]
    # copy the df to insert the keywords without modifying the original df
    df_duplicate = df_cleaned.copy()
    products = getNproducts(df_cleaned, 5)
    # Link keywords and insert them into a new df
    index = 0
    for product in products:
        product_keywords = keyword_link(product, keywords)
        print(product_keywords)
        insertIn_df(df_duplicate, product_keywords, index)
        index = index + 1

    # ----------------------------------------------------------------------------------
    # Creating Titles
    # ----------------------------------------------------------------------------------
    products = getNproducts(df_duplicate, 5, brand=True)
    for product in products:
        product_title = title_create(product)
        print(product_title)


if __name__ == "__main__":
    main()
