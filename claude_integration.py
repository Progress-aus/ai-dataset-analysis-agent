"""
Claude API Integration for Dataset Gap Analysis
"""

import os
from anthropic import Anthropic

class ClaudeIntegration:
    """Wrapper for Claude API calls"""
    
    def __init__(self, api_key):
        """Initialize Claude client with API key"""
        self.client = Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-6"
        print("[CLAUDE] ✓ Initialized with API key")
    
    def interpret_findings(self, findings_dict):
        """Send findings to Claude for interpretation"""
        print("\n[CLAUDE] Sending findings for AI interpretation...")
        
        structure = findings_dict.get('structure_comparison', {})
        content = findings_dict.get('content_analysis', {})
        
        prompt = f"""You are a Data Quality Expert. Analyze these dataset comparison findings:

STRUCTURE:
- Matching columns: {len(structure.get('matching_columns', []))}
- Only in Dataset 1: {len(structure.get('only_in_dataset_1', []))}
- Only in Dataset 2: {len(structure.get('only_in_dataset_2', []))}
- Type mismatches: {len(structure.get('type_mismatches', []))}

CONTENT:
- Dataset 1 duplicates: {content.get('dataset_1_duplicate_percent', 0):.1f}%
- Dataset 2 duplicates: {content.get('dataset_2_duplicate_percent', 0):.1f}%
- Data gaps >15%: {len(content.get('significant_gaps', []))}

Provide a brief interpretation (2-3 sentences) of what these findings mean for data quality."""
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )
            
            result = response.content[0].text
            print("[CLAUDE] ✓ AI interpretation received")
            return result
            
        except Exception as e:
            print(f"[CLAUDE] ✗ Error: {str(e)}")
            return None
    
    def generate_recommendations(self, findings_dict):
        """Generate business recommendations"""
        print("\n[CLAUDE] Generating AI-powered recommendations...")
        
        structure = findings_dict.get('structure_comparison', {})
        content = findings_dict.get('content_analysis', {})
        
        matching_cols = len(structure.get('matching_columns', []))
        type_mismatches = len(structure.get('type_mismatches', []))
        sig_gaps = len(content.get('significant_gaps', []))
        
        prompt = f"""You are a Data Quality Expert. Based on these findings:
- Matching columns: {matching_cols}
- Type mismatches: {type_mismatches}
- Data gaps: {sig_gaps}

Provide 3-5 specific business recommendations to improve data quality. Format as numbered list."""
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            result = response.content[0].text
            print("[CLAUDE] ✓ AI recommendations generated")
            return result
            
        except Exception as e:
            print(f"[CLAUDE] ✗ Error: {str(e)}")
            return None


def test_claude_api(api_key):
    """Test if Claude API is working"""
    print("\n" + "="*70)
    print("[TEST] Testing Claude API Connection")
    print("="*70)
    
    integration = ClaudeIntegration(api_key)
    
    test_findings = {
        'structure_comparison': {
            'matching_columns': ['Brand_Name'],
            'only_in_dataset_1': ['Category', 'Country', 'Price_AUD', 'Volume_ml', 'Rating', 'Alcohol_Percentage'],
            'only_in_dataset_2': ['Year', 'Region', 'Units_000s', 'Revenue_AUD_Million', 'Market_Share_Percent', 'Customer_Age_Group'],
            'type_mismatches': []
        },
        'content_analysis': {
            'dataset_1_duplicate_percent': 0,
            'dataset_2_duplicate_percent': 0,
            'significant_gaps': []
        }
    }
    
    print("\n1. Testing interpretation...")
    interpretation = integration.interpret_findings(test_findings)
    
    if interpretation:
        print(f"\nInterpretation:\n{interpretation}")
        
        print("\n2. Testing recommendations...")
        recommendations = integration.generate_recommendations(test_findings)
        
        if recommendations:
            print(f"\nRecommendations:\n{recommendations}")
            print("\n[TEST] ✓✓✓ Claude API is WORKING!!!")
            return True
    
    print("\n[TEST] ✗ Claude API failed")
    return False


if __name__ == "__main__":
    api_key = os.getenv('ANTHROPIC_API_KEY')
    
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set")
        exit(1)
    
    test_claude_api(api_key)