import pandas as pd

def load_data(filepath):
    """Load CSV or Excel file and return a cleaned DataFrame."""
    
    if filepath.endswith(".csv"):
        df = pd.read_csv(filepath)
    else:
        df = pd.read_excel(filepath)
    
    # Clean the data
    df['date'] = pd.to_datetime(df['date'])
    df['amount'] = df['amount'].abs()          # make sure all amounts are positive
    df['category'] = df['category'].str.strip().str.lower()
    df.dropna(subset=['amount', 'category'], inplace=True)
    
    # Add a month column for grouping later
    df['month'] = df['date'].dt.to_period('M').astype(str)
    
    return df


def get_category_totals(df):
    """Total spending per category, sorted highest first."""
    return df.groupby('category')['amount'].sum().sort_values(ascending=False)


def get_monthly_totals(df):
    """Total spending per month."""
    return df.groupby('month')['amount'].sum()


def get_top_transactions(df, n=5):
    """Return the n most expensive transactions."""
    return df.nlargest(n, 'amount')[['date', 'description', 'amount', 'category']]


def get_budget_analysis(df, budget: dict):
    """
    Compare actual spending vs budget per category.
    budget is a dict like {'food': 3000, 'transport': 1000}
    """
    actuals = get_category_totals(df)
    
    results = []
    for category, limit in budget.items():
        spent = actuals.get(category, 0)
        difference = spent - limit
        status = "over" if difference > 0 else "under"
        results.append({
            'category': category,
            'spent': round(spent, 2),
            'budget': limit,
            'difference': round(abs(difference), 2),
            'status': status
        })
    
    return pd.DataFrame(results)




if __name__ == "__main__":
    df = load_data("data/sample.csv")
    print(df.head())
    print("\nCategory totals:")
    print(get_category_totals(df))
    print("\nMonthly totals:")
    print(get_monthly_totals(df))