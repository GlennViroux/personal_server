
import re
import requests
from datetime import date,datetime

from data_download import Celestrak,IGS
from geometry import Geometry
from snippets import df2geojsonLineString,df2geojsonSatPoints,df2geojsonStationPoints,send_mail

mail_from = "portfolioglennviroux@gmail.com"
mail_for = "glenn.viroux@gmail.com"
subject = "MySubject"
text = "Hello darkness my old friend"

send_mail(mail_for,mail_from,subject,text)


