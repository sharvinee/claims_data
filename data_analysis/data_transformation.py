import pandas as pd
import hashlib as hl

# load data as df
filepath ='/workspaces/claims_data/data/claim_data.csv'
df = pd.read_csv(filepath)

# hash sensitive datadef hash_data(data):   
def sha256_hash(value):
  full_hash = hl.sha256(str(value).encode()).hexdigest()
  return full_hash[:10]

# apply hashing to sensitive columns
sensitive_columns = ['Patient ID', 'Claim ID']

for col in sensitive_columns:
    df[col] = df[col].apply(sha256_hash)

# save transformed data
output_filepath = '/workspaces/claims_data/data/clean_claims.csv' 
df.to_csv(output_filepath, index=False)
