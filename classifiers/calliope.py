from typing import Dict, List
import nltk
import pandas as pd
import pickle5 as pickle
import string

class CalliopeModel:
    def __init__(self, pickle_path: str, reference_path: str):
        # Read pickled model
        self.model = pickle.load(open(pickle_path, 'rb'))

        # Read reference data
        df = pd.read_csv(reference_path)
        data = df.to_numpy()
        word_string = ''
        for point in data:
            word_string = word_string + point[0].translate(str.maketrans('', '', string.punctuation))

        # Get word features
        all_words = nltk.FreqDist(w.lower() for w in word_string.split())
        self.word_features = list(all_words)[:5]

    def get_features(self, text: List[str]) -> Dict[str, bool]:
        words = set(text)
        features = {}
        for word in self.word_features:
            features['contains({})'.format(word)] = (word in words)
        return features
    
    def classify(self, text: str) -> bool:
        features = self.get_features(text.split())
        return self.model.classify(features) == 'GOOD'
