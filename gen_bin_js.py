import requests
import io

API_URL = "https://api.github.com/repos/CTCaer/hekate/releases/latest"
SERIALIZED_FILENAME = "hekate.bin.js"

## Script that downloads the latest bin from hekate and serializes it as a .bin.js file.

def download_file_to_bytes_io(url) -> io.BytesIO:
    r = requests.get(url)
    filedata = io.BytesIO()
    if r.status_code == 200:
        filedata.write(r.content)
    filedata.seek(0)
    return filedata

def extract_specific_file_from_zip():
    pass

def fetch_hekate_zip() -> io.BytesIO:
    r = requests.get(API_URL)
    jdata = r.json()
    return download_file_to_bytes_io([d for d in hekate_json["assets"] if d["name"].startswith("hekate_ctcaer")][0]["browser_download_url"])

def get_hekate_payload(hekate_zip: io.BytesIO) -> io.BytesIO:
    pass

def serialize_to_js(hekate_payload: io.BytesIO, filename: str):
    pass

if __name__ == "__main__":
    api_response = fetch_hekate_zip()
    payload = get_hekate_payload(api_response)
    serialize_to_js(payload, SERIALIZED_FILENAME)