import pandas as pd
import binascii
import random
import time

class Shingling:
    def __init__(self, data, k_shingle = 5):
        self.data = data
        self.k_shingle = k_shingle

    def create_set(self):
        all_shingle_sets = {}
        for index, record in enumerate(self.data):
            # contains all unique (no duplicate) shingles of input data
            shingle_set = set()

            for i in range(len(record) - self.k_shingle + 1):
                # create shingle based on specified length
                shingle = record[i: i + self.k_shingle].encode()
                # hashing to 32-bit integer
                crc = binascii.crc32(shingle) & 0xffffffff
                # add hash value to document shingleset if not present yet
                shingle_set.add(crc)

            # store all shingle sets from each record together
            all_shingle_sets[index] = shingle_set
        return all_shingle_sets

class CompareSets:
    def __init__(self, sets):
        self.sets = sets

    def compute(self):
        # create dict of all jaccard similarities
        jaccard_similarities = {}
        for i in range(0, len(self.sets)):
            set1 = self.sets[i]
            for j in range(i + 1, len(self.sets)):
                set2 = self.sets[j]

                # calculate and store jaccard similarities
                jaccard_similarities[(i, j)] = (len(set1.intersection(set2)) / len(set1.union(set2)))

        return jaccard_similarities

class MinHash:
    # for crc32 hashing
    max_shingle = (2 ** 32) - 1
    max_prime = 4294967311

    def __init__(self, sets, num_hashes = 10):
        self.sets = sets
        self.num_hashes = num_hashes

    def generate_coefficients(self):
        # list all coefficients
        coefficients = []

        for i in range(0, self.num_hashes):
            random_coefficient = random.randint(0, self.max_shingle)

            # ensure unique coefficients
            while random_coefficient in coefficients:
                random_coefficient = random.randint(0, self.max_shingle)

            coefficients.append(random_coefficient)
        return coefficients

    def create_signatures(self, coefficient_a, coefficient_b):
        # signature vectors
        signatures = []

        # hashfunction on shingle and take lowest value
        for index, shingleSet in self.sets.items():

            sig = []

            for i in range(0, self.num_hashes):
                min_hash = self.max_prime + 1
                for shingle in shingleSet:
                    # generate hash code
                    hash_code = (coefficient_a[i] * shingle + coefficient_b[i]) % self.max_prime

                    # store lowest hash value as min_hash
                    if hash_code < min_hash:
                        min_hash = hash_code

                sig.append(min_hash)

            signatures.append(sig)
        return signatures

class CompareSignatures:
    def __init__(self, signatures):
        self.signatures = signatures

    def estimate_similarity(self):
        estimated_similarities = {}
        num_signatures = len(self.signatures)

        # compare each signature with another
        for i in range(0, num_signatures):
            sig1 = self.signatures[i]

            for j in range(i + 1, num_signatures):
                sig2 = self.signatures[j]

                # count the number of equivalent values in signature
                count = 0

                # compare signatures for each MinHash value
                num_hashes = len(self.signatures[0])
                for k in range(0, num_hashes):
                    if sig1[k] == sig2[k]:
                        count += 1

                # calculate ratio of matched values in signatures
                estimated_similarities[(i, j)] = count / num_hashes
        return estimated_similarities

class LocalitySensitiveHashing:
    def __init__(self, signatures, bands, rows, threshold):
        self.signatures = signatures
        self.bands = bands
        self.rows = rows
        self.threshold = threshold

    def get_candidates(self):
        candidate_pairs = {}
        num_signatures = len(self.signatures)

        for band in range(0, self.bands):
            # hash bands and compare on equality
            for i in range(0, num_signatures):
                band_hash1 = hash(tuple(self.signatures[i][band * self.rows:band * self.rows + self.rows]))
                for j in range(i + 1, num_signatures):
                    band_hash2 = hash(tuple(self.signatures[j][band * self.rows:band * self.rows + self.rows]))

                    # if hashes are equal store as candidate pairs
                    if band_hash1 == band_hash2:
                        c = (i, j)
                        if c not in candidate_pairs:
                            candidate_pairs[(i, j)] = 1
                        else:
                            candidate_pairs[(i, j)] += 1

        return candidate_pairs

    def estimate_similarity(self, candidates):
        estimated_similarities = {}
        for c_pair, matching_bands in candidates.items():
            if (matching_bands / self.bands) >= self.threshold:
                sig1 = self.signatures[c_pair[0]]
                sig2 = self.signatures[c_pair[1]]

                # count the number of equivalent values in signature
                count = 0
                num_hashes = len(self.signatures[0])
                for k in range(0, num_hashes):
                    if sig1[k] == sig2[k]:
                        count += 1

                # calculate ratio of matched values in signatures
                candidates_similarity = count / num_hashes
                estimated_similarities[c_pair] = candidates_similarity
        return estimated_similarities



if __name__ == "__main__":

    # load airline reviews
    reviews_all = pd.read_csv("data/skytrax-reviews-dataset-master/data/airline.csv").content
    # num of reviews to analyse
    numReviews = 500
    # subset of reviews
    reviews = reviews_all[0:numReviews]
    del reviews_all

    #############
    # Shingling
    #############

    # create shingles, taking k of 7 since the reviews tend to be short
    t0 = time.time()
    k_shingle = 8
    shingles = Shingling(reviews, k_shingle).create_set()
    elapsed = time.time() - t0
    print("Shingling took %.2f sec \n" % elapsed)

    #####################
    # Jaccard Similarity
    #####################

    #  compute jaccard similarity and show top results
    t0 = time.time()
    jaccard_similarity = CompareSets(shingles).compute()
    elapsed = time.time() - t0
    print("Jaccard took %.2f sec \n" % elapsed)
    print("---- Top results comparing sets ----")
    for index, value in jaccard_similarity.items():
        if value >= 0.4:
            print(index, value)
            print(reviews[index[0]], "\n")
            print(reviews[index[1]], "\n")
    del jaccard_similarity

    ###########
    # MinHash
    ###########

    t0 = time.time()
    num_hashes = 10

    min_hash = MinHash(shingles, num_hashes)

    # generate random coefficients
    coefficient_a = min_hash.generate_coefficients()
    coefficient_b = min_hash.generate_coefficients()

    # create signatures
    signatures = min_hash.create_signatures(coefficient_a, coefficient_b)

    elapsed = time.time() - t0
    print("MinHashing for", num_hashes, "hashfunctions took %.2f sec \n" % elapsed)

    #####################
    # Compare Signatures
    #####################

    t0 = time.time()
    signature_similarity = CompareSignatures(signatures).estimate_similarity()

    elapsed = time.time() - t0
    print("Comparing signatures took %.2f sec \n" % elapsed)

    print("---- Top results comparing signatures ----")
    for index, value in signature_similarity.items():
        if value >= 0.4:
            print(index, value)
            print(reviews[index[0]], "\n")
            print(reviews[index[1]], "\n")
    del signature_similarity

    #########
    # LSH
    #########

    t0 = time.time()
    bands = 20
    rows = 5
    # Approximate threshold
    threshold = (1 / bands) ** (1 / rows)

    lsh = LocalitySensitiveHashing(signatures, bands, rows, threshold)
    # get pairs of candidates
    candidates = lsh.get_candidates()

    # evaluate signature similarity meeting the threshold
    candidates_estimated_similarity = lsh.estimate_similarity(candidates)
    print("LSH for", bands, "bands,", rows, "rows,", "and threshold", threshold, "took %.2f sec \n" % elapsed)

    print("---- Top results comparing signatures after LSH ----")
    for index, value in candidates_estimated_similarity.items():
        if value >= 0.4:
            print(index, value)
            print(reviews[index[0]], "\n")
            print(reviews[index[1]], "\n")

    del candidates, candidates_estimated_similarity







