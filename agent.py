"""
AI Dataset Gap Analysis Agent - PRODUCTION VERSION
"""

import pandas as pd
import json
from datetime import datetime
import os

class DatasetGapAnalysisAgent:
    """Main agent for dataset gap analysis"""
    
    def __init__(self, csv_path_1, csv_path_2):
        self.csv_path_1 = csv_path_1
        self.csv_path_2 = csv_path_2
        self.df1 = None
        self.df2 = None
        self.findings = {}
        
        print(f"\n[AGENT] Initializing...")
        print(f"  Dataset 1: {csv_path_1}")
        print(f"  Dataset 2: {csv_path_2}")
    
    def validate_files(self):
        """Check if files exist"""
        if not os.path.exists(self.csv_path_1):
            return False, f"File not found: {self.csv_path_1}"
        if not os.path.exists(self.csv_path_2):
            return False, f"File not found: {self.csv_path_2}"
        print(f"✓ Both files exist")
        return True, "Files validated"
    
    def step_1_load_data(self):
        """STEP 1: Load CSV files"""
        print("\n[AGENT STEP 1] Loading datasets...")
        
        try:
            self.df1 = pd.read_csv(self.csv_path_1)
        except UnicodeDecodeError:
            self.df1 = pd.read_csv(self.csv_path_1, encoding='latin-1')
        except Exception as e:
            return False, f"Error loading {self.csv_path_1}: {str(e)}"
        
        try:
            self.df2 = pd.read_csv(self.csv_path_2)
        except UnicodeDecodeError:
            self.df2 = pd.read_csv(self.csv_path_2, encoding='latin-1')
        except Exception as e:
            return False, f"Error loading {self.csv_path_2}: {str(e)}"
        
        print(f"✓ Dataset 1: {self.df1.shape[0]} rows, {self.df1.shape[1]} columns")
        print(f"✓ Dataset 2: {self.df2.shape[0]} rows, {self.df2.shape[1]} columns")
        
        return True, "Data loaded successfully"
    
    def step_2_compare_structure(self):
        """STEP 2: Compare column names and types"""
        print("\n[AGENT STEP 2] Comparing structure...")
        
        cols1 = set(self.df1.columns)
        cols2 = set(self.df2.columns)
        
        matching = cols1.intersection(cols2)
        only_in_1 = cols1 - cols2
        only_in_2 = cols2 - cols1
        
        print(f"✓ Matching columns: {len(matching)}")
        print(f"✓ Only in Dataset 1: {len(only_in_1)}")
        print(f"✓ Only in Dataset 2: {len(only_in_2)}")
        
        # Check type mismatches
        type_mismatches = []
        for col in matching:
            type1 = str(self.df1[col].dtype)
            type2 = str(self.df2[col].dtype)
            if type1 != type2:
                type_mismatches.append({
                    'column': col,
                    'dataset_1_type': type1,
                    'dataset_2_type': type2
                })
                print(f"⚠️  Type mismatch in '{col}': {type1} vs {type2}")
        
        self.findings['structure'] = {
            'matching_columns': list(matching),
            'only_in_dataset_1': list(only_in_1),
            'only_in_dataset_2': list(only_in_2),
            'type_mismatches': type_mismatches
        }
        
        return True, "Structure comparison complete"
    
    def step_3_compare_content(self):
        """STEP 3: Analyze data quality"""
        print("\n[AGENT STEP 3] Analyzing data quality...")
        
        # Missing data percentages
        gaps_1 = (self.df1.isnull().sum() / len(self.df1) * 100).to_dict()
        gaps_2 = (self.df2.isnull().sum() / len(self.df2) * 100).to_dict()
        
        # Duplicates
        dups_1 = int(self.df1.duplicated().sum())
        dups_2 = int(self.df2.duplicated().sum())
        dups_1_pct = (dups_1 / len(self.df1) * 100) if len(self.df1) > 0 else 0
        dups_2_pct = (dups_2 / len(self.df2) * 100) if len(self.df2) > 0 else 0
        
        print(f"✓ Dataset 1 duplicates: {dups_1} ({dups_1_pct:.1f}%)")
        print(f"✓ Dataset 2 duplicates: {dups_2} ({dups_2_pct:.1f}%)")
        
        # Find significant gaps (> 15%)
        significant_gaps = []
        gap_threshold = 15
        
        for col in gaps_1:
            if gaps_1[col] > gap_threshold:
                significant_gaps.append({
                    'column': col,
                    'dataset': 'dataset_1',
                    'missing_percent': round(gaps_1[col], 1)
                })
                print(f"⚠️  Dataset 1: '{col}' has {gaps_1[col]:.1f}% missing (SIGNIFICANT)")
        
        for col in gaps_2:
            if gaps_2[col] > gap_threshold:
                significant_gaps.append({
                    'column': col,
                    'dataset': 'dataset_2',
                    'missing_percent': round(gaps_2[col], 1)
                })
                print(f"⚠️  Dataset 2: '{col}' has {gaps_2[col]:.1f}% missing (SIGNIFICANT)")
        
        self.findings['content'] = {
            'dataset_1_gaps_percent': {k: round(v, 1) for k, v in gaps_1.items()},
            'dataset_2_gaps_percent': {k: round(v, 1) for k, v in gaps_2.items()},
            'dataset_1_duplicates': dups_1,
            'dataset_1_duplicate_percent': round(dups_1_pct, 1),
            'dataset_2_duplicates': dups_2,
            'dataset_2_duplicate_percent': round(dups_2_pct, 1),
            'significant_gaps': significant_gaps
        }
        
        return True, "Content analysis complete"
    
    def step_4_apply_rules(self):
        """STEP 4: Apply significance thresholds"""
        print("\n[AGENT STEP 4] Applying significance rules...")
        
        flags = []
        
        # Rule 1: Type mismatches
        for mismatch in self.findings['structure']['type_mismatches']:
            flags.append({
                'type': 'TYPE_MISMATCH',
                'severity': 'HIGH',
                'column': mismatch['column'],
                'detail': f"Type mismatch: {mismatch['dataset_1_type']} vs {mismatch['dataset_2_type']}",
                'action': 'Standardize column types before merge'
            })
        
        # Rule 2: Data gaps
        for gap in self.findings['content']['significant_gaps']:
            flags.append({
                'type': 'DATA_GAP',
                'severity': 'HIGH',
                'column': gap['column'],
                'dataset': gap['dataset'],
                'detail': f"Column '{gap['column']}' has {gap['missing_percent']}% missing data",
                'action': 'Investigate source system'
            })
        
        # Rule 3: Duplicates
        if self.findings['content']['dataset_1_duplicate_percent'] > 5:
            flags.append({
                'type': 'DUPLICATES',
                'severity': 'MEDIUM',
                'detail': f"Dataset 1 has {self.findings['content']['dataset_1_duplicate_percent']}% duplicate rows",
                'action': 'Remove duplicates before analysis'
            })
        
        if self.findings['content']['dataset_2_duplicate_percent'] > 5:
            flags.append({
                'type': 'DUPLICATES',
                'severity': 'MEDIUM',
                'detail': f"Dataset 2 has {self.findings['content']['dataset_2_duplicate_percent']}% duplicate rows",
                'action': 'Remove duplicates before analysis'
            })
        
        print(f"✓ Found {len(flags)} flagged issues")
        
        self.findings['flags'] = flags
        return True, "Rules applied"
    
    def step_5_generate_recommendations(self):
        """STEP 5: Generate recommendations"""
        print("\n[AGENT STEP 5] Generating recommendations...")
        
        recommendations = []
        
        if self.findings['structure']['type_mismatches']:
            recommendations.append(
                "STANDARDIZE COLUMN TYPES: Type mismatches detected. Convert columns to same types before merging."
            )
        
        if self.findings['content']['significant_gaps']:
            recommendations.append(
                "INVESTIGATE MISSING DATA: Significant gaps detected. Contact source system owners."
            )
        
        if (self.findings['content']['dataset_1_duplicate_percent'] > 5 or 
            self.findings['content']['dataset_2_duplicate_percent'] > 5):
            recommendations.append(
                "REMOVE DUPLICATES: Duplicate rows detected. Remove before analysis."
            )
        
        if self.findings['structure']['only_in_dataset_2']:
            recommendations.append(
                f"ALIGN COLUMNS: Dataset 2 has unique columns. Decide if needed in merge."
            )
        
        recommendations.append(
            "VALIDATION: After addressing issues, re-run analysis to confirm resolution."
        )
        
        print(f"✓ Generated {len(recommendations)} recommendations")
        
        self.findings['recommendations'] = recommendations
        return True, "Recommendations generated"
    
    def to_json(self):
        """Convert findings to JSON"""
        output = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'status': 'ANALYSIS_COMPLETE',
                'dataset_1': os.path.basename(self.csv_path_1),
                'dataset_2': os.path.basename(self.csv_path_2),
                'total_flags': len(self.findings.get('flags', []))
            },
            'structure_comparison': self.findings.get('structure', {}),
            'content_analysis': self.findings.get('content', {}),
            'flagged_issues': self.findings.get('flags', []),
            'recommendations': self.findings.get('recommendations', [])
        }
        return output
    
    def run(self):
        """Execute full analysis"""
        print("\n" + "="*70)
        print("AI DATASET GAP ANALYSIS AGENT")
        print("="*70)
        
        valid, msg = self.validate_files()
        if not valid:
            print(f"✗ {msg}")
            return {'status': 'FAILED', 'error': msg}
        
        self.step_1_load_data()
        self.step_2_compare_structure()
        self.step_3_compare_content()
        self.step_4_apply_rules()
        self.step_5_generate_recommendations()
        
        print("\n" + "="*70)
        print("ANALYSIS COMPLETE")
        print("="*70)
        
        return self.to_json()


# Main
if __name__ == "__main__":
    import sys
    import os
    from claude_integration import ClaudeIntegration
    
    if len(sys.argv) != 3:
        print("\nUsage: python agent.py <dataset_1.csv> <dataset_2.csv>")
        sys.exit(1)
    
    csv_1 = sys.argv[1]
    csv_2 = sys.argv[2]
    
    agent = DatasetGapAnalysisAgent(csv_1, csv_2)
    results = agent.run()
    
    # Add Claude AI insights
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if api_key:
        print("\n" + "="*70)
        print("[CLAUDE] Adding AI-powered insights...")
        print("="*70)
        
        claude = ClaudeIntegration(api_key)
        
        # Get AI interpretation
        interpretation = claude.interpret_findings(results)
        if interpretation:
            results['ai_interpretation'] = interpretation
        
        # Get AI recommendations
        recommendations = claude.generate_recommendations(results)
        if recommendations:
            results['ai_recommendations'] = recommendations
    else:
        print("\n[WARNING] ANTHROPIC_API_KEY not set. Skipping Claude AI insights.")
        results['ai_interpretation'] = None
        results['ai_recommendations'] = None
    
    # Save results
    print("\n[OUTPUT] Saving results...")
    with open('analysis_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    print("✓ Results saved to: analysis_results.json")
    
    print(f"\n[SUMMARY]")
    print(f"  Matching columns: {len(results['structure_comparison'].get('matching_columns', []))}")
    print(f"  Flagged issues: {results['metadata']['total_flags']}")
    print(f"  Recommendations: {len(results['recommendations'])}")
    if results.get('ai_interpretation'):
        print(f"  AI Interpretation: Generated ✓")
    if results.get('ai_recommendations'):
        print(f"  AI Recommendations: Generated ✓")