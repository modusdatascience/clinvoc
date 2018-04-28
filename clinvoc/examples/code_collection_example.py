from clinvoc.code_collections import CodeCollection
import os
from clinvoc.icd9 import ICD9CM
from clinvoc.code_maps import CodeMap
from clinvoc.icd10 import ICD10CM

# This CSV file contains sets of codes in several categories
# See: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4134331/
filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pccccs2.csv')

# Create a CodeCollection based on the CSV file
collection = CodeCollection.from_csv(filename, vocabs={'ICD-9': ICD9CM()}, header=True,
                                     ignore=[0, 'ICD-10'])

# Create a CodeMap from the collection
code_map = CodeMap.from_code_collection(collection, standardizers={'ICD-9': ICD9CM().standardize, 
                                                                   'ICD-10': ICD10CM().standardize})

# Map ICD9 code V45.2 to see that it's a neurologic or neuromuscular device
print(code_map[('ICD-9', 'V45.2')])

