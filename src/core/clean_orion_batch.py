import pandas as pd
import os

def clean_dataset():
    dataset_path = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\data_lake\orion_batch_DJIA_PUBLICATION_enriched"
    
    print(f"Loading dataset from: {dataset_path}")
    try:
        df = pd.read_parquet(dataset_path)
        print(f"Original shape: {df.shape}")
        
        has_nans = df.isna().any().any()
        
        if has_nans:
            print("NaNs detected in the dataset. Applying fillna(0) to feature columns...")
            df.fillna(0, inplace=True)
            
            # Verify they are gone
            assert not df.isna().any().any(), "Failed to clear all NaNs!"
            print("All NaNs successfully filled with 0.")
            
            # Save the cleaned dataset
            # To avoid overwriting blindly, saving to a new directory or just overwrite if that's standard
            output_path = dataset_path + "_cleaned"
            df.to_parquet(output_path)
            print(f"Cleaned dataset saved to: {output_path}")
        else:
            print("No NaNs detected in the dataset. It is safe to pass to SAE workers.")
            
    except Exception as e:
        print(f"Failed to process dataset: {e}")

if __name__ == "__main__":
    clean_dataset()
