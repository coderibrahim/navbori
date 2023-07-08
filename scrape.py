import requests
from bs4 import BeautifulSoup
from bottle import Bottle, request
import json
from bson import ObjectId
from pymongo import MongoClient

class Functionalities:
    def scrape_website(self, barcode_number):
        global a_text, img_src, a_href
        search_url = 'https://marketkarsilastir.com/ara/' + barcode_number

        response = requests.get(search_url)
        soup = BeautifulSoup(response.content, 'html.parser')

        products_div = soup.find('div', class_='products')

        ul_element = products_div.find('ul')

        li_items = ul_element.find_all('li')

        scraped_products_data = []

        for li in li_items:
            img_src = li.find('img')['src']

            a_element = li.find('a', class_='pi-name mt-1')

            a_href = a_element['href']
            a_text = a_element.text.strip()

            response = requests.get("https://marketkarsilastir.com/" + a_href)
            inner_soup = BeautifulSoup(response.content, 'html.parser')

            table = inner_soup.find('table', class_='table text-center table-hover')
            tbody = table.find('tbody')
            tr_items = tbody.find_all('tr')

            for tr in tr_items:
                first_td = tr.find_all('td')[0]
                second_td = tr.find_all('td')[1]
                third_td = tr.find_all('td')[2]

                brand = first_td.find('img')['title']
                brand_image = first_td.find('img')['src']
                recently_changed_price_full = second_td.find('small').text.strip()
                recently_changed_price = recently_changed_price_full.replace('Son Fiyat Değişim Tarihi:', '').strip()
                price = third_td.text.strip()

                data = {
                    'brand': brand,
                    'brand_image': brand_image,
                    'barcode_number': barcode_number,
                    'name': a_text,
                    'recently_changed_price': recently_changed_price,
                    'price': price
                }
                scraped_products_data.append(data)

        # MongoDB Connection
        #client = MongoClient('mongodb+srv://ibrahim:plaka65jk21706556..@cluster0.sboemja.mongodb.net/test')
        #db = client['Navbori']
        #collection_product = db['products']
        #collection_products_with_price = db['products_with_details']
        #inserted_ids = []

        #for data in scraped_products_data:
            #    result = collection_products_with_price.insert_one(data)
        #    inserted_ids.append(str(result.inserted_id))

        #inserted_ids_str = ', '.join(inserted_ids)

        #product = {
            #    'barcode_number': barcode_number,
            #    'name': a_text,
            #    'image': img_src,
            #   'address': a_href,
        #   'prices': inserted_ids_str
        #}

        #collection_product.insert_one(product)
        return scraped_products_data


app = Bottle()
func = Functionalities()


@app.route('/scrape', method='POST')
def scrape_handler():
    barcode_number = request.forms.get('barcode_number')
    if barcode_number is None:
        return json.dumps({'error': 'Barcode number is missing'})

    results = func.scrape_website(barcode_number)
    results_serializable = json.dumps(results, default=str)

    return results_serializable

if __name__ == '__main__':
    app.run(debug=True)