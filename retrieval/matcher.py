import pandas as pd
from rapidfuzz import process, fuzz
import os
import re

class ViolationMatcher:
    def __init__(self, parquet_name="laws.parquet"):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.parquet_path = os.path.join(base_dir, "..", "data", "processed", parquet_name)
        
        if not os.path.exists(self.parquet_path):
            raise FileNotFoundError(f"Không tìm thấy file dữ liệu tại: {self.parquet_path}")
            
        self.df = pd.read_parquet(self.parquet_path)
        self.unique_violations = self.df[self.df['violation_type'].notna()]['violation_type'].unique().tolist()

    def _normalize(self, text):
        if not text: return ""
        text = str(text).lower()
        text = re.sub(r'[“”"\'«»]', '', text)
        text = re.sub(r'[:;,.]$', '', text)
        return " ".join(text.split())

    def search(self, query_violation, vehicle_type="chung", threshold=75):
        if not query_violation:
            return None

        norm_query = self._normalize(query_violation)

        norm_unique_map = {self._normalize(v): v for v in self.unique_violations}
        norm_list = list(norm_unique_map.keys())

        if norm_query in norm_list:
            original_text = norm_unique_map[norm_query]
            print(f"   [MATCH] Exact match (normalized) for: {original_text[:50]}...")
            exact_results = self.df[self.df['violation_type'] == original_text]
            return self._filter_vehicle(exact_results, vehicle_type)

        best_match = process.extractOne(
            norm_query, 
            norm_list, 
            scorer=fuzz.WRatio
        )
        
        if best_match and best_match[1] >= threshold:
            norm_matched_text = best_match[0]
            original_text = norm_unique_map[norm_matched_text]
            
            print(f"   [MATCH] Fuzzy match ({best_match[1]}%): {original_text[:50]}...")
            
            fuzzy_results = self.df[self.df['violation_type'] == original_text]
            return self._filter_vehicle(fuzzy_results, vehicle_type)
        
        return None

    def _filter_vehicle(self, df_results, vehicle_type):
        if vehicle_type == "chung" or not vehicle_type:
            return df_results.to_dict(orient='records')
            
        filtered = df_results[df_results['vehicle_type'].isin([vehicle_type, 'chung'])]
        
        if filtered.empty:
            return df_results.to_dict(orient='records')
            
        return filtered.to_dict(orient='records')