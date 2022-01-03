import os
import random
import requests
from dataclasses import dataclass
from io import BytesIO
from typing import List
from zipfile import ZipFile

import pandas as pd
from urllib.request import Request, urlopen


ROOT_PATH = "./files"
FORM_PATH = os.path.join(ROOT_PATH, "forms")
COLUMNS = ["CIK", "Company Name", "Form Type", "Date Filed", "Filename"]
SAMPLE_SIZE = 10

EDGAR_INDEX_URL = "https://www.sec.gov/Archives/edgar/full-index/{year}/QTR{quarter}/"
EDGAR_DATA_URL = "https://www.sec.gov/Archives/{filename}"
HEADERS = {
    "Accept-Encoding": "gzip",
    "User-Agent": "Georgia Tech FinTech Lab rohname@gmail.com",
}


@dataclass(frozen=True)
class Filing:
    cik: int
    date: str


@dataclass(frozen=True)
class FormEntry:
    cik: int
    date: str
    filename: str


@dataclass(frozen=True)
class IndexUrl:
    year: int
    quarter: int
    url: str


def generate_urls() -> List[IndexUrl]:
    return [
        IndexUrl(
            year=year,
            quarter=quarter,
            url=EDGAR_INDEX_URL.format(year=year, quarter=quarter),
        )
        for year in range(1995, 2022)
        for quarter in range(1, 5)
    ]


def get_contents(url: str) -> List[str]:
    req = Request(f"{url}/master.zip")
    for header, val in HEADERS.items():
        req.add_header(header, val)

    bytes = urlopen(req).read()
    file = ZipFile(BytesIO(bytes))
    return [
        line.decode("utf-8").replace("\r", "").replace("\n", "")
        for line in file.open("master.idx").readlines()
    ]


def filter_8k(contents: List[str]) -> List[FormEntry]:
    start = contents.index("|".join(COLUMNS)) + 2
    entries = [row.split("|") for row in contents[start:]]
    return [
        FormEntry(cik=entry[0], date=entry[3], filename=entry[4])
        for entry in entries
        if entry[2] == "8-K"
    ]


def parse_contents(filings: List[Filing], contents: List[str], year: int, quarter: int):
    candidates = filter_8k(contents)
    chosen = random.sample(candidates, SAMPLE_SIZE)
    print(f"Downloading {len(chosen)} files for year: {year}, quarter: {quarter}")
    for entry in chosen:
        filings.append(Filing(cik=entry.cik, date=entry.date))
        download(entry)


def download(entry: FormEntry):
    resp = requests.get(
        EDGAR_DATA_URL.format(filename=entry.filename),
        headers=HEADERS,
    )
    if resp.status_code != 200:
        print(f"Failed to get data file {entry.filename}")
        return

    try:
        download_name = f"{entry.date}-{entry.cik}.txt"
        with open(os.path.join(FORM_PATH, download_name), "w") as f:
            f.write(strip_html(resp.text))
    except Exception as e:
        print(f"Failed to download file {entry.filename}\nError: {str(e)}")


def strip_html(text: str) -> str:
    lines = []
    for l in text.splitlines():
        if "<" in l and ">" in l:
            continue
        lines.append(l)
    return "\n".join(lines) + "\n"


def main():
    if not os.path.exists(ROOT_PATH):
        os.makedirs(ROOT_PATH)
    if not os.path.exists(FORM_PATH):
        os.makedirs(FORM_PATH)

    filings = []
    for index_url in generate_urls():
        contents = get_contents(index_url.url)
        parse_contents(
            filings=filings,
            contents=contents,
            year=index_url.year,
            quarter=index_url.quarter,
        )

    filings_rows = [{"CIK": f.cik, "date": f.date} for f in filings]
    filings_df = pd.DataFrame(filings_rows)
    filings_df.to_csv(os.path.join(ROOT_PATH, "filings.csv"))


main()
