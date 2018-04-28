# clinvoc

The clinvoc package gives you tools for working with clinical vocabularies in Python. 
- parse and standardize clinical vocabularies
- expand ranges and wildcard characters (i.e. '745.0-745.3' or '745.6*') into correct sets of codes 
- parse code collections directly from csv
- code mapping to categories

Currently, clinvoc supports the following code systems: 
- ICD9
- ICD10
- HCPCS
- NDC
- LOINC
- UBREV

### Installation
```bash 
$ pip install git+https://github.com/modusdatascience/clinvoc
```

### Basic example

```
from clinvoc.icd9 import ICD9CM

# This string describes a set of ICD 9 codes
codestring = '745.0-745.3, 745.6*, 746, 747.1-747.49, 747.81, 747.89, 35.8, 35.81, 35.82, 35.83, 35.84'

# Use clinvoc to parse and standardize the above codes
vocab = ICD9CM()
codeset = vocab.parse(codestring)

# check out your new parsed codeset
print(sorted(codeset))
```

### License

clinvoc is provided under an MIT license. Enjoy!
