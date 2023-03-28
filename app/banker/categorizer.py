import pandas as pd


categories = {
    'grocery': [
        'wm supercenter',
        'harris teeter',
        'food lion',
        'walgreens',
        'costco whse',
    ],
    'gas': [
        'costco gas',
    ],
    'entertainment': [
        'sq *',
        'tst*',
        'm pocha',
        'sushi',
        'gizmo',
        'top polish nails',
        'cook out'
    ],
    'home': [
        'home depot'
    ]
}


def apply_category(trans_df: pd.DataFrame) -> pd.DataFrame:
    trans_df['category'] = trans_df['description'].apply(categorize_transaction)
    return trans_df


def categorize_transaction(transaction):
    category = get_category(categories, transaction)
    return category


def get_category(categories, value: str) -> str:
    out_val = [cat for cat in categories if any(val in value for val in categories[cat])]
    if not out_val:
        return 'uncategorized'
    else:
        return out_val[0]