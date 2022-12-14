"""Compute score for Divergent Association Task,
a quick and simple measure of creativity
(Copyright 2021 Jay Olson; see LICENSE)"""

import re
import itertools
import numpy
import scipy.spatial.distance
import pandas as pd


class Model:
    """Create model to compute DAT"""

    def __init__(self, model="glove_100_3_polish.txt", dictionary="posortowane4.txt", pattern="^[a-ząćęłńóśźż][a-ząćęłńóśźż-]*[a-ząćęłńóśźż]$"):
        """Join model and words matching pattern in dictionary"""

        # Keep unique words matching pattern from file
        words = set()
        with open(dictionary, "r", encoding="utf8") as f:
            for line in f:
                if re.match(pattern, line):
                    words.add(line.rstrip("\n"))


        # Join words with model
        vectors = {}
        with open(model, "r", encoding="utf8") as f:
            for line in f:
                tokens = line.split(" ")
                word = tokens[0]
                if word in words:
                    vector = numpy.asarray(tokens[1:], "float32")
                    vectors[word] = vector
        self.vectors = vectors


    def validate(self, word, invalid=0):
        """Clean up word and find best candidate to use"""

        # Strip unwanted characters
        clean = re.sub(r"[^a-ząćęłńóśźżĄĆĘŁŃÓŚŹŻA-Z- ]+", "", word).strip().lower()
        if len(clean) <= 1:
            return None # Word too short

        # Generate candidates for possible compound words
        # "valid" -> ["valid"]
        # "cul de sac" -> ["cul-de-sac", "culdesac"]
        # "top-hat" -> ["top-hat", "tophat"]
        candidates = []
        if " " in clean:
            candidates.append(re.sub(r" +", "-", clean))
            candidates.append(re.sub(r" +", "", clean))
        else:
            candidates.append(clean)
            if "-" in clean:
                candidates.append(re.sub(r"-+", "", clean))
        for cand in candidates:
            if invalid == 0: # pass 0 to return valid words, 1 to return invalid words
                if cand in self.vectors:
                    return cand # Return first word that is in model
                return None  # Could not find valid word
            if invalid == 1:
                if cand in self.vectors:
                    continue
                return cand
                 # Could not find valid word




    def distance(self, word1, word2):
        """Compute cosine distance (0 to 2) between two words"""

        return scipy.spatial.distance.cosine(self.vectors.get(word1), self.vectors.get(word2))


    def dat(self, words, all_words=0, minimum=7):
        """Compute DAT score"""
        # Keep only valid unique words
        uniques = []
        for word in words:
            valid = self.validate(word, 0)
            if valid and valid not in uniques:
                uniques.append(valid)


        # Keep subset of words
        if len(uniques) >= minimum:
            subset = uniques[:minimum]
        else:
            return None # Not enough valid words

        # Compute distances between each pair of words
        distances = []
        pairs = []
        for word1, word2 in itertools.combinations(subset, 2):
            dist = self.distance(word1, word2)
            distances.append(dist)
            pairs.append((word1, word2, dist))
        


        if all_words == 1: #pass 1 to print out all distances, leave out to get DAT score only
            return pairs
        else:
            return (sum(distances) / len(distances)) * 100 # Compute the DAT score (average semantic distance multiplied by 100)

    def invalid_words(self, words):
        """Print words not found in model"""
        invalid_list = []
        for word in words:
            invalid_word = self.validate(word, 1)
            if invalid_word is not None:
                invalid_list.append(invalid_word)

        return invalid_list
