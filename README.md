# LSH
In progress: clean code and represent pipeline in class structure.
Calculating Jaccard Similarity, MinHash and LSH

Exercises consists of finding similar items within a dataset, normally in the form of duplicates but also highly similar forms of text.

Data:
- Flight reviews

Process:
- Loading in dataset 
- Shingling (n-grams)
- Jaccard similariy: computate exact similarity between document shingles (computationally expensive)
- MinHashing: represent sets as signature matrix through using the minimum values of various hash functions
- Signature similarity: computing similarity based on signatures (close to jaccard similarity)
- LSH: compare hashes of bands in each document to further optimize computational time, only evaluate signatures that meet the threshold
