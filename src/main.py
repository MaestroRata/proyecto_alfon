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
            The response must be a single string with all the keywords separated by commas.
            """
        ),
        HumanMessage(content=f"keywords: {keywords}\n" f"products: {product}\n"),
    ]
    response = chat.invoke(messages)
    json_resp = json.loads(
        response.content
    )  # Parse output into a valid str to insert into df
    return {json_resp["keywords"]}


def getNproducts(df, N=5, brand=False, title=False):
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
        # Created for the title_create function
        if brand == True:
            keywords = f"Keywords: {row.Keywords}\n"
            product_brand = "Brand: Guirca\n"
            products.append(
                f"{product_brand} {product_str} {keywords} {categories_str}"
            )
        # Created for the bullet_points_create function
        if title == True:
            keywords = f"Keywords: {row.Keywords}\n"
            product_title = f"Title: {row.Title}\n"
            # Created for the description_create function
            products.append(
                f"{product_title} {product_str} {keywords} {categories_str}"
            )
        else:
            products.append(f"{product_str} {categories_str}")
        count += 1
        if count >= max_iterations:
            break
    return products


def insertIn_df(df, llm_output, index, column):
    # This function takes in a dataframe, a list of keywords and an index and inserts the keywords into the dataframe.
    if column not in df.columns:
        df[column] = None  # Initialize the column with None values
    df.at[index, column] = llm_output
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
            + """ You need to follow these rules:
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


def bullet_points_create(product, language="spanish"):
    # """
    # This function takes in a product and returns a string with the corresponding bullet points.
    # """
    chat = ChatOpenAI(model="gpt-3.5-turbo")
    messages = [
        SystemMessage(
            content="""
            You are an Amazon SEO expert. I will provide you with the brand, name, keywords and
            categories of several products. You need to deduce bullet points for each product 
            and create a structured response.
            Always response in the following JSON format: {"bullet_points": <response>}
            """
        ),
        HumanMessage(
            content=f"Deduce bullet points for this product: {product}\n Write your response in {language}"
            + """ You need to follow these rules:
            - You must create 5 bullet points.
            - The bullet points must contain all the keywords.
            - Every bullet point must contain 500 characters.
            - Format the product name so it's not all in uppercase.
            - Do not include the keywords rawly, but rather use them to create coherent bullet points.
            - Add an emoji at the beginning of each bullet point.
            Here is an example:
            Title: Kaffe Large French Press Coffee Maker (34oz / 1L) - Thick Borosilicate Glass and BPA-Free Plastic Coffee Press - Matte Black - Lightweight Travel & Camping Coffee Maker - 3 Level Filter French Press
            Name: Large French Press Coffee Maker 34oz/1L
            Keywords: Coffee, French Press, Large, Matte Black, Free Plastic, Camping, Travel
            Categories: Matte Black, Borosilicate Glass, Camping, 3 Level Filter
            The bullet points should be: 
            🌱 UNIVERSAL ECO-FRIENDLY DESIGN: Kaffe french press coffee maker will be your ideal choice because of its efficient and timeless design, with no need for plastic capsules, coffee pods or paper filters. The coffee pot is made from taste-neutral borosilicate glass that ensures years of use. This classic French press coffee maker is the simplest way to a fragrant brew.
            ♨️ KEEP YOUR COFFEE HOT FOR A LONG TIME: Our french press coffee maker will keep your coffee, tea or beverage warm for up to 4 times longer than a glass coffee press. Its double wall insulation is designed to keep the heat inside and away from your hands. It can be the key to jump start your day.
            ☕️ LONG-LASTING TASTE AND AROMATIC COFFEE OILS ARE GUARANTEED:This coffee press is designed with dual-filter screen and composed of a sandwich of steel mesh held in place to increase the smoothness of the brew and let the orginal taste of grounds last for hours.
            ⚙️ BALANCE BETWEEN CAPACITY, LONG LASTING USAGE AND SAFETY. Kaffe large french press has a 6-Cup Capacity (800 ml / 27 oz). An additional filter included with our french press coffee ensures long lasting and durable usage with no rust. At the same time, it maintains the pure taste of coffee with the best aromas without any additional VS cheap analoges.
            💯 LIFETIME MANUFACTURER'S WARRANTY - We take pride the quality of our Kaffe camping coffee pot and our record speaks for itself. We promise to treat you like family! Covers any damage or defect. Money back guarantee!
            """
        ),
    ]
    response = chat.invoke(messages)
    json_resp = json.loads(
        response.content
    )  # Parse output into a valid str to insert into df
    product_bullet_points = json_resp["bullet_points"]
    return product_bullet_points


def description_create(product, language="spanish"):
    # """
    # This function takes in a product and returns a string with the corresponding description.
    # """
    chat = ChatOpenAI(model="gpt-3.5-turbo")
    messages = [
        SystemMessage(
            content="""
            You are an Amazon SEO expert. I will provide you with the brand, name, keywords and
            categories of several products. You need to deduce a description for each product 
            and create a structured response.
            Always response in the following JSON format: {"description": <response>}
            """
        ),
        HumanMessage(  # Change this ------------------------------
            content=f"Deduce a description for this product: {product}\n Write your response in {language}"
            + """ You need to follow these rules:
            - The description must contain 2000 characters.
            - The description must contain all the keywords.
            - Do not include the keywords rawly, but rather use them to create coherent descriptions.
            Here is an example:
            Title: Kaffe Large French Press Coffee Maker (34oz / 1L) - Thick Borosilicate Glass and BPA-Free Plastic Coffee Press - Matte Black - Lightweight Travel & Camping Coffee Maker - 3 Level Filter French Press
            Name: Large French Press Coffee Maker 34oz/1L
            Keywords: Coffee, French Press, Large, Matte Black, Free Plastic, Camping, Travel
            Categories: Matte Black, Borosilicate Glass, Camping, 3 Level Filter
            The description should be: 
            The Kaffe Large French Press Coffee Maker is the perfect coffee maker for home, office, travel, and camping. 
            It features a durable matte black finish with BPA-free plastic and borosilicate glass. 
            The 34oz / 1L capacity is perfect for sharing with friends and family. 
            The 3 level filter ensures that your coffee is smooth and delicious every time.
            """
        ),  # -----------------------------------------------------
    ]
    response = chat.invoke(messages)
    json_resp = json.loads(
        response.content
    )  # Parse output into a valid str to insert into df
    product_description = json_resp["description"]
    return product_description


def main():
    # ----------------------------------------------------------------------------------
    # Linking keywords to products
    # ----------------------------------------------------------------------------------

    load_dotenv("../.env")
    # getKeywords(), while not having this method we create a list of keywords
    keywords = """Disfraz Adulto, Carnaval, Disfraz Halloween, Disfraces chulos, Disfraces para fiestas"""
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
    products = getNproducts(df_cleaned, 1)
    # Link keywords and insert them into a new df
    index = 0
    for product in products:
        product_keywords = keyword_link(product, keywords)
        print(product_keywords)
        insertIn_df(df_duplicate, product_keywords, index, "Keywords")
        index = index + 1

    # ----------------------------------------------------------------------------------
    # Creating Titles
    # ----------------------------------------------------------------------------------
    products = getNproducts(df_duplicate, 1, brand=True)
    index = 0
    for product in products:
        product_title = title_create(product)
        print(product_title)
        insertIn_df(df_duplicate, product_title, index, "Title")
        index = index + 1

    # ----------------------------------------------------------------------------------
    # Creating Bullet Points and Descriptions
    # ----------------------------------------------------------------------------------

    products = getNproducts(df_duplicate, 1, title=True)
    index = 0
    for product in products:
        product_bullet_points = bullet_points_create(product)
        product_description = description_create(product)
        print(product_bullet_points)
        print(product_description)
        insertIn_df(df_duplicate, product_bullet_points, index, "Bullet_Points")
        insertIn_df(df_duplicate, product_description, index, "Description")
        index = index + 1


if __name__ == "__main__":
    main()
