import pandas as pd
from mlxtend.frequent_patterns import fpgrowth
from mlxtend.preprocessing import TransactionEncoder

def run_fpgrowth():
    # Toy dataset for demonstration
    dataset = [['Milk', 'Onion', 'Nutmeg', 'Kidney Beans', 'Eggs', 'Yogurt'],
               ['Dill', 'Onion', 'Nutmeg', 'Kidney Beans', 'Eggs', 'Yogurt'],
               ['Milk', 'Apple', 'Kidney Beans', 'Eggs'],
               ['Milk', 'Unicorn', 'Corn', 'Kidney Beans', 'Yogurt'],
               ['Corn', 'Onion', 'Onion', 'Kidney Beans', 'Ice cream', 'Eggs']]

    te = TransactionEncoder()
    te_ary = te.fit(dataset).transform(dataset)
    df = pd.DataFrame(te_ary, columns=te.columns_)

    # Extract frequent itemsets using fpgrowth
    frequent_itemsets = fpgrowth(df, min_support=0.6, use_colnames=True)
    
    print("Frequent Patterns:")
    print(frequent_itemsets)

if __name__ == "__main__":
    run_fpgrowth()
