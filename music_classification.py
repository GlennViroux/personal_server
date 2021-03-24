import os
import logging
import librosa
import librosa.display
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from contextlib import redirect_stdout
from keras.utils import to_categorical
from keras.optimizers import Adam
from tensorflow.python.keras import models,regularizers
from tensorflow.python.keras.layers import Dense,Conv2D,MaxPooling2D,Dropout,Flatten,BatchNormalization

from pathlib import Path

logging.basicConfig(level=logging.INFO,format='[%(asctime)s] - [%(levelname)s] - %(message)s', datefmt='%Y/%m/%d-%H:%M:%S')


class MusicConfig:
    def __init__(self,
                 number_of_epochs=None,
                 train_test_ratio=None,
                 learning_rate=None,
                 batch_size=None,
                 sample_length=None,
                 num_data_series_per_sample=None,
                 n_mels=None,
                 augment_data=None,
                 noise_factor=None,
                 pitch_factor=None,
                 speed_factor=None):
        self.number_of_epochs = number_of_epochs if number_of_epochs else 200
        self.train_test_ratio = train_test_ratio if train_test_ratio else 0.80
        self.learning_rate = learning_rate if learning_rate else 0.0001
        self.batch_size = batch_size if batch_size else 32
        self.sample_length = sample_length if sample_length else 4
        self.num_data_series_per_sample = num_data_series_per_sample if num_data_series_per_sample else 6
        self.n_mels = n_mels if n_mels else 64
        self.augment_data = augment_data if (not augment_data==None) else False
        self.noise_factor = noise_factor if noise_factor else 0.001
        self.pitch_factor = pitch_factor if pitch_factor else 0.80
        self.speed_factor = speed_factor if speed_factor else 0.80

    def __repr__(self):
        lines = []
        lines.append(f"-- CNN Configuration --")
        lines.append("{0:<40}: {1:<20}".format("Number of epochs",self.number_of_epochs))
        lines.append("{0:<40}: {1:<20}".format("Train test ratio",self.train_test_ratio))
        lines.append("{0:<40}: {1:<20}".format("Learning rate",self.learning_rate))
        lines.append("{0:<40}: {1:<20}".format("Batch size",self.batch_size))
        lines.append("{0:<40}: {1:<20}".format("Sample length",self.sample_length))
        lines.append("{0:<40}: {1:<20}".format("Number of data series per sample",self.num_data_series_per_sample))
        lines.append("{0:<40}: {1:<20}".format("Number of mels",self.n_mels))
        lines.append("{0:<40}: {1:<20}".format("Augment data",self.augment_data))
        lines.append("{0:<40}: {1:<20}".format("Noise factor",self.noise_factor))
        lines.append("{0:<40}: {1:<20}".format("Pitch factor",self.pitch_factor))
        lines.append("{0:<40}: {1:<20}".format("Speed factor",self.speed_factor))

        return "\n".join(lines)

    @classmethod
    def read_config(cls,config_file):
        config_file = Path(config_file)
        if not config_file.exists():
            logging.error(f"Provided configuration file {config_file} does not exist.")
        
        lines = []
        with config_file.open("r") as f:
            lines = f.readlines()

        number_of_epochs = None
        train_test_ratio = None
        learning_rate = None
        batch_size=None
        sample_length = None
        num_data_series_per_sample = None
        n_mels = None
        augment_data = None
        noise_factor = None
        pitch_factor = None
        speed_factor = None

        for line in lines:
            elems = [elem.strip() for elem in line.split(":")]
            if not len(elems)==2:
                continue

            if elems[0]=="Number of epochs":
                number_of_epochs = int(elems[1])
            elif elems[0]=="Train test ratio":
                train_test_ratio = float(elems[1])
            elif elems[0]=="Learning rate":
                learning_rate = float(elems[1])
            elif elems[0]=="Batch size":
                batch_size = int(elems[1])
            elif elems[0]=="Sample length":
                sample_length = int(elems[1])
            elif elems[0]=="Number of data series per sample":
                num_data_series_per_sample = int(elems[1])
            elif elems[0]=="Number of mels":
                n_mels = int(elems[1])
            elif elems[0]=="Augment data":
                augment_data = elems[1]=="1"
            elif elems[0]=="Noise factor":
                noise_factor = float(elems[1])
            elif elems[0]=="Pitch factor":
                pitch_factor = float(elems[1])
            elif elems[0]=="Speed factor":
                speed_factor = float(elems[1])

        result = MusicConfig(
            number_of_epochs=number_of_epochs,
            train_test_ratio=train_test_ratio,
            learning_rate=learning_rate,
            batch_size=batch_size,
            sample_length=sample_length,
            num_data_series_per_sample=num_data_series_per_sample,
            n_mels=n_mels,
            augment_data=augment_data,
            noise_factor=noise_factor,
            pitch_factor=pitch_factor,
            speed_factor=speed_factor
        )

        return result

class MusicClassification:
    def __init__(self,config=None):
        self.data_dir = Path("./drive/MyDrive/Machine_Learning/GZTAN")
        self.plot_dir = Path("./drive/MyDrive/Machine_Learning/plots")
        self.plot_dir.mkdir(parents=True,exist_ok=True)
        self.model_results_dir = Path("./machine_learning/ml_model_results")
        self.model_results_dir.mkdir(parents=True,exist_ok=True)
        self.model = None
        self.trained = False
        self.genre_encoding = {
            'blues':0,
            'classical':1,
            'country':2,
            'disco':3,
            'hiphop':4,
            'jazz':5,
            'metal':6,
            'pop':7,
            'reggae':8,
            'rock':9
        }

        if isinstance(config,MusicConfig):
          self.config = config
        else:
          self.config = MusicConfig()
          self.config.train_test_ratio = 0.90
          self.config.number_of_epochs = 300
          self.config.learning_rate = 0.0001
          self.config.batch_size = 100
          self.sample_length = 2
          self.n_mels = 64

    def get_all_samples(self):
        result = []
        for root,_,files in os.walk(self.data_dir):
            for f in files:
                f_path = Path(f"{root}/{f}")
                if not f_path.suffix=='.wav':
                    continue

                result.append(f_path)
        
        return result

    def get_samples_per_type(self):
        result = {}
        all_samples = self.get_all_samples()
        for f_path in all_samples:
            genre,number = f_path.stem.split('.')
            if not genre in result:
                result[genre] = []
            result[genre].append(f_path)

        return result
        
    def plot_all_spectograms(self):
        logging.info("Plotting all Mel spectograms...")

        all_samples = self.get_all_samples()
        for f_path in all_samples:
            genre,number = f_path.stem.split('.')
            output_dir = self.plot_dir / genre
            output_dir.mkdir(parents=True,exist_ok=True)
            output_file = output_dir / f"{genre}_{number}.png"
            self.plot_spectogram(f_path,output_file)

    def get_mel_spectogram(self,sample,n_seconds=None,random=True,y=None,sr=None):

        if isinstance(sample,str):
            sample = Path(sample)
        if not sample.exists():
            logging.error(f"File {sample} does not exist")
            return None

        if not isinstance(y,np.ndarray) and not sr:
            y,sr = librosa.load(sample)

        if n_seconds:
            start = 0
            if random:
                start = np.random.randint(0,len(y)-n_seconds*sr)
            y = y[start:start+sr*n_seconds]
            pass

        return self.calculate_mel_spec(y,sr)

    def calculate_mel_spec(self,y,sr):
        mel_spec = librosa.feature.melspectrogram(y=y,sr=sr,n_mels=self.config.n_mels)
        mel_spec_db = librosa.power_to_db(mel_spec,ref=np.max)

        return mel_spec_db

    def plot_spectogram(self,sample,output):      
        y,sr = librosa.load(sample)  
        mel_spec_db = self.calculate_mel_spec(y,sr)
        librosa.display.specshow(mel_spec_db, sr=sr, x_axis='time', y_axis='mel')
        plt.colorbar(format='%+2.0f dB') 
        plt.title(f"Mel spectogram")
        plt.savefig(output)
        plt.clf()
        logging.info(f"Generated plot: {output}")

    def plot_spectogram_raw(self,y,sr,output):        
        mel_spec_db = self.calculate_mel_spec(y,sr)
        librosa.display.specshow(mel_spec_db, sr=sr, x_axis='time', y_axis='mel')
        plt.colorbar(format='%+2.0f dB') 
        plt.title(f"Mel spectogram")
        plt.savefig(output)
        plt.clf()
        logging.info(f"Generated plot: {output}")

    def manipulate_data(self,data,noise_factor,pitch_factor,speed_factor):
        logging.debug("Manipulating data...")
        y,sr = librosa.load(data)
        result = y

        if noise_factor:
          noise = np.random.randn(len(result))*noise_factor
          result = result + noise

        if pitch_factor:
          sampling_rate = 22050
          result = librosa.effects.pitch_shift(result, sampling_rate, pitch_factor)

        if speed_factor:
          result = librosa.effects.time_stretch(result, speed_factor)

        return result

    def load_data(self):
        logging.info("Loading data...")
        samples_per_type = self.get_samples_per_type()

        x_train,x_test = [],[]
        y_train,y_test = [],[]
        for genre in samples_per_type:
            samples = samples_per_type[genre]
            np.random.shuffle(samples)
            logging.info(f"Processing genre {genre}")
            for i in range(len(samples)):
                sample = samples[i]

                for _ in range(self.config.num_data_series_per_sample):
                    mel_spec = self.get_mel_spectogram(sample,n_seconds=self.config.sample_length)

                    if self.config.augment_data:
                        manipulated_sample = self.manipulate_data(sample,self.config.noise_factor,self.config.pitch_factor,self.config.speed_factor)
                        mel_spec_manipulated = self.get_mel_spectogram(sample,n_seconds=self.config.sample_length,y=manipulated_sample,sr=22050)

                    if i/len(samples)<self.config.train_test_ratio:
                        x_train.append(mel_spec)
                        y_train.append(self.genre_encoding[genre])

                        if self.config.augment_data:
                          x_train.append(mel_spec_manipulated)
                          y_train.append(self.genre_encoding[genre])
                    else:
                        x_test.append(mel_spec)
                        y_test.append(self.genre_encoding[genre]) 

                        if self.config.augment_data:
                          x_test.append(mel_spec_manipulated)
                          y_test.append(self.genre_encoding[genre])

            logging.info(f"Currently {len(x_train)} training points and {len(x_test)} testing points")

        x_train = np.array(x_train)
        y_train = np.array(y_train)
        x_test = np.array(x_test)
        y_test = np.array(y_test)

        self.x_train = x_train.reshape(x_train.shape+(1,))
        self.y_train = to_categorical(y_train)
        self.x_test = x_test.reshape(x_test.shape+(1,))
        self.y_test = to_categorical(y_test)

        #print(f"X train shape: {x_train.shape}")
        #print(f"X test shape: {x_test.shape}")
        #print(f"Y train shape: {y_train.shape}")
        #print(f"Y test shape: {y_test.shape}")

    def train_model(self):
        logging.info("Training CNN model...")
        callback = [tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=5)]

        self.history = self.model.fit(
            self.x_train,
            self.y_train,
            validation_data=(self.x_test,self.y_test),
            epochs=self.config.number_of_epochs,
            #callbacks=callback,
            verbose=2,
            batch_size=self.config.batch_size)
        
        self.trained = True

    def save_results_training(self):
        logging.info("Saving results from training model")

        acc = self.history.history['accuracy']
        val_acc = self.history.history['val_accuracy']
        loss = self.history.history['loss']
        val_loss = self.history.history['val_loss']

        x = range(self.config.number_of_epochs)

        fig,axes = plt.subplots(1,2,figsize=(16,8))
        axes[0].plot(x,acc,label="Training accuracy")
        axes[0].plot(x,val_acc,label="Validation accuracy")
        axes[0].set_xlabel("Epochs")
        axes[0].set_ylabel("Accuracy")
        axes[0].set_title("Model accuracy")
        axes[0].legend()
        axes[0].grid(b=True)
        axes[1].plot(x,loss,label="Training loss")
        axes[1].plot(x,val_loss,label="Validation loss") 
        axes[1].set_xlabel("Epochs")
        axes[1].set_ylabel("Loss")
        axes[1].set_title("Model loss")
        axes[1].legend()
        axes[1].grid(b=True)

        output_dir = self.get_results_dir()
        fig.savefig(output_dir / "training_evolution.png")
        self.model.save(output_dir / "saved_model")

        modelsumma = output_dir / "model_summary.txt"
        modelsumma.touch(exist_ok=True)
        with modelsumma.open('w') as f:
            with redirect_stdout(f):
                self.model.summary()

        modelconfig = output_dir / "model_config.txt"
        modelconfig.touch(exist_ok=True)
        with modelconfig.open('w') as f:
            with redirect_stdout(f):
                print(self.config)

    def get_results_dir(self):
        folders = [f.name for f in os.scandir(self.model_results_dir) if f.is_dir()]
        if not folders:
          result = self.model_results_dir / "results_1"
          result.mkdir(parents=True,exist_ok=True)
          return result

        folder_numbers = [int(folder.split("_")[-1]) for folder in folders]
        folder_numbers = sorted(folder_numbers)
        latest = folder_numbers[-1]
        new = latest+1
        result = self.model_results_dir / f"results_{new}"
        result.mkdir(parents=True,exist_ok=True)

        return result

    def load_saved_model(self,exec_number):
      logging.info(f"Loading saved model number {exec_number}")
      saved_model = self.model_results_dir / f"results_{exec_number}" / "saved_model"
      if not saved_model.is_dir():
        logging.error(f"No results found for execution number {exec_number}")
        return False

      self.model = models.load_model(saved_model)
      self.trained = True

    def predict(self,sample,number_of_tries=None,verbose=False):
        '''
        Predict the genre of a provided sample.
        '''
        if isinstance(sample,str):
            sample = Path(sample)
        if not sample.exists():
            logging.error(f"File {sample} does not exist")
            return None

        MAX_TRIES = 5
        y,sr = librosa.load(sample)
        sample_length = len(y)/sr

        if not number_of_tries:
            max_tries = int(sample_length/self.config.sample_length)
            number_of_tries = min(MAX_TRIES,max_tries)


        if sample_length<self.config.sample_length:
            logging.error(f"The provided sample does not have at least {self.config.sample_length} seconds of sound, rejected")
            return None

        results = []

        for _ in range(number_of_tries):

            start = np.random.randint(0,len(y)-self.config.sample_length*sr)
            sample_to_predict = y[start:start+sr*self.config.sample_length]

            mel_spec = self.calculate_mel_spec(sample_to_predict,sr)

            to_predict = np.array([mel_spec])
            to_predict = to_predict.reshape(to_predict.shape+(1,))
            to_predict = tf.convert_to_tensor(to_predict)

            results.append(self.model.predict(to_predict)[0])

        if verbose:
            header = "{0:<17}".format("Genre")
            for i in range(number_of_tries):
                header = header + "{0:>10}".format(f"Pred. #{i+1}")
            header = header + "{0:>15}".format("Mean result")
            print(header)

        results_json = {}
        for genre in self.genre_encoding:
            line = "{0:<15}: ".format(genre)
            percs = []
            for result in results:
                perc = round(result[self.genre_encoding[genre]]*100,2)
                percs.append(perc)
                line = line+"{0:>10}".format(str(perc)+"%")
            
            mean_perc = round(np.mean(percs),2)
            line = line+"{0:>15}".format(str(mean_perc)+"%")
            results_json[genre] = mean_perc

            if verbose:
                print(line) 

        return results_json
        
    def init_model(self):
        logging.info("Initializing CNN model")
        model = models.Sequential()
        model.add(Conv2D(32,(3,3),activation='relu',input_shape=(self.config.n_mels,(43*self.config.sample_length)+1,1)))
        model.add(MaxPooling2D(pool_size=(2,2),strides=(2,2),padding='same'))
        model.add(BatchNormalization())

        model.add(Conv2D(32,(3,3),activation='relu'))
        model.add(MaxPooling2D(pool_size=(2,2),strides=(2,2),padding='same'))
        model.add(BatchNormalization())

        model.add(Conv2D(32,(2,2),activation='relu'))
        model.add(MaxPooling2D(pool_size=(2,2),strides=(2,2),padding='same'))
        model.add(BatchNormalization())

        model.add(Flatten())
        model.add(Dense(64,activation='relu',kernel_regularizer=regularizers.l2(0.01)))
        model.add(Dropout(0.5))

        model.add(Dense(32,activation='relu',kernel_regularizer=regularizers.l2(0.01)))
        model.add(Dropout(0.5))

        model.add(Dense(16,activation='relu',kernel_regularizer=regularizers.l2(0.01)))
        model.add(Dropout(0.5))

        #output layer
        model.add(Dense(10,activation='softmax'))

        opt = Adam(learning_rate=self.config.learning_rate)
        model.compile(optimizer=opt,loss='categorical_crossentropy',metrics=['accuracy'])

        self.model = model