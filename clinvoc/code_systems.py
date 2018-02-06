from frozendict import frozendict
from clinvoc.icd10 import ICD10PCS, ICD10CM
from clinvoc.icd9 import ICD9CM, ICD9PCS
from clinvoc.hcpcs import HCPCS
from clinvoc.loinc import LOINC
from clinvoc.ndc import NDC
from clinvoc.ubrev import UBREV

def code_system_standardizers(icd10cm=dict(), icd10pcs=dict(), icd9cm=dict(),
                              icd9pcs=dict(), hcpcs=dict(), loinc=dict(),
                              ndc=dict(), ubrev=dict()):
    result = frozendict(
                        ICD10PCS = ICD10PCS(**icd10cm).standardize,
                        ICD10CM = ICD10CM(**icd10pcs).standardize,
                        ICD9CM = ICD9CM(**icd9cm).standardize,
                        ICD9PCS = ICD9PCS(**icd9pcs).standardize,
                        HCPCS = HCPCS(**hcpcs).standardize,
                        LOINC = LOINC(**loinc).standardize,
                        NDC = NDC(**ndc).standardize,
                        UBREV = UBREV(**ubrev).standardize,
                        )
    
    return result