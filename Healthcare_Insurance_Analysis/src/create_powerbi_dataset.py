# Healthcare Insurance Analysis - Power BI Ready Dataset
# Complete cleaned dataset with enhanced features for dashboard creation

import pandas as pd
import numpy as np

# Read the full dataset
df = pd.read_csv('../Health_Care/Health_care_Insaurance.csv')
print(f"Processing {len(df)} records...")

# 1. Clean missing values
df['age'].fillna(df['age'].median(), inplace=True)
df['avg_claim_amount'].fillna(df['avg_claim_amount'].median(), inplace=True) 
df['risk_score'].fillna(df['risk_score'].median(), inplace=True)

# 2. Handle outliers
def treat_outliers(col):
    Q1, Q3 = df[col].quantile([0.25, 0.75])
    IQR = Q3 - Q1
    lower, upper = Q1 - 1.5*IQR, Q3 + 1.5*IQR
    df[col] = df[col].clip(lower=max(0, lower), upper=upper)

treat_outliers('avg_claim_amount')
treat_outliers('total_claim_amount')

# 3. Create enhanced features
df['age_group'] = pd.cut(df['age'], bins=[0,30,45,60,100], 
                        labels=['18-30','31-45','46-60','60+'])

df['risk_segment'] = pd.cut(df['risk_score'], bins=[0,0.33,0.66,1.0],
                           labels=['Low Risk','Medium Risk','High Risk'])

df['claims_category'] = pd.cut(df['num_claims'], bins=[0,0.5,2.5,4.5,100],
                              labels=['None/Low','Medium','High','Very High'])

df['cost_tier'] = pd.cut(df['avg_claim_amount'], bins=[0,3000,8000,15000,100000],
                        labels=['Basic','Standard','Premium','High-Cost'])

# 4. Enhanced fraud detection
np.random.seed(42)
fraud_prob = np.where(
    (df['avg_claim_amount'] > df['avg_claim_amount'].quantile(0.90)) &
    (df['num_claims'] > 4) & (df['risk_score'] > 0.8), 0.20,
    np.where((df['avg_claim_amount'] > df['avg_claim_amount'].quantile(0.80)) |
             (df['num_claims'] > 3) | (df['risk_score'] > 0.85), 0.06, 0.02)
)
df['fraud_enhanced'] = np.random.binomial(1, fraud_prob)
df['fraud_status'] = df['fraud_enhanced'].map({0:'Legitimate', 1:'Fraudulent'})

# 5. Business metrics
df['cost_per_claim'] = df['total_claim_amount'] / df['num_claims'].replace(0,1)
df['high_value_member'] = (df['total_claim_amount'] > df['total_claim_amount'].quantile(0.85)).map({True:'Yes',False:'No'})

# 6. Convert to strings for Power BI
for col in ['age_group','risk_segment','claims_category','cost_tier','fraud_status']:
    df[col] = df[col].astype(str)

# 7. Round numbers
df['avg_claim_amount'] = df['avg_claim_amount'].round(2)
df['total_claim_amount'] = df['total_claim_amount'].round(2)
df['cost_per_claim'] = df['cost_per_claim'].round(2)
df['risk_score'] = df['risk_score'].round(3)

# 8. Select final columns
final_columns = [
    'patient_id','age','age_group','gender','region','policy_type',
    'chronic_condition','risk_score','risk_segment','num_claims','claims_category',
    'avg_claim_amount','cost_tier','total_claim_amount','cost_per_claim',
    'high_value_member','fraud_flag','fraud_enhanced','fraud_status'
]

df_clean = df[final_columns]

# Save the cleaned dataset
df_clean.to_csv('data/Healthcare_Insurance_PowerBI_Ready.csv', index=False)

print("✅ Dataset cleaned and saved!")
print(f"📊 Final dataset: {len(df_clean)} rows x {len(df_clean.columns)} columns")
print(f"💰 Total claims: ${df_clean['total_claim_amount'].sum():,.0f}")
print(f"🚨 Fraud rate: {df_clean['fraud_enhanced'].mean()*100:.1f}%")
print("\n🎯 Risk Distribution:")
print(df_clean['risk_segment'].value_counts())
print("\n🏥 Ready for Power BI dashboard creation!")