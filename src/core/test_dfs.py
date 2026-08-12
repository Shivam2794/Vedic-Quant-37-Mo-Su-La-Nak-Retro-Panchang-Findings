import sys
sys.path.append(r'C:\Users\Shivam Patel\.gemini\antigravity\scratch\orion_pipeline')
from chapter3_agent8_dfs import XGBoostTreeDFS
import xgboost as xgb
from sklearn.datasets import make_classification

with open('output.txt', 'w') as f:
    f.write('Started\n')
    try:
        X, y = make_classification(n_samples=100, n_features=3, n_informative=3, n_redundant=0, random_state=42)
        dtrain = xgb.DMatrix(X, label=y, feature_names=['A', 'B', 'C'])
        bst = xgb.train({'max_depth': 3, 'eta': 1, 'tree_method': 'exact'}, dtrain, num_boost_round=1)
        f.write('Trained\n')
        mapper = XGBoostTreeDFS(bst)
        interactions = mapper.extract_interactions(min_length=2)
        f.write('Interactions found:\n')
        f.write(str(interactions) + '\n')
    except Exception as e:
        import traceback
        f.write(traceback.format_exc())
