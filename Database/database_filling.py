from Database.settings import user, password, host, db_name, yandex_api_key
from pprint import pprint
import requests


def calculate_spn(radius_meters):
    meters_per_degree_lat = 111320.0
    lat_span = radius_meters / meters_per_degree_lat
    lon_span = lat_span
    return lat_span, lon_span


def map_search_yandex(lat, lng, query, radius, skip=0, types=0):
    """
    :param lat:
    :param lng:
    :param query:
    :param radius:
    :param types: 0 - ищем только банки, 1 ищем все
    :return:
    """
    spn = calculate_spn(radius)
    url = f"https://search-maps.yandex.ru/v1/"

    params = {
        "apikey": yandex_api_key,
        "text": query,
        "lang": "ru_RU",
        "ll": f"{lng},{lat}",
        "spn": f"{spn[0]},{spn[1]}",
        "rspn": "1",
        "results": "50",
        "skip": f"{skip}"
    }

    headers = {
        "Accept": "application/json",
    }

    response = requests.request("GET", url, params=params)
    data = response.json()
    return data


if __name__ == '__main__':
    lat = 55.7522200
    lng = 37.6155600
    for i in range(100):
        data = map_search_yandex(lat, lng, "ВТБ", 400000, skip=i * 50)
        data = data.get('features')
        for bank in data:
            #if bank['properties']['CompanyMetaData']['Categories'][0]['class'] == 'banks':
            print('*' * 40)
            coordinates = bank.get('geometry').get('coordinates')
            company_metadata = bank.get('properties').get('CompanyMetaData')
            category = company_metadata.get('Categories')[-1].get('class')
            hours = company_metadata.get('Hours')
            phones = company_metadata.get('Phones')
            address = company_metadata.get('address')
            name = company_metadata.get('name')
            pprint(coordinates)
            print(category)
            #pprint(company_metadata['Categories'][0]['class'])
            #pprint(bank['properties']['CompanyMetaData']['Hours']['Availabilities'])
            pprint(hours)
            #pprint(bank['properties']['CompanyMetaData']['Phones'])
            pprint(phones)
            pprint(address)
            pprint(name)
            #pprint(bank)
            print('*' * 40)
        if len(data) != 50:
            break


