import requests
import io
import shutil
import zipfile

bin_files = {
    "hekate": {
        "API_URL": "https://api.github.com/repos/CTCaer/hekate/releases/latest", # API version url
        "BIN_NAME": "hekate_ctcaer", # BIN_NAME -> used to determine what file to extract from zip or what to download from API
        "SERIALIZED_FILENAME": "hekate.bin.js", # File to store serialized contents in.
        "SHORT_NAME": "hekate",
        "zipped": True # Do we need to extract a zip or is it just a raw payload.
    },
    "tegraexplorer": {
        "API_URL": "https://api.github.com/repos/suchmememanyskill/TegraExplorer/releases/latest",
        "BIN_NAME": "TegraExplorer",
        "SERIALIZED_FILENAME": "tegraexplorer.bin.js",
        "SHORT_NAME": "tegraexplorer",
        "zipped": False,
    },
    "lockpick": {
        "API_URL": "https://api.github.com/repos/shchmue/Lockpick_RCM/releases/latest",
        "BIN_NAME": "Lockpick_RCM",
        "SERIALIZED_FILENAME": "lockpick.bin.js",
        "SHORT_NAME": "lockpick",
        "zipped": False,
    },
}

### BASIC FILE STUFF, DO NOT EDIT
DEFAULT_SERIALIZED_CONTENTS = """
const {} = new Uint8Array([
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

def extract_specific_file_from_zip(zip_file, bin_name) -> io.BytesIO:
    filename = None
    filedata = io.BytesIO()
    with zipfile.ZipFile(zip_file) as z:
        for zinfo in z.infolist():
            if zinfo.filename.startswith(bin_name):
                filename = zinfo.filename
                break
        if filename is None:
            raise Exception("Zipfile does not contain required match.")

        with z.open(filename) as zfile:
            shutil.copyfileobj(zfile, filedata)
    filedata.seek(0)
    return filedata

def fetch_hekate_zip(api_url) -> io.BytesIO:
    r = requests.get(api_url)
    jdata = r.json()
    return download_file_to_bytes_io([d for d in jdata["assets"] if d["name"].startswith("hekate_ctcaer")][0]["browser_download_url"])

def fetch_github_repo_file(api_url, filename) -> io.BytesIO:
    r = requests.get(api_url)
    jdata = r.json()
    return download_file_to_bytes_io([d for d in jdata["assets"] if d["name"].startswith(filename)][0]["browser_download_url"])

def fetch_github_latest_tag(api_url) -> io.BytesIO:
    r = requests.get(api_url)
    jdata = r.json()
    return jdata["tag_name"]

def serialize_to_js(short_name: str, payload: io.BytesIO, filename: str):
    payload = payload.read()

    # List so we can loop byte for byte
    serialized = [bytes([b]) for b in payload]
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

    out_string = DEFAULT_SERIALIZED_CONTENTS.format(short_name, final_str)
    with open(filename, "w") as outfile:
        outfile.write(out_string)

def generate_js(program: str):
    api_response = fetch_github_repo_file(bin_files[program]["API_URL"], bin_files[program]["BIN_NAME"])
    if bin_files[program]["zipped"]:
        payload = extract_specific_file_from_zip(api_response, bin_files[program]["BIN_NAME"])
    else:
        payload = api_response
    serialize_to_js(bin_files[program]["SHORT_NAME"], payload, bin_files[program]["SERIALIZED_FILENAME"])

def generate_html():
    with open("html/preface.html", "r") as preface_file:
        preface = preface_file.read()

    with open("html/core.html", 'r') as template_file:
        core = template_file.read()

    with open("html/post.html", "r") as post_file:
        post = post_file.read()

    html_data_list = []
    html_data_list.append(preface)
    html_data_list.append(core.format(
        fetch_github_latest_tag(bin_files["hekate"]["API_URL"]),
        fetch_github_latest_tag(bin_files["tegraexplorer"]["API_URL"]),
        fetch_github_latest_tag(bin_files["lockpick"]["API_URL"]),
    ))
    html_data_list.append(post)


    out_string = "".join(html_data_list)
    with open("index.html", "w") as indexfile:
        indexfile.write(out_string)

def main():
    generate_js("hekate")
    generate_js("tegraexplorer")
    generate_js("lockpick")
    generate_html()

if __name__ == "__main__":
    main()
