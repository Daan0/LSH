# LSH
Calculating Jaccard Similarity, MinHash and LSH signature comparison

Exercises consists of finding similar items within a dataset, normally in the form of duplicates but also highly similar forms of text.

## Program structure
Classes: 
•	Shingling: constructs k–shingles of a given length k (e.g., 5) from a given document, computes a hash value for each unique shingle, and represents the document in the form of an ordered set of its hashed k-shingles.
•	CompareSets: computes the Jaccard similarity of two sets of integers – two sets of hashed shingles.
•	MinHashing: builds a minHash signature (in the form of a vector or a set) of a given length n from a given set of integers (a set of hashed shingles).
•	CompareSignatures: estimates similarity of two integer vectors – minhash signatures – as a fraction of components, in which they agree.
•	LocalitySensitiveHashing: implements the LSH technique, given a collection of minhash signatures (integer vectors) and a similarity threshold t, the LSH class (using banding and hashing) finds all candidate pairs of signatures that agree on at least fraction t of their components.

Main:
•	Loading in dataset
•	Shingling (n-grams)
•	Jaccard similarity: compute exact similarity between document shingles (computationally expensive)
•	MinHashing: represent sets as signature matrix through using the minimum values of various hash functions
•	Signature similarity: computing similarity based on signatures (estimation jaccard similarity)
•	LSH: compare hashes of bands in each document to further optimize computational time, only evaluate signatures that meet the threshold

## Data
Skytrax User Reviews Dataset (August 2nd, 2015)
A scraped dataset created from all user reviews found on Skytrax (www.airlinequality.com). It is unknown under which license Skytrax published these reviews. However, the reviews are accessible by anyone with a browser and the robots.txt on their website did not specifically prohibit the scraping of them.
Source: https://github.com/quankiquanki/skytrax-reviews-dataset
The program only takes a subset of the airline reviews dataset of 1000 records to compare on similarity. 

## Parameter space decisions
-	Shingle length is equal to 8 characters, as reviews tend to be of varying length and to allow for comparison of documents with varying word order.
-	Number of hash functions used are 10, in order to evaluate whether we can achieve highly accurate results with only a limited number of permutations.
-	As the reviews tend be not so similar in nature (no plagiarism), we opt for a larger bands and smaller rows. This will result into slightly longer computational cost, but allows us to compare documents based on a lower threshold.
