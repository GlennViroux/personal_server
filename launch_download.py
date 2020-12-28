
from data_download import Celestrak

if __name__=='__main__':
    celestrak = Celestrak("./config/download_config.ini")
    celestrak.download_all()