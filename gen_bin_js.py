import requests
import io
import shutil
import zipfile

API_URL = "https://api.github.com/repos/CTCaer/hekate/releases/latest"
BIN_NAME = "hekate_ctcaer_"
SERIALIZED_FILENAME = "hekate.bin.js"

### BASIC FILE STUFF, DO NOT EDIT
DEFAULT_SERIALIZED_CONTENTS = """
const hekate = new Uint8Array([
    {}
]);
"""

## Script that downloads the latest bin from hekate and serializes it as a .bin.js file.

def download_file_to_bytes_io(url) -> io.BytesIO:
    r = requests.get(url)
    filedata = io.BytesIO()
    if r.status_code == 200:
        filedata.write(r.content)
    filedata.seek(0)
    return filedata

def extract_specific_file_from_zip(zip_file) -> io.BytesIO:
    filename = None
    filedata = io.BytesIO()
    with zipfile.ZipFile(zip_file) as z:
        for zinfo in z.infolist():
            if zinfo.filename.startswith(BIN_NAME):
                filename = zinfo.filename
                break
        if filename is None:
            raise Exception("Zipfile does not contain required match.")

        with z.open(filename) as zfile:
            shutil.copyfileobj(zfile, filedata)
    filedata.seek(0)
    return filedata

def fetch_hekate_zip() -> io.BytesIO:
    r = requests.get(API_URL)
    jdata = r.json()
    return download_file_to_bytes_io([d for d in jdata["assets"] if d["name"].startswith("hekate_ctcaer")][0]["browser_download_url"])

def get_hekate_payload(hekate_zip: io.BytesIO) -> io.BytesIO:
    return extract_specific_file_from_zip(hekate_zip)

def serialize_to_js(hekate_payload: io.BytesIO, filename: str):
    hekate_payload = hekate_payload.read()

    # List so we can loop byte for byte
    serialized = [bytes([b]) for b in hekate_payload]
    final_str = []

    # Formatting
    max_ctr = 16
    str_on_line = 0

    # Special check to ensure that a comma isn't placed on the end
    last_byte = len(serialized) - 1
    for idx, byte in enumerate(serialized):
        if idx != last_byte:
            final_str.append(f"0x{byte.hex()}, ")
        else:
            final_str.append(f"0x{byte.hex()}")

        # More readable
        str_on_line += 1
        if str_on_line >= max_ctr:
            str_on_line = 0
            final_str.append("\n    ")

    final_str = "".join(final_str)

    out_string = DEFAULT_SERIALIZED_CONTENTS.format(final_str)
    with open(filename, "w") as outfile:
        outfile.write(out_string)

if __name__ == "__main__":
    api_response = fetch_hekate_zip()
    payload = get_hekate_payload(api_response)
    serialize_to_js(payload, SERIALIZED_FILENAME)