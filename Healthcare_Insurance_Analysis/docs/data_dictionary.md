# Data Dictionary
## Healthcare Insurance Claims Analysis

**Last Updated:** January 6, 2026  
**Dataset:** Healthcare Insurance Claims Data  

---

## Overview
This document provides detailed definitions and specifications for all variables in the healthcare insurance claims dataset used for risk analysis and fraud detection.

---

## Variable Definitions

### 1. patient_id
- **Type:** String (Text)
- **Description:** Unique identifier for each insurance member
- **Format:** P + 6-digit number (e.g., P200001)
- **Range:** P200001 to P202000
- **Uniqueness:** Primary key - one record per patient
- **Business Use:** Member identification and tracking

### 2. age
- **Type:** Numeric (Integer)
- **Description:** Member's age in complete years at time of data collection
- **Range:** 18 to 89 years
- **Units:** Years
- **Missing Values:** 52 records (2.6%) - imputed with mean
- **Business Use:** Risk assessment, demographic analysis

### 3. gender
- **Type:** Categorical (Binary)
- **Description:** Member's self-reported gender
- **Values:** 
  - Male (51.6% of records)
  - Female (48.4% of records)
- **Missing Values:** None
- **Business Use:** Demographic analysis, risk modeling

### 4. region
- **Type:** Categorical (Nominal)
- **Description:** Geographic region of member's primary residence
- **Values:**
  - North (25.6% of records)
  - South (23.9% of records)  
  - East (24.1% of records)
  - West (26.4% of records)
- **Missing Values:** None
- **Business Use:** Regional cost analysis, fraud pattern detection

### 5. policy_type
- **Type:** Categorical (Ordinal)
- **Description:** Insurance policy tier/level
- **Values:**
  - Basic (39.9% of records) - Lowest coverage tier
  - Standard (34.5% of records) - Mid-level coverage
  - Premium (25.7% of records) - Highest coverage tier
- **Missing Values:** None
- **Business Use:** Cost analysis, member segmentation

### 6. chronic_condition
- **Type:** Binary (Boolean)
- **Description:** Indicates whether member has one or more diagnosed chronic medical conditions
- **Values:**
  - Yes (38.9% of records) - Has chronic condition(s)
  - No (61.1% of records) - No chronic conditions
- **Definition:** Chronic conditions include diabetes, heart disease, COPD, cancer, arthritis, etc.
- **Missing Values:** None
- **Business Use:** Cost prediction, care management targeting

### 7. num_claims
- **Type:** Numeric (Integer)
- **Description:** Total number of insurance claims filed by member during analysis period
- **Range:** 0 to 15 claims
- **Units:** Count of claims
- **Statistics:**
  - Mean: 2.8 claims
  - Median: 3.0 claims
  - Standard Deviation: 2.4 claims
- **Missing Values:** None (but 40 records had negative values, corrected to 0)
- **Business Use:** Utilization analysis, fraud detection

### 8. avg_claim_amount
- **Type:** Numeric (Currency)
- **Description:** Average dollar amount per claim for the member
- **Format:** USD currency
- **Range:** $1,067 to $13,936
- **Calculation:** total_claim_amount / num_claims (for members with >0 claims)
- **Statistics:**
  - Mean: $5,739
  - Median: $4,892
  - Standard Deviation: $3,231
- **Missing Values:** 38 records (1.9%) - imputed with mean
- **Business Use:** Cost analysis, risk assessment

### 9. total_claim_amount
- **Type:** Numeric (Currency)
- **Description:** Total dollar amount of all claims for the member
- **Format:** USD currency
- **Range:** $1,282 to $83,847 (after outlier treatment)
- **Statistics:**
  - Mean: $16,731
  - Median: $11,854
  - Standard Deviation: $17,125
- **Missing Values:** None
- **Outliers:** 109 records capped at upper bound
- **Business Use:** Cost analysis, member ranking, financial planning

### 10. risk_score
- **Type:** Numeric (Continuous)
- **Description:** Calculated risk score indicating member's likelihood of high future costs
- **Range:** 0.0 to 1.0
- **Scale:** 
  - 0.0 = Lowest risk
  - 1.0 = Highest risk
- **Statistics:**
  - Mean: 0.783
  - Median: 0.850
  - Standard Deviation: 0.239
- **Missing Values:** 29 records (1.45%) - imputed with mean
- **Business Use:** Member segmentation, predictive modeling

### 11. fraud_flag
- **Type:** Binary (Boolean)
- **Description:** Indicator of known or suspected fraudulent activity
- **Values:**
  - 0 = No fraud detected
  - 1 = Fraud confirmed or highly suspected
- **Original Format:** Yes/No (converted to 0/1)
- **Missing Values:** None
- **Business Use:** Fraud analysis, pattern detection, loss prevention

---

## Derived Variables
*Variables created during analysis*

### risk_segment
- **Type:** Categorical (Ordinal)
- **Description:** Member risk category based on risk_score
- **Values:**
  - Low Risk (0.0-0.5): 16.5% of members
  - Medium Risk (0.5-0.8): 28.7% of members
  - High Risk (0.8-1.0): 54.9% of members
- **Business Use:** Targeted interventions, resource allocation

### fraud_flag_synthetic
- **Type:** Binary (Boolean)
- **Description:** Synthetic fraud indicator created for analysis demonstration
- **Values:** 0 (No fraud), 1 (Fraud)
- **Rate:** 3.9% fraud rate
- **Business Use:** Fraud pattern analysis, model development

### suspicious_score
- **Type:** Numeric (Integer)
- **Description:** Composite score indicating suspicious activity level
- **Range:** 0 to 3
- **Components:**
  - high_claim_flag: Top 10% of claim amounts
  - frequent_claims_flag: Top 15% of claim frequency
  - high_risk_flag: Top 20% of risk scores
- **Business Use:** Fraud investigation prioritization

---

## Data Quality Metrics

### Completeness
- **Overall completeness:** 98.5%
- **Records with any missing values:** 119 (5.95%)
- **Complete records:** 1,881 (94.05%)

### Accuracy
- **Data validation pass rate:** 97.9%
- **Corrected anomalies:** 149 records
- **Quality score:** High (>95%)

### Consistency
- **Cross-field validation pass rate:** 99.8%
- **Business rule compliance:** 100%
- **Referential integrity:** 100%

---

## Business Rules & Constraints

### Logical Relationships
1. **avg_claim_amount × num_claims ≈ total_claim_amount** (with minor rounding differences)
2. **num_claims = 0** should correspond to **total_claim_amount = 0**
3. **chronic_condition = Yes** typically correlates with higher risk_score
4. **age** generally positively correlated with risk_score

### Data Validation Rules
1. All currency amounts must be positive
2. Age must be between 18 and 120
3. Risk score must be between 0.0 and 1.0
4. Number of claims must be non-negative integer

### Business Constraints
1. Members under 18 excluded from analysis (dependent coverage)
2. Outlier treatment applied to prevent skewing of analysis
3. Fraud flags require investigation validation

---

## Change Log

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2026-01-06 | 1.0 | Initial version | Syed Muhammad Ali |

---

## Contact Information
**Data Owner:** Syed Muhammad Ali  
**Email:** [email@domain.com]  
**Last Review:** January 6, 2026  
**Next Review:** April 6, 2026