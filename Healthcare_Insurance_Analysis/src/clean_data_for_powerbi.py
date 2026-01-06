#!/usr/bin/env python3
"""
Healthcare Insurance Data Cleaning for Power BI
Prepares clean, analysis-ready CSV for dashboard creation
Author: Syed Muhammad Ali
"""

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def clean_healthcare_data(input_path, output_path):
    """
    Clean and prepare healthcare insurance data for Power BI
    """
    print("🏥 Healthcare Insurance Data Cleaning for Power BI")
    print("=" * 55)
    
    # Load original data
    print("📊 Loading original data...")
    df = pd.read_csv(input_path)
    print(f"Original dataset: {df.shape[0]} rows, {df.shape[1]} columns")
    
    # 1. Handle Missing Values
    print("\n🧹 Step 1: Handling missing values...")
    missing_before = df.isnull().sum().sum()
    
    # Fill missing values with appropriate methods
    df['age'].fillna(df['age'].mean(), inplace=True)
    df['avg_claim_amount'].fillna(df['avg_claim_amount'].mean(), inplace=True)
    df['risk_score'].fillna(df['risk_score'].mean(), inplace=True)
    
    missing_after = df.isnull().sum().sum()
    print(f"Missing values reduced from {missing_before} to {missing_after}")
    
    # 2. Handle Outliers using IQR method
    print("\n📈 Step 2: Treating outliers...")
    def treat_outliers_iqr(data, column):
        Q1 = data[column].quantile(0.25)
        Q3 = data[column].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers_before = ((data[column] < lower_bound) | (data[column] > upper_bound)).sum()
        data[column] = data[column].clip(lower=lower_bound, upper=upper_bound)
        
        return outliers_before
    
    # Treat outliers in financial columns
    financial_columns = ['avg_claim_amount', 'total_claim_amount']
    for col in financial_columns:
        outliers_count = treat_outliers_iqr(df, col)
        print(f"  {col}: {outliers_count} outliers treated")
    
    # 3. Create Risk Segments
    print("\n🎯 Step 3: Creating risk segments...")
    df['risk_segment'] = pd.cut(df['risk_score'], 
                               bins=[0, 0.5, 0.8, 1.0],
                               labels=['Low Risk', 'Medium Risk', 'High Risk'],
                               include_lowest=True)
    
    # Convert to string for Power BI compatibility
    df['risk_segment'] = df['risk_segment'].astype(str)
    
    risk_distribution = df['risk_segment'].value_counts()
    print(f"Risk segments created:")
    for segment, count in risk_distribution.items():
        print(f"  {segment}: {count} members ({count/len(df)*100:.1f}%)")
    
    # 4. Create Synthetic Fraud Indicators (for demonstration)
    print("\n🚨 Step 4: Creating fraud indicators...")
    np.random.seed(42)  # For reproducible results
    
    # Create fraud probability based on suspicious patterns
    fraud_probability = np.where(
        (df['avg_claim_amount'] > df['avg_claim_amount'].quantile(0.95)) &
        (df['risk_score'] > 0.9) &
        (df['num_claims'] > 5),
        0.15,  # 15% chance for highly suspicious cases
        np.where(
            (df['avg_claim_amount'] > df['avg_claim_amount'].quantile(0.85)) |
            (df['risk_score'] > 0.8) |
            (df['num_claims'] > 3),
            0.05,  # 5% chance for moderately suspicious cases
            0.01   # 1% base fraud rate
        )
    )
    
    df['fraud_flag'] = np.random.binomial(1, fraud_probability)
    df['fraud_status'] = df['fraud_flag'].map({0: 'Legitimate', 1: 'Fraudulent'})
    
    fraud_count = df['fraud_flag'].sum()
    fraud_rate = fraud_count / len(df) * 100
    print(f"Fraud indicators created: {fraud_count} fraudulent cases ({fraud_rate:.1f}%)")
    
    # 5. Create Additional Business Intelligence Columns
    print("\n📊 Step 5: Creating BI-ready columns...")
    
    # Age groups for better analysis
    df['age_group'] = pd.cut(df['age'], 
                            bins=[0, 30, 45, 60, 100],
                            labels=['18-30', '31-45', '46-60', '60+'],
                            include_lowest=True).astype(str)
    
    # Claim frequency categories
    df['claim_frequency'] = pd.cut(df['num_claims'],
                                  bins=[0, 1, 3, 5, float('inf')],
                                  labels=['Low (1)', 'Medium (2-3)', 'High (4-5)', 'Very High (6+)'],
                                  include_lowest=True).astype(str)
    
    # Claim amount categories
    df['claim_amount_category'] = pd.cut(df['avg_claim_amount'],
                                        bins=[0, 5000, 15000, 30000, float('inf')],
                                        labels=['Low (<$5K)', 'Medium ($5K-$15K)', 'High ($15K-$30K)', 'Very High (>$30K)'],
                                        include_lowest=True).astype(str)
    
    # Cost per claim calculation
    df['cost_per_claim'] = df['total_claim_amount'] / df['num_claims'].replace(0, 1)
    
    # High-value member flag (top 10% by total claims)
    high_value_threshold = df['total_claim_amount'].quantile(0.9)
    df['high_value_member'] = (df['total_claim_amount'] > high_value_threshold).map({True: 'Yes', False: 'No'})
    
    # Chronic condition impact on costs
    df['chronic_cost_impact'] = df['chronic_condition'].map({'Yes': 'High Impact', 'No': 'Low Impact'})
    
    print(f"  Age groups: {df['age_group'].value_counts().to_dict()}")
    print(f"  High-value members: {df['high_value_member'].value_counts()['Yes']} identified")
    
    # 6. Data Type Optimization for Power BI
    print("\n🔧 Step 6: Optimizing data types...")
    
    # Convert categorical columns to string (Power BI friendly)
    categorical_columns = ['gender', 'region', 'policy_type', 'chronic_condition', 
                          'risk_segment', 'fraud_status', 'age_group', 'claim_frequency',
                          'claim_amount_category', 'high_value_member', 'chronic_cost_impact']
    
    for col in categorical_columns:
        if col in df.columns:
            df[col] = df[col].astype(str)
    
    # Ensure numeric columns are properly typed
    numeric_columns = ['age', 'num_claims', 'avg_claim_amount', 'total_claim_amount', 
                      'risk_score', 'cost_per_claim', 'fraud_flag']
    
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Round financial columns to 2 decimal places
    financial_cols = ['avg_claim_amount', 'total_claim_amount', 'risk_score', 'cost_per_claim']
    for col in financial_cols:
        if col in df.columns:
            df[col] = df[col].round(2)
    
    # 7. Create Summary Statistics for Dashboard KPIs
    print("\n📈 Step 7: Calculating summary statistics...")
    
    total_members = len(df)
    total_claims_cost = df['total_claim_amount'].sum()
    avg_claim_amount = df['avg_claim_amount'].mean()
    fraud_rate = df['fraud_flag'].mean() * 100
    high_risk_percentage = (df['risk_segment'] == 'High Risk').mean() * 100
    chronic_percentage = (df['chronic_condition'] == 'Yes').mean() * 100
    
    # Add metadata row for Power BI KPIs (optional - can be used for dashboard cards)
    summary_stats = {
        'total_members': total_members,
        'total_claims_cost': total_claims_cost,
        'average_claim_amount': avg_claim_amount,
        'fraud_rate_percent': fraud_rate,
        'high_risk_percentage': high_risk_percentage,
        'chronic_condition_percentage': chronic_percentage
    }
    
    print("Summary Statistics:")
    for key, value in summary_stats.items():
        if 'percentage' in key or 'rate' in key:
            print(f"  {key}: {value:.1f}%")
        elif 'cost' in key or 'amount' in key:
            print(f"  {key}: ${value:,.0f}")
        else:
            print(f"  {key}: {value:,.0f}")
    
    # 8. Final Data Quality Check
    print("\n✅ Step 8: Final data quality check...")
    
    # Check for any remaining issues
    final_missing = df.isnull().sum().sum()
    duplicates = df.duplicated().sum()
    negative_claims = (df['avg_claim_amount'] < 0).sum()
    
    print(f"  Missing values: {final_missing}")
    print(f"  Duplicate rows: {duplicates}")
    print(f"  Negative claim amounts: {negative_claims}")
    
    # Remove any duplicate patient_ids (keep first occurrence)
    if 'patient_id' in df.columns:
        duplicates_removed = df.duplicated(subset=['patient_id']).sum()
        df = df.drop_duplicates(subset=['patient_id'], keep='first')
        if duplicates_removed > 0:
            print(f"  Removed {duplicates_removed} duplicate patient records")
    
    # 9. Save Cleaned Data
    print(f"\n💾 Step 9: Saving cleaned data...")
    
    # Reorder columns for better Power BI experience
    column_order = [
        'patient_id', 'age', 'age_group', 'gender', 'region', 'policy_type',
        'chronic_condition', 'chronic_cost_impact', 'risk_score', 'risk_segment',
        'num_claims', 'claim_frequency', 'avg_claim_amount', 'claim_amount_category',
        'total_claim_amount', 'cost_per_claim', 'high_value_member',
        'fraud_flag', 'fraud_status'
    ]
    
    # Ensure all columns exist and reorder
    available_columns = [col for col in column_order if col in df.columns]
    other_columns = [col for col in df.columns if col not in column_order]
    final_columns = available_columns + other_columns
    
    df_final = df[final_columns].copy()
    
    # Save to CSV
    df_final.to_csv(output_path, index=False)
    
    print(f"✅ Clean data saved to: {output_path}")
    print(f"📊 Final dataset: {df_final.shape[0]} rows, {df_final.shape[1]} columns")
    
    # 10. Create Power BI Import Guide
    guide_content = f"""
# 🔥 POWER BI IMPORT GUIDE

## 📊 Dataset Overview
- **File:** {output_path}
- **Records:** {df_final.shape[0]:,}
- **Columns:** {df_final.shape[1]}
- **Total Claims Value:** ${total_claims_cost:,.0f}
- **Fraud Rate:** {fraud_rate:.1f}%

## 🎯 Key Metrics for Dashboard Cards
- Total Members: {total_members:,}
- Average Claim Amount: ${avg_claim_amount:,.0f}
- High-Risk Members: {high_risk_percentage:.1f}%
- Chronic Condition Members: {chronic_percentage:.1f}%

## 📈 Recommended Visualizations

### 1. Risk Analysis
- **Pie Chart:** Risk Segment Distribution
- **Bar Chart:** Total Claims by Risk Segment
- **Scatter Plot:** Risk Score vs Claim Amount

### 2. Fraud Detection
- **Donut Chart:** Fraud Status Distribution
- **Map:** Fraud Rate by Region
- **Table:** Top 10 Suspicious Claims

### 3. Cost Analysis
- **Waterfall Chart:** Cost Breakdown by Factors
- **Line Chart:** Claims Trend by Age Group
- **Heatmap:** Policy Type vs Region Performance

### 4. Member Demographics
- **Bar Chart:** Claims by Age Group
- **Stacked Bar:** Chronic Condition Impact
- **KPI Cards:** Key Business Metrics

## 🔧 Power BI Import Steps
1. Open Power BI Desktop
2. Get Data > Text/CSV
3. Select: {output_path}
4. Click Transform Data for any final adjustments
5. Load data and start building dashboard

## 📊 Pre-built Measures (DAX)
```dax
Total Claims Cost = SUM(Claims[total_claim_amount])
Average Risk Score = AVERAGE(Claims[risk_score])
Fraud Rate % = DIVIDE(COUNTROWS(FILTER(Claims, Claims[fraud_flag] = 1)), COUNTROWS(Claims)) * 100
High Risk Members = COUNTROWS(FILTER(Claims, Claims[risk_segment] = "High Risk"))
```

## 🎨 Suggested Color Themes
- **Risk Levels:** Green (Low), Yellow (Medium), Red (High)
- **Fraud Status:** Blue (Legitimate), Red (Fraudulent)
- **Regions:** Use consistent color mapping

Ready for professional dashboard creation! 🚀
"""
    
    guide_path = output_path.replace('.csv', '_PowerBI_Guide.md')
    with open(guide_path, 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    print(f"📋 Power BI guide created: {guide_path}")
    
    return df_final, summary_stats

def main():
    """Main execution function"""
    # File paths
    input_file = '../data/Health_care_Insaurance.csv'
    output_file = '../data/Healthcare_Insurance_Clean_PowerBI.csv'
    
    try:
        # Clean the data
        cleaned_df, stats = clean_healthcare_data(input_file, output_file)
        
        print("\n🎉 SUCCESS! Data cleaning completed successfully!")
        print("=" * 55)
        print("📊 Your Power BI-ready dataset is available at:")
        print(f"📁 {output_file}")
        print(f"\n🚀 Ready for dashboard creation with {len(cleaned_df):,} clean records!")
        print("\n💡 Next Steps:")
        print("1. Import CSV into Power BI Desktop")
        print("2. Create visualizations using the recommended charts")
        print("3. Build executive dashboard with KPI cards")
        print("4. Share insights with stakeholders")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during data cleaning: {str(e)}")
        return False

if __name__ == "__main__":
    main()