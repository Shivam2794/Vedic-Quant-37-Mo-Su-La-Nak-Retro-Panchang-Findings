import itertools
from collections import defaultdict
from typing import List, Set, Dict, Any

class AssociationRuleMiner:
    """
    Association Rule Miner using the Apriori algorithm.
    Calculates Overlapping Support, Confidence, and Lift for given transactions.
    """
    def __init__(self, min_support: float = 0.1, min_confidence: float = 0.5):
        self.min_support = min_support
        self.min_confidence = min_confidence
        self.frequent_itemsets = {}
        self.num_transactions = 0

    def fit(self, transactions: List[List[Any]]):
        """Finds frequent itemsets in the transactions database."""
        self.num_transactions = len(transactions)
        transaction_sets = [set(t) for t in transactions]
        
        # Extract 1-itemsets
        item_counts = defaultdict(int)
        for t in transaction_sets:
            for item in t:
                item_counts[frozenset([item])] += 1
                
        # Filter based on min_support
        current_l = {
            itemset: count / self.num_transactions 
            for itemset, count in item_counts.items() 
            if count / self.num_transactions >= self.min_support
        }
        self.frequent_itemsets.update(current_l)
        
        k = 2
        while current_l:
            candidates = self._generate_candidates(list(current_l.keys()), k)
            candidate_counts = defaultdict(int)
            for t in transaction_sets:
                for candidate in candidates:
                    if candidate.issubset(t):
                        candidate_counts[candidate] += 1
                        
            # Filter candidate itemsets based on min_support
            current_l = {
                itemset: count / self.num_transactions 
                for itemset, count in candidate_counts.items() 
                if count / self.num_transactions >= self.min_support
            }
            self.frequent_itemsets.update(current_l)
            k += 1

    def _generate_candidates(self, itemsets: List[frozenset], k: int) -> Set[frozenset]:
        candidates = set()
        for i in range(len(itemsets)):
            for j in range(i + 1, len(itemsets)):
                union_set = itemsets[i].union(itemsets[j])
                if len(union_set) == k:
                    candidates.add(union_set)
        return candidates

    def _get_subsets(self, itemset: frozenset) -> List[frozenset]:
        subsets = []
        itemset_list = list(itemset)
        for i in range(1, len(itemset_list)):
            subsets.extend([frozenset(x) for x in itertools.combinations(itemset_list, i)])
        return subsets

    def generate_rules(self) -> List[Dict[str, Any]]:
        """
        Generates association rules and calculates overlapping support, 
        confidence, and lift metrics.
        Returns a list of rules that meet the minimum confidence threshold.
        """
        rules = []
        for itemset, support in self.frequent_itemsets.items():
            if len(itemset) > 1:
                subsets = self._get_subsets(itemset)
                for antecedent in subsets:
                    consequent = itemset.difference(antecedent)
                    if not consequent:
                        continue
                        
                    antecedent_support = self.frequent_itemsets.get(antecedent, 0)
                    consequent_support = self.frequent_itemsets.get(consequent, 0)
                    
                    if antecedent_support > 0:
                        confidence = support / antecedent_support
                        if confidence >= self.min_confidence:
                            rules.append({
                                'antecedent': set(antecedent),
                                'consequent': set(consequent),
                                'support': support,         # Overlapping Support P(A and B)
                                'confidence': confidence,   # Confidence P(B|A)
                                'lift': confidence / consequent_support if consequent_support > 0 else 0
                            })
        return rules

if __name__ == "__main__":
    # Example usage for testing the miner
    sample_transactions = [
        ['Bread', 'Milk', 'Diaper'],
        ['Bread', 'Milk', 'Beer', 'Eggs'],
        ['Milk', 'Diaper', 'Beer', 'Cola'],
        ['Bread', 'Milk', 'Diaper', 'Beer'],
        ['Bread', 'Milk', 'Diaper', 'Cola']
    ]

    print("Running Association Rule Miner...")
    miner = AssociationRuleMiner(min_support=0.4, min_confidence=0.6)
    miner.fit(sample_transactions)
    rules = miner.generate_rules()

    print(f"Found {len(rules)} rules:")
    print("-" * 40)
    for r in sorted(rules, key=lambda x: x['confidence'], reverse=True):
        print(f"Rule: {r['antecedent']} -> {r['consequent']}")
        print(f"  Overlapping Support: {r['support']:.2f}")
        print(f"  Confidence:          {r['confidence']:.2f}")
        print(f"  Lift:                {r['lift']:.2f}")
        print("-" * 40)
