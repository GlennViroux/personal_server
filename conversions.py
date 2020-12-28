'''
Useful conversions
'''
import requests
import re

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

def norad2prn(norad_id,group):
    if group=="galileo" or group=="gps-ops":
        return norad_id.split('PRN')[1].replace(')','').replace('\n','').strip()
    elif group=="beidou":
        if '(' in norad_id and ')' in norad_id:
            return norad_id.split('(')[1].replace(')','').replace('\n','').strip()
        else:
            if norad_id.strip() in BEIDOU_EXTRA:
                return BEIDOU_EXTRA[norad_id.strip()]
            else:
                return ''

def cosmos2prn(input_number):
    n = "[0-9]"
    date = n*2+"."+n*2+"."+n*4
    pattern = f"^\\|  {n}{n}{n}  \\| {n}{n}{n}{n} \\| {n}/{n}{n} \\|  .{n}  \\| {date} \\| {date} \\| .* \\| .* \\|.*"

    result = {}
    req = requests.get("https://www.glonass-iac.ru/en/CUSGLONASS/getCUSMessage.php")
    lines = req.text.split('\n')
    for line in lines:
        if re.match(pattern,line):
            elems = line.split('|')
            cosmos_number = elems[2].strip()
            slot = elems[3].split('/')[1].strip()
            result[cosmos_number] = slot

    if not str(input_number) in result:
        print("GLENNY cosmos number not found!")
        return False

    return result[str(input_number)]
    
