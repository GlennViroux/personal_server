'''
from file_utils import get_temp_file
from music_classification import MusicClassification,MusicConfig
config_file = "./machine_learning/model_results/results_36/model_config.txt"
config = MusicConfig.read_config(config_file)
mclas = MusicClassification(config)
mclas.load_saved_model(36)
wav_file = "./ffmpeg_temp_files/wav/sample_1.wav"
result = mclas.predict(wav_file,verbose=True)
print(result)
'''


