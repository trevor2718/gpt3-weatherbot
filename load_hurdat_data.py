import os
import requests
from lxml import html


pwd = os.getcwd()
download_dir = "hurdat_data"
hurdat_data_page = "https://www.nhc.noaa.gov/data"


if not os.path.exists(download_dir):
    os.mkdir(download_dir)


def download_latest_data():
    # return filepath of the newly downloaded file else returns false
    try:
        download_link = ""
        headers = {"Cache-Control": "no-cache"}

        r = requests.get(hurdat_data_page, headers=headers)
        raw_html = r.content
        
        tree = html.fromstring(raw_html)
        
        # xpath to download the data file
        xpath = "/html/body/div[5]/div/p[24]/a"
        download_tag = tree.xpath(xpath)
        
        if download_tag and download_tag is not None and len(download_tag):
            if "href" in download_tag[0].attrib:
                if download_tag[0].attrib["href"].strip().startswith("/data") \
                    and download_tag[0].attrib["href"].strip().endswith(".txt"):
                    download_link = hurdat_data_page + download_tag[0].attrib["href"].strip()[5:]
        
        if download_link:
            filepath = os.path.join(download_dir, download_link.split("/")[-1])
            data = requests.get(download_link)

            with open(filepath, "wb") as f:
                f.write(data.content)
            
            return filepath
        else:
            return False
    except Exception as e:
        print("Error occured while downloading the data => ", e)
        return False

