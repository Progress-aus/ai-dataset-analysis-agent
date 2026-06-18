"""
Agent API Wrapper
Simple interface for Streamlit to call the agent
"""

import json
from agent import DatasetGapAnalysisAgent

class AgentAPI:
    """API wrapper around the agent"""
    
    @staticmethod
    def analyze_datasets(csv_path_1, csv_path_2):
        """
        Main entry point for Streamlit
        
        Args:
            csv_path_1: Path to first CSV
            csv_path_2: Path to second CSV
        
        Returns:
            dict: {'status': 'SUCCESS'/'ERROR', 'data': results}
        """
        try:
            print("[API] Analyzing datasets...")
            agent = DatasetGapAnalysisAgent(csv_path_1, csv_path_2)
            results = agent.run()
            
            return {
                'status': 'SUCCESS',
                'data': results
            }
        except Exception as e:
            print(f"[API] Error: {str(e)}")
            return {
                'status': 'ERROR',
                'error': str(e)
            }
    
    @staticmethod
    def format_for_display(results):
        """
        Format JSON results for nice display
        
        Args:
            results: Output from analyze_datasets
        
        Returns:
            dict: Formatted for Streamlit
        """
        if results['status'] != 'SUCCESS':
            return None
        
        data = results['data']
        
        return {
            'summary': {
                'matching_columns': len(data['structure_comparison'].get('matching_columns', [])),
                'type_mismatches': len(data['structure_comparison'].get('type_mismatches', [])),
                'total_flags': data['metadata']['total_flags'],
                'total_recommendations': len(data['recommendations'])
            },
            'structure': data['structure_comparison'],
            'content': data['content_analysis'],
            'issues': data['flagged_issues'],
            'recommendations': data['recommendations'],
            'timestamp': data['metadata']['timestamp']
        }
    
    @staticmethod
    def get_summary(results):
        """Get quick 1-line summary"""
        if results['status'] != 'SUCCESS':
            return "Analysis failed"
        
        data = results['data']
        flags = data['metadata']['total_flags']
        
        if flags == 0:
            return "✓ Datasets are compatible (no issues found)"
        elif flags <= 3:
            return f"⚠️  {flags} issues found (minor)"
        else:
            return f"⚠️⚠️ {flags} issues found (significant)"
    
    @staticmethod
    def export_csv(results, filename='analysis_summary.csv'):
        """
        Export findings to CSV for Excel users
        
        Args:
            results: Output from analyze_datasets
            filename: Where to save CSV
        """
        if results['status'] != 'SUCCESS':
            return False
        
        data = results['data']
        
        # Create CSV content
        csv_content = "Issue Type,Severity,Column,Detail,Action\n"
        
        for issue in data['flagged_issues']:
            csv_content += f"{issue['type']},{issue['severity']},{issue.get('column', 'N/A')},\"{issue['detail']}\",\"{issue['action']}\"\n"
        
        # Write to file
        with open(filename, 'w') as f:
            f.write(csv_content)
        
        print(f"[API] Results exported to {filename}")
        return True
    
    @staticmethod
    def save_results(results, filename='analysis_results.json'):
        """Save full results to JSON"""
        if results['status'] != 'SUCCESS':
            return False
        
        with open(filename, 'w') as f:
            json.dump(results['data'], f, indent=2)
        
        print(f"[API] Results saved to {filename}")
        return True


def test_api():
    """Test the API"""
    print("\n[TEST] Testing Agent API...")
    
    # Test with sample data
    results = AgentAPI.analyze_datasets('data/sample_1.csv', 'data/sample_2.csv')
    
    if results['status'] == 'SUCCESS':
        print("[TEST] ✓ API working!")
        
        # Test formatting
        formatted = AgentAPI.format_for_display(results)
        print(f"\nSummary:")
        print(f"  Matching columns: {formatted['summary']['matching_columns']}")
        print(f"  Type mismatches: {formatted['summary']['type_mismatches']}")
        print(f"  Flagged issues: {formatted['summary']['total_flags']}")
        print(f"  Recommendations: {formatted['summary']['total_recommendations']}")
        
        # Test summary
        summary = AgentAPI.get_summary(results)
        print(f"\nQuick summary: {summary}")
        
        # Export CSV
        AgentAPI.export_csv(results)
        
        # Save JSON
        AgentAPI.save_results(results)
        
        return True
    else:
        print(f"[TEST] ✗ API failed: {results['error']}")
        return False


if __name__ == "__main__":
    test_api()