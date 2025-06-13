from flask import Flask, render_template, request
import requests
from googletrans import Translator

app = Flask(__name__)
translator = Translator()

@app.route('/', methods=['GET', 'POST'])
def home():
    product_data = None
    error_message = None

    if request.method == 'POST':
        user_input = request.form['product_input'].strip().lower()

        if user_input.isdigit() and len(user_input) >= 8:
            url = f"https://world.openfoodfacts.org/api/v0/product/{user_input}.json"   #barcode search api
            response = requests.get(url, headers={'Accept-Language': 'en'})

            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 1:
                    product = data.get('product')
                    raw_ingredients = (
                        product.get('ingredients_text_en') or 
                        product.get('ingredients_text') or 
                        ""
                    )
                    if raw_ingredients:
                        try:
                            detected = translator.detect(raw_ingredients)
                            translated_ingredients = translator.translate(raw_ingredients, src=detected.lang, dest='en').text   #translating to english
                        except:
                            translated_ingredients = raw_ingredients
                    else:
                        translated_ingredients = "N/A"

                    product_data = {
                        'name': product.get('product_name_en') or product.get('product_name', 'N/A'),
                        'brand': product.get('brands', 'N/A'),
                        'ingredients': translated_ingredients,
                        'nutri_score': product.get('nutrition_grades', 'N/A'),
                        'allergens': ', '.join([tag.split(':')[-1].capitalize() for tag in product.get('allergens_tags', [])]) or "None",
                        'image': product.get('image_front_small_url', '')
                    }
                else:
                    error_message = "Product not found. Try another barcode or name."
            else:
                error_message = "Failed to reach API."

        else:
            search_url = f"https://world.openfoodfacts.org/cgi/search.pl?search_terms={user_input}&search_simple=1&action=process&json=1"   #product name search api
            search_response = requests.get(search_url, headers={'Accept-Language': 'en'})

            if search_response.status_code == 200:
                search_data = search_response.json()
                products = search_data.get('products', [])

                if products:
                    product = products[0]
                    raw_ingredients = (
                        product.get('ingredients_text_en') or 
                        product.get('ingredients_text') or 
                        ""
                    )
                    if raw_ingredients:
                        try:
                            detected = translator.detect(raw_ingredients)
                            translated_ingredients = translator.translate(raw_ingredients, src=detected.lang, dest='en').text
                        except:
                            translated_ingredients = raw_ingredients
                    else:
                        translated_ingredients = "N/A"

                    product_data = {
                        'name': product.get('product_name_en') or product.get('product_name', 'N/A'),
                        'brand': product.get('brands', 'N/A'),
                        'ingredients': translated_ingredients,
                        'nutri_score': product.get('nutrition_grades', 'N/A'),
                        'allergens': ', '.join([tag.split(':')[-1].capitalize() for tag in product.get('allergens_tags', [])]) or "None",
                        'image': product.get('image_front_small_url', '')
                    }
                else:
                    error_message = "No matching product found for the given name."
            else:
                error_message = "Failed to reach search API."

    return render_template("index.html", product=product_data, error=error_message)

if __name__ == '__main__':
    app.run(debug=True)