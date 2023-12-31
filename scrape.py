import json
import time
import requests
from bottle import Bottle, request
from bs4 import BeautifulSoup


class Functionalities:
    def scrape_website(self, barcode_number):
        search_url = 'https://marketkarsilastir.com/ara/' + barcode_number

        url = "https://scrapers-proxy2.p.rapidapi.com/standard"

        querystring = {"url": search_url}

        ## finisked Key Mails
        ## 41 21 quzycary ss00 beyany
        
        finishedkey = "1fe3b92a9bmsh2bde008e1a81054p1f19a4jsnd2a80d1560f3"
        finishedSecondKey = "92466fb05amsh87d78f5ee9b9f4fp100b06jsn84d686748ab9"
        thirtyKey = "de39c34fd4msh978e36c6dfc34b8p1bfbebjsnda3a060330ac"
        
        headers = {
            "X-RapidAPI-Key": "d4e9ae81b6msh1c14feddac349e4p153b96jsn7a9eeb28285c",
            "X-RapidAPI-Host": "scrapers-proxy2.p.rapidapi.com"
        }


        response = requests.get(url, headers=headers, params=querystring, timeout=50)
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

            second_url = "https://marketkarsilastir.com/" + a_href
            second_querystring = {"url": second_url}
            second_headers = {
                "X-RapidAPI-Key": "4366eff652msh87c2b68d7adc904p10beb0jsn8111010aa1b2",
                "X-RapidAPI-Host": "scrapers-proxy2.p.rapidapi.com"
            }

            response_second = requests.get(url, headers=second_headers, params=second_querystring, timeout=30)

            if response_second.status_code != 200:
                print("Hata: Ürün isteği başarısız oldu:", a_href)
                continue

            inner_soup = BeautifulSoup(response_second.content, 'html.parser')

            table = inner_soup.find('table', class_='table text-center table-hover')
            if table is None:
                print("Hata: Tablo bulunamadı:", a_href)
                continue

            tbody = table.find('tbody')
            if tbody is None:
                print("Hata: Tbody bulunamadı:", a_href)
                continue

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
                    'product_image':img_src,
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


@app.route('/scrape', method='GET')
def scrape_handler():
    barcode_number = request.query.get('number')
    if barcode_number is None:
        return json.dumps({'error': 'Barcode number is missing'})

    results = func.scrape_website(barcode_number)

    if 'error' in results:
        return json.dumps({'error': results['error']})

    results_serializable = json.dumps(results, default=str)
    
    return results_serializable



if __name__ == '__main__':
    app.run(debug=True)
