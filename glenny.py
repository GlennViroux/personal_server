from music_classification import MusicClassification,MusicConfig

config = MusicConfig()
config.train_test_ratio = 0.80
config.number_of_epochs = 200
config.learning_rate = 0.00005
config.batch_size = 32
config.sample_length = 4
config.num_data_series_per_sample = 6
config.n_mels = 64
config.augment_data = False
config.noise_factor = 0.001
config.pitch_factor = 0.80
config.speed_factor = 0.80


mclas = MusicClassification(config)
mclas.load_data()
mclas.init_model()
mclas.train_model()
mclas.save_results_training()







