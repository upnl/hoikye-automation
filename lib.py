import csv
import os
import sys
import re

# https://stackoverflow.com/a/14981125
def eprint(*args, **kwargs) -> None:
    print(*args, file=sys.stderr, **kwargs)

def parseprice(s) -> int:
    return int(s.replace(",", ""))

def formatprice(n) -> str:
    return f"{n:,}"

def parsedate(s):
    assert re.match(r"\d{4}.\d{2}.\d{2} \d{2}:\d{2}:\d{2}", s)
    return s[:10]

def do_or_exit(func, *args, task_label=None):
    try:
        return func(*args)
    except Exception as e:
        if task_label:
            eprint(f"Error while {task_label}: {e}")
        else:
            eprint(f"Error: {e}")
        sys.exit(1)

def _read_csv(filename, *, header_row, header, new_header, parsers) -> list[dict]:
    assert len(header) == len(new_header) and len(new_header) == len(parsers)
    assert all(type(h) == str for h in header)
    assert type(header_row) == int
    assert all(
            (type(h) == str and callable(p)) or h is None
            for h, p in zip(new_header, parsers)
            )

    eprint(f"Reading '{filename}'...")

    # check if input file exists
    if not os.path.exists(filename):
        eprint(f"Error: File '{filename}' not found")
        raise FileNotFoundError(f"File '{filename}' not found")

    # read input file
    with open(filename, "r") as file:
        reader = csv.reader(file)
        rows = list(reader)

    # simple check for header
    if rows[header_row] != header:
        eprint(f"Error: Invalid input file. Expected header at row {header_row+1}: {header}")
        raise ValueError(f'Invalid input file. Expected header at row {header_row+1}: {header}')

    # process data
    data = []
    for i, row in enumerate(rows[header_row+1:]):
        if len(row) != len(new_header):
            eprint(f"Warning: Invalid row: {i+header_row+1}. Skipping...")
            continue
        data.append({key: p(value) for key, value, p in zip(new_header, row, parsers) if key})

    return data

def read_account(filename) -> list[dict]:
    """
    Read account data from a CSV file.
    Returns a list of dictionaries of the form:
    [
        {'date': '2021.01.01', 'type': '입금', 'amount': 10000, 'balance': 10000, 'description': '홍길동', 'memo': ''},
        ...
    ]
    'type' field can be '입금' or '출금'
    """
    return _read_csv(
        filename,
        header_row = 10,
        header     = ['',   '거래일시', '구분', '거래금액', '거래 후 잔액', '거래구분', '내용',        '메모', ''  ],
        new_header = [None, 'date',     'type', 'amount',   'balance',      None,       'description', 'memo', None],
        parsers    = [None, parsedate,  str,    parseprice, parseprice,     None,       str,           str,    None],
        )

def read_members(filename) -> list[dict]:
    """
    Read members data from a CSV file.
    Returns a list of dictionaries of the form:
    [
        {'name': '홍길동', 'id': 'hong', 'phone': '010-1234-5678', 'email': 'hong@example.com', 'grade': '정회원'},
        ...
    ]
    'grade' field can be either '정회원', '준회원', 'OB', or '신입회원'
    """
    return _read_csv(
        filename,
        header_row = 0,
        header     = ['이름', '아이디', '전화번호', '이메일', '회원등급'],
        new_header = ['name', 'id', 'phone', 'email', 'grade'],
        parsers    = [str,    str,  str,       str,     str],
        )
