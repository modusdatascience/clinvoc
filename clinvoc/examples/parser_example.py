from clinvoc.icd9 import ICD9CM

# This string describes a set of ICD 9 codes
codestring = '745.0-745.3, 745.6*, 746, 747.1-747.49, 747.81, 747.89, 35.8, 35.81, 35.82, 35.83, 35.84'

# Use clinvoc to parse and standardize the above codes
vocab = ICD9CM()
codeset = vocab.parse(codestring)
print(codeset)
