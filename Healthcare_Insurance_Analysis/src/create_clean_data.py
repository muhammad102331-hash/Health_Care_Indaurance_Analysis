import pandas as pd
import numpy as np

# Load and clean the healthcare insurance data
print("Loading healthcare insurance data...")
df = pd.read_csv('../Health_Care/Health_care_Insaurance.csv')

print("Starting data cleaning process...")

# 1. Handle missing values
df['age'].fillna(df['age'].median(), inplace=True)
df['avg_claim_amount'].fillna(df['avg_claim_amount'].median(), inplace=True)
df['risk_score'].fillna(df['risk_score'].median(), inplace=True)

# 2. Handle outliers using IQR method
def treat_outliers_iqr(data, column):
    Q1 = data[column].quantile(0.25)
    Q3 = data[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    data[column] = data[column].clip(lower=lower_bound, upper=upper_bound)
    return data

# Apply outlier treatment
df = treat_outliers_iqr(df, 'avg_claim_amount')
df = treat_outliers_iqr(df, 'total_claim_amount')

# 3. Create risk segments
df['risk_segment'] = pd.cut(df['risk_score'], 
                           bins=[0, 0.5, 0.8, 1.0],
                           labels=['Low Risk', 'Medium Risk', 'High Risk'],
                           include_lowest=True)

# 4. Create fraud indicators (enhanced from original yes/no)
np.random.seed(42)
fraud_probability = np.where(
    (df['avg_claim_amount'] > df['avg_claim_amount'].quantile(0.95)) &
    (df['risk_score'] > 0.9) &
    (df['num_claims'] > 5),
    0.15,
    np.where(
        (df['avg_claim_amount'] > df['avg_claim_amount'].quantile(0.85)) |
        (df['risk_score'] > 0.8) |
        (df['num_claims'] > 3),
        0.05,
        0.01
    )
)

df['fraud_flag_binary'] = np.random.binomial(1, fraud_probability)
df['fraud_status'] = df['fraud_flag_binary'].map({0: 'Legitimate', 1: 'Fraudulent'})

# 5. Create additional analysis columns
# Age groups
df['age_group'] = pd.cut(df['age'], 
                        bins=[0, 30, 45, 60, 100],
                        labels=['18-30', '31-45', '46-60', '60+'],
                        include_lowest=True)

# Claim frequency categories
df['claim_frequency'] = pd.cut(df['num_claims'],
                              bins=[0, 1, 3, 5, float('inf')],
                              labels=['Low (1)', 'Medium (2-3)', 'High (4-5)', 'Very High (6+)'],
                              include_lowest=True)

# Claim amount categories
df['claim_amount_category'] = pd.cut(df['avg_claim_amount'],
                                    bins=[0, 5000, 15000, 30000, float('inf')],
                                    labels=['Low (<$5K)', 'Medium ($5K-$15K)', 'High ($15K-$30K)', 'Very High (>$30K)'],
                                    include_lowest=True)

# Cost per claim calculation
df['cost_per_claim'] = df['total_claim_amount'] / df['num_claims'].replace(0, 1)

# High-value member flag (top 10% by total claims)
high_value_threshold = df['total_claim_amount'].quantile(0.9)
df['high_value_member'] = df['total_claim_amount'] > high_value_threshold

# 6. Clean and format data for Power BI
# Convert categories to strings
categorical_cols = ['risk_segment', 'fraud_status', 'age_group', 'claim_frequency', 'claim_amount_category']
for col in categorical_cols:
    df[col] = df[col].astype(str)

# Convert boolean to Yes/No for better Power BI display
df['high_value_member'] = df['high_value_member'].map({True: 'Yes', False: 'No'})

# Round numeric columns
df['avg_claim_amount'] = df['avg_claim_amount'].round(2)
df['total_claim_amount'] = df['total_claim_amount'].round(2)
df['risk_score'] = df['risk_score'].round(3)
df['cost_per_claim'] = df['cost_per_claim'].round(2)

# 7. Reorder columns for better Power BI experience
column_order = [
    'patient_id', 'age', 'age_group', 'gender', 'region', 'policy_type',
    'chronic_condition', 'risk_score', 'risk_segment', 'num_claims', 'claim_frequency',
    'avg_claim_amount', 'claim_amount_category', 'total_claim_amount', 'cost_per_claim',
    'high_value_member', 'fraud_flag', 'fraud_flag_binary', 'fraud_status'
]

# Ensure all columns exist and reorder
df_clean = df[column_order].copy()

# Save cleaned data
output_path = '../data/Healthcare_Insurance_Clean_PowerBI.csv'
df_clean.to_csv(output_path, index=False)

print(f"✅ Cleaned data saved to: {output_path}")
print(f"📊 Dataset: {len(df_clean)} rows, {len(df_clean.columns)} columns")

# Display summary
print("\n📈 Data Summary:")
print(f"Total Members: {len(df_clean):,}")
print(f"Total Claims Cost: ${df_clean['total_claim_amount'].sum():,.0f}")
print(f"Average Claim Amount: ${df_clean['avg_claim_amount'].mean():,.0f}")
print(f"Fraud Rate: {df_clean['fraud_flag_binary'].mean()*100:.1f}%")
print(f"High-Risk Members: {(df_clean['risk_segment'] == 'High Risk').sum()}")

print("\nRisk Segment Distribution:")
print(df_clean['risk_segment'].value_counts())

print("\n🎯 Ready for Power BI import!")