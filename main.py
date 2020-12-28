
from data_download import Celestrak

celestrak = Celestrak("./config/download_config.ini")

#celestrak.download_all()

date = "2020/12/25"
group = "glo-ops"
print(celestrak.get_csv(date,group).dtypes)