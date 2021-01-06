'''
Useful conversions
'''
import requests
import re
from pathlib import Path
from datetime import datetime,timedelta

class GlonassInfo:
    @classmethod
    def download_cus_message(cls):
        yesterday = datetime.now() - timedelta(days=1)
        yesterday_date = yesterday.date()
        year = yesterday_date.year
        month = str(yesterday_date.month).zfill(2)
        day = str(yesterday_date.day).zfill(2)
        basepath = Path(f"./output/{year}/{month}/{day}/glonass_cus")
        basepath.mkdir(parents=True,exist_ok=True)
        filepath = basepath / f"CUSMessage_{year}{month}{day}.txt"
        req = requests.get("https://www.glonass-iac.ru/en/CUSGLONASS/getCUSMessage.php")
        with filepath.open("wb") as f:
            f.write(req.content)

    @classmethod
    def get_cus_msg(cls):
        yesterday = datetime.now() - timedelta(days=1)
        yesterday_date = yesterday.date()
        year = yesterday_date.year
        month = str(yesterday_date.month).zfill(2)
        day = str(yesterday_date.day).zfill(2)
        filepath = Path(f"./output/{year}/{month}/{day}/glonass_cus/CUSMessage_{year}{month}{day}.txt")
        result = []
        if filepath.exists():
            with filepath.open("r") as f:
                result = f.readlines()
        return result

BEIDOU_EXTRA = {
    "BEIDOU-2 G8":"C01",
    "BEIDOU-3 IGSO-3":"C40",
    "BEIDOU-3 M21":"C43",
    "BEIDOU-3 M22":"C44",
    "BEIDOU-3 M19":"C41",
    "BEIDOU-3 M20":"C42",
    "BEIDOU-3 G2":"C60",
    "BEIDOU-3 G3":"C61"}

#TODO create decent Constellations class to check constellation statuses, 
#for example from http://www.csno-tarc.cn/en/system/constellation and 
#conversions from NORAD IDs to PRNs

def norad2prn(norad_id):
    '''
    Convert the provided Norad ID to PRN
    '''
    if "GPS" in norad_id:
        return "G"+norad_id.split('PRN')[1].strip().replace(')','')
    elif "GSAT" in norad_id and "PRN E" in norad_id:
        return norad_id.split('PRN')[1].strip().replace(')','')
    elif "COSMOS" in norad_id:
        prn = cosmos2prn(int(norad_id.split(" ")[1]))
        if prn:
            return "R"+prn
        else:
            return ""
    elif "BEIDOU" in norad_id:
        if '(' in norad_id and ')' in norad_id:
            return norad_id.split('(')[1].replace(')','').replace('\n','').strip()
        else:
            if norad_id.strip() in BEIDOU_EXTRA:
                return BEIDOU_EXTRA[norad_id.strip()]
            else:
                return 'N/A'

def cosmos2prn(input_number):
    n = "[0-9]"
    date = n*2+"."+n*2+"."+n*4
    pattern = f"^\\|  {n}{n}{n}  \\| {n}{n}{n}{n} \\| {n}/{n}{n} \\|  .{n}  \\| {date} \\| {date} \\| .* \\| .* \\|.*"

    result = {}
    glo_msg_lines = GlonassInfo.get_cus_msg()
    if not glo_msg_lines:
        print(f"GLENNY glonass cus message not found!")
        return False
    
    for line in glo_msg_lines:
        if re.match(pattern,line):
            elems = line.split('|')
            cosmos_number = elems[2].strip()
            slot = elems[3].split('/')[1].strip()
            result[cosmos_number] = slot

    if not str(input_number) in result:
        print(f"GLENNY cosmos number {input_number} not found!")
        return False

    return result[str(input_number)]
    
