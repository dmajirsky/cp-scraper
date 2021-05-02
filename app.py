import json
import requests
import datetime
from bs4 import BeautifulSoup
from flask import Flask
from flask import request


app = Flask(__name__)


@app.route('/connections', methods=["GET"])
def get_connections():
    url =" https://cp.hnonline.sk/"
    trans_type = request.args.get('type')
    start = request.args.get('start')
    dest = request.args.get('dest')
    time = request.args.get('time')

    trans_type = encrypt_for_url(trans_type)
    start = encrypt_for_url(start)
    dest = encrypt_for_url(dest)

    if trans_type.__contains__("mhd") or trans_type.__contains__("kosice"):
        url = url + "kosice"
    else:
        url = url + trans_type

    url = url + "/spojenie/vysledky/"
    url = url + "?f=" + start
    url = url + "&t=" + dest
    date_time = time.split("_")

    data = do_page_request(url, date_time)

    json_object = json.dumps(data, indent=4, ensure_ascii=False)
    print(json_object)
    return json_object


def encrypt_for_url(value):
    str_list = list(value)
    switcher = {
        " ": "%20",
        "á": "%C3%A1",
        "ä": "%C3%A4",
        "č": "%C4%8D",
        "ď": "%C4%8F",
        "é": "%C3%A9",
        "ě": "%C4%9B",
        "í": "%C3%AD",
        "ĺ": "%C4%BA",
        "ľ": "%C4%BE",
        "ň": "%C5%88",
        "ó": "%C3%B3",
        "ô": "%C3%B4",
        "ŕ": "%C5%95",
        "ř": "%C5%99",
        "š": "%C5%A1",
        "ť": "%C5%A5",
        "ú": "%C3%BA",
        "ů": "%C5%AF",
        "ý": "%C3%BD",
        "ž": "%C5%BE",
        "Á": "%C3%81",
        "Ä": "%C3%84",
        "Č": "%C4%8C",
        "Ď": "%C4%8E",
        "É": "%C3%89",
        "Ě": "%C4%9A",
        "Í": "%C3%8D",
        "Ĺ": "%C4%B9",
        "Ľ": "%C4%BD",
        "Ň": "%C5%87",
        "Ó": "%C3%93",
        "Ô": "%C3%94",
        "Ŕ": "%C5%94",
        "Ř": "%C5%98",
        "Š": "%C5%A0",
        "Ť": "%C5%A4",
        "Ú": "%C3%9A",
        "Ů": "%C5%AE",
        "Ý": "%C3%9D",
        "Ž": "%C5%BD"
    }
    idx = 0
    for i in str_list:
        str_list[idx] = switcher.get(i, i)
        idx += 1
    return "".join(str_list)


def do_page_request(url, date_time):
    url_with_time = url + "&date=" + date_time[0]
    url_with_time = url_with_time + "&time=" + date_time[1]

    page = requests.get(url_with_time)

    soup = BeautifulSoup(page.content, 'html.parser')

    results = soup.find(id='content')

    connection_details = results.find_all('div', class_='connection-details')

    data = {"data": []}

    connection = {"connection": []}
    for detail in connection_details:

        outsideOfPopup = detail.find_all('div', class_='outside-of-popup')

        for outside in outsideOfPopup:
            try:
                link = {}
                number = outside.find('div', class_='title-container').find('span')
                firstTime = outside.find('li', class_='item active').find('p', class_='reset time')
                firstStation = outside.find('li', class_='item active').find('p', class_='station')
                lastTime = outside.find('li', class_='item active last').find('p', class_='reset time')
                lastStation = outside.find('li', class_='item active last').find('p', class_='station')

                link["number"] = number.text
                link["first-time"] = str(firstTime.text)
                link["first-station"] = str(firstStation.text)
                link["last-time"] = str(lastTime.text)
                link["last-station"] = str(lastStation.text)
                connection["connection"].append(link)
            except:
                date_obj = datetime.datetime.strptime(date_time[0], "%d.%m.%Y") + datetime.timedelta(days=1)
                date_time[0] = date_obj.strftime("%d.%m.%Y")
                date_time[1] = "00:00"
                return do_page_request(url, date_time)

    data["data"].append(connection)
    return data


if __name__ == '__main__':
    app.run()
