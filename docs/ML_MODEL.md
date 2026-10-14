# ML Model

## Selected model
ExtraTreesClassifier with `class_weight='balanced'` and tuned hyperparameters:
- n_estimators=300
- max_depth=30
- min_samples_split=5
- min_samples_leaf=1
- max_features='log2'

## Features (18)
Numerical: Tenure, CityTier, WarehouseToHome, HourSpendOnApp,
NumberOfDeviceRegistered, SatisfactionScore, NumberOfAddress, Complain,
OrderAmountHikeFromlastYear, CouponUsed, OrderCount, DaySinceLastOrder,
CashbackAmount.

Categorical: PreferredLoginDevice, PreferredPaymentMode, Gender,
PreferedOrderCat, MaritalStatus.

## Test set metrics
| Metric | Value |
|--------|-------|
| Accuracy | 97.34% |
| Precision | 91.67% |
| Recall | 92.63% |
| F1 | 0.9215 |
| ROC-AUC | 0.9963 |
| PR-AUC | 0.9824 |

## Threshold
Optimized on validation set to **0.4553** (maximizes F1).

## Top features
1. Tenure (24.99%)
2. CashbackAmount (9.31%)
3. Complain (6.54%)
4. WarehouseToHome (6.01%)