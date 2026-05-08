import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LassoCV
from sklearn.model_selection import GroupKFold, cross_val_predict
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, r2_score
from xgboost import XGBRegressor

# Cleans the data, engineers features, and prepares the X, y variables for modeling
def prepare_data(combined_df):
    print("Preparing data features...")
    np.random.seed(418)
    df = combined_df.copy()
    
    # Keeping only players that have played atleast 5 full games
    df = df[df['minutesPlayed'] >= 450].copy()
    df['log_salary'] = np.log1p(df['Salary (EUR)'])
    
    # Per-90 min stats
    stats = ['goals', 'assists', 'totalShots', 'keyPasses',
             'tackles', 'interceptions', 'saves', 'clearances']
    for s in stats:
        df[f'{s}_per_90'] = df[s] / (df['minutesPlayed'] / 90)
        
    # One-hot encoding
    df = pd.get_dummies(df, columns=['Position'], prefix='pos', drop_first=True)
    df = pd.get_dummies(df, columns=['Club'], prefix='club', drop_first=True)
    
    features = (
        [f'{s}_per_90' for s in stats]
        + ['Age', 'minutesPlayed', 'rating']
        + [c for c in df.columns if c.startswith('pos_')]
        + [c for c in df.columns if c.startswith('club_')]
    )
    
    # Drop NAs and set up matrices
    df_model = df.dropna(subset=features + ['log_salary']).reset_index(drop=True)
    X = df_model[features] 
    y = df_model['log_salary']
    groups = df_model['Player']
    
    # Create the cross-validation folds here so both models use the exact same splits
    cv = GroupKFold(n_splits=5)

    return df_model, X, y, groups, cv

# Trains a cross-validated Lasso regression model
def train_lasso_model(X, y, groups, cv):
    print("Training Lasso model...")
    model = Pipeline([
        ('scaler', StandardScaler()),
        ('lasso', LassoCV(cv=5, random_state=42, max_iter=10000))
    ])
    lasso_preds = cross_val_predict(model, X, y, cv=cv, groups=groups)

    # Refit on the full dataset to extract feature coefficients
    model.fit(X, y)
    coefs = pd.Series(model.named_steps['lasso'].coef_, index=X.columns)
    top_lasso = coefs.reindex(coefs.abs().sort_values(ascending=False).index).head(10)
    
    print("\n--- Top 10 Features Driving Salary (Lasso) ---")
    print(top_lasso.round(3))
    print("-" * 40)
    
    return lasso_preds

# Trains a cross-validated XGBoost model
def train_xgboost_model(X, y, groups, cv):
    print("Training XGBoost model...")
    xgb = XGBRegressor(
        n_estimators=300,
        max_depth=4,
        learning_rate=0.05,
        random_state=418,
        verbosity=0
    )
    xgb_preds = cross_val_predict(xgb, X, y, cv=cv, groups=groups)

    # Refit on the full dataset to extract tree-based feature importance
    xgb.fit(X, y)
    importances = pd.Series(xgb.feature_importances_, index=X.columns)
    top_xgb = importances.sort_values(ascending=False).head(10)
    
    print("\n--- Top 10 Features Driving Salary (XGBoost) ---")
    print(top_xgb.round(3))
    print("-" * 40)
    
    return xgb_preds

# Evaluates both models side-by-side, picks the winner, and calculates mispricing.
def compare_models_and_evaluate(df_model, y, lasso_preds, xgb_preds):
    print("\n--- Model Showdown Results ---")
    
    # Calculate Metrics
    mae_lasso = mean_absolute_error(y, lasso_preds)
    mae_xgb   = mean_absolute_error(y, xgb_preds)
    r2_lasso  = r2_score(y, lasso_preds)
    r2_xgb    = r2_score(y, xgb_preds)

    print(f"{'Model':<10} {'R²':>8} {'MAE':>8} {'% error':>10}")
    print("-" * 40)
    print(f"{'Lasso':<10} {r2_lasso:>8.3f} {mae_lasso:>8.3f} ±{(np.exp(mae_lasso)-1)*100:>7.1f}%")
    print(f"{'XGBoost':<10} {r2_xgb:>8.3f} {mae_xgb:>8.3f} ±{(np.exp(mae_xgb)-1)*100:>7.1f}%")

    # Store predictions for the plotting function
    df_model['lasso_log_pred'] = lasso_preds
    df_model['xgb_log_pred'] = xgb_preds

    # Pick the Winner
    if mae_xgb < mae_lasso:
        print("\nXGBoost wins! Using XGBoost for final mispricing calculations.")
        final_pred = xgb_preds
    else:
        print("\nLasso wins! Using Lasso for final mispricing calculations.")
        final_pred = lasso_preds

    # Calculate final salary deviations
    df_model['predicted_salary'] = np.expm1(final_pred)
    df_model['pct_deviation']    = (np.exp(y - final_pred) - 1) * 100

    # Positional Accuracy Analysis
    pos_cols = [c for c in df_model.columns if c.startswith('pos_')]
    df_model['Calculated_Position'] = df_model[pos_cols].idxmax(axis=1).str.replace('pos_', '')
    df_model.loc[df_model[pos_cols].sum(axis=1) == 0, 'Calculated_Position'] = 'D'
    
    df_model['abs_residual'] = abs(y - final_pred)
    per_pos = (df_model.groupby('Calculated_Position')['abs_residual']
               .agg(['mean', 'count'])
               .rename(columns={'mean': 'MAE_log', 'count': 'n_players'}))
    per_pos['typical_error_pct'] = (np.exp(per_pos['MAE_log']) - 1) * 100
    
    print("\n--- Per-Position Accuracy (Winning Model) ---")
    print(per_pos.round(2))
    
    return df_model

# Plots a side-by-side comparison of Actual vs Predicted salaries for both models.
def plot_ml_sanity_check(df_model):
    sns.set_theme(style="whitegrid")
    fig, axes = plt.subplots(1, 2, figsize=(16, 7), sharey=True, sharex=True)
    
    y = df_model['log_salary']
    
    # Plot 1: Lasso
    axes[0].scatter(y, df_model['lasso_log_pred'], alpha=0.4, color='#2ab0ff', edgecolor='w', s=60)
    axes[0].plot([y.min(), y.max()], [y.min(), y.max()], 'r--', linewidth=2, label='Perfect prediction')
    axes[0].set_title('Lasso: Predicted vs Actual', fontsize=14, fontweight='bold')
    axes[0].set_xlabel('Actual log(salary)', fontsize=12)
    axes[0].set_ylabel('Predicted log(salary)', fontsize=12)
    axes[0].legend()

    # Plot 2: XGBoost
    axes[1].scatter(y, df_model['xgb_log_pred'], alpha=0.4, color='#ff7f0e', edgecolor='w', s=60)
    axes[1].plot([y.min(), y.max()], [y.min(), y.max()], 'r--', linewidth=2, label='Perfect prediction')
    axes[1].set_title('XGBoost: Predicted vs Actual', fontsize=14, fontweight='bold')
    axes[1].set_xlabel('Actual log(salary)', fontsize=12)
    axes[1].legend()

    plt.suptitle('Sanity Check: Lasso vs. XGBoost', fontsize=18, fontweight='bold')
    plt.tight_layout()
    plt.show()

# Analyzes the final model predictions to identify the most overpaid and underpaid players across the dataset.
def analyze_mispricing(df_model):
    print("\n" + "="*60)
    print("   MISPRICING ANALYSIS: OVERPAID VS UNDERPAID ")
    print("="*60 + "\n")

    # Summarize each player's average actual vs predicted salary
    player_summary = (df_model.groupby('Player')
        .agg(
            Position       = ('Calculated_Position', 'first'),
            seasons        = ('Season', 'count'),
            avg_actual     = ('Salary (EUR)', 'mean'),
            avg_predicted  = ('predicted_salary', 'mean'),
            avg_pct_dev    = ('pct_deviation', 'mean'),
        )
        .reset_index()
    )
    
    # Filter to players with at least 2 seasons of data for reliability
    player_summary = player_summary[player_summary['seasons'] >= 2]
    
    # Formatting
    def fmt_money(x):
        return f"\u20AC{x/1e6:.1f}M"
        
    player_summary['Actual']    = player_summary['avg_actual'].apply(fmt_money)
    player_summary['Predicted'] = player_summary['avg_predicted'].apply(fmt_money)
    player_summary['Deviation'] = player_summary['avg_pct_dev'].apply(lambda x: f"{x:+.0f}%")
    
    # Display top 10 overpaid and underpaid players by position
    display_cols = ['Player', 'Position', 'seasons', 'Actual', 'Predicted', 'Deviation']
    
    # Map the letters to full words for the final report
    position_map = {
        'F': 'FORWARDS',
        'M': 'MIDFIELDERS',
        'D': 'DEFENDERS',
        'K': 'GOALKEEPERS'
    }
    
    for pos_code, pos_name in position_map.items():
        pos_df = player_summary[player_summary['Position'] == pos_code]

        print("=" * 70)
        print(f"  POSITION: {pos_name}")
        print("=" * 70)
        
        print("\nTOP 10 OVERPAID (Actual Salary > Model Prediction):")
        overpaid = pos_df.nlargest(10, 'avg_pct_dev')[display_cols]
        print(overpaid.to_string(index=False))
        
        print("\nTOP 10 UNDERPAID (Actual Salary < Model Prediction):")
        underpaid = pos_df.nsmallest(10, 'avg_pct_dev')[display_cols]
        print(underpaid.to_string(index=False))
        print("\n")
        
    return player_summary