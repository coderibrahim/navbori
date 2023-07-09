import json
import time
import requests
from bottle import Bottle, request
from bs4 import BeautifulSoup



class Functionalities:
    def scrape_website(self, barcode_number):
        global soup
        search_url = 'https://marketkarsilastir.com/ara/' + barcode_number

        url = "https://scrapers-proxy2.p.rapidapi.com/standard"

        querystring = {"url": search_url}

        headers = {
            "X-RapidAPI-Key": "1fe3b92a9bmsh2bde008e1a81054p1f19a4jsnd2a80d1560f3",
            "X-RapidAPI-Host": "scrapers-proxy2.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers, params=querystring, timeout=30)

        soup = BeautifulSoup(response.content, 'html.parser')
        print("soup data:")
        print(soup.prettify())    

        products_div = soup.find('div', class_='products')
        if products_div is None:
            return {'error': 'Products not found'}

        ul_element = products_div.find('ul')
        if ul_element is None:
            return {'error': 'List not found'}

        li_items = ul_element.find_all('li')

        scraped_products_data = []

        for li in li_items:
            img_src = li.find('img')['src']

            a_element = li.find('a', class_='pi-name mt-1')

            a_href = a_element['href']
            a_text = a_element.text.strip()

            response = requests.get("https://marketkarsilastir.com/" + a_href, timeout=63)
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

        return scraped_products_data


app = Bottle()
func = Functionalities()


@app.route('/scrape', method='POST')
def scrape_handler():
    barcode_number = request.forms.get('barcode_number')
    if barcode_number is None:
        return json.dumps({'error': 'Barcode number is missing'})

    results = func.scrape_website(barcode_number)

    if 'error' in results:
        return json.dumps({'error': results['error']})

    results_serializable = json.dumps(results, default=str)
    return results_serializable


if __name__ == '__main__':
    app.run(debug=True)
