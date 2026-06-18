"""
AI Dataset Analysis - Dual Feature System
Gap Analysis + Comparison Analysis
"""

import streamlit as st
import pandas as pd
from agent import DatasetGapAnalysisAgent
from agent_api import AgentAPI
import json
import os
from claude_integration import ClaudeIntegration

st.set_page_config(
    page_title="AI Dataset Analysis System",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 AI Dataset Analysis System")
st.markdown("Two powerful analysis tools in one platform")

# Sidebar
st.sidebar.header("🎯 Select Analysis Type")
analysis_type = st.sidebar.radio(
    "Choose your analysis:",
    ["Gap Analysis", "Comparison Analysis"],
    help="Gap Analysis: Find structural differences\nComparison Analysis: Compare metrics across periods"
)

st.sidebar.markdown("---")
st.sidebar.header("About")

if analysis_type == "Gap Analysis":
    st.sidebar.info("""
    **Gap Analysis** identifies:
    - Structure mismatches
    - Data quality issues
    - Type incompatibilities
    - Integration blockers
    """)
else:
    st.sidebar.info("""
    **Comparison Analysis** shows:
    - Metric changes (Q1 vs Q2)
    - Performance trends
    - Store/location performance
    - Growth/decline patterns
    """)

st.markdown("---")

# ============================================================================
# FEATURE 1: GAP ANALYSIS
# ============================================================================

if analysis_type == "Gap Analysis":
    st.subheader("📊 Gap Analysis Tool")
    st.markdown("Compare two datasets and identify structural differences and data quality issues")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📁 Upload Dataset 1")
        file1 = st.file_uploader("Choose first CSV file", type="csv", key="gap_file1")
    
    with col2:
        st.subheader("📁 Upload Dataset 2")
        file2 = st.file_uploader("Choose second CSV file", type="csv", key="gap_file2")
    
    if st.button("🔍 Run Gap Analysis", use_container_width=True):
        if file1 is None or file2 is None:
            st.error("❌ Please upload both files")
        else:
            # Save uploaded files temporarily
            with open("temp_1.csv", "wb") as f:
                f.write(file1.getbuffer())
            with open("temp_2.csv", "wb") as f:
                f.write(file2.getbuffer())
            
            st.info("⏳ Analyzing datasets for structural differences...")
            
            # Run analysis
            agent = DatasetGapAnalysisAgent("temp_1.csv", "temp_2.csv")
            results = agent.run()
            
            # Add Claude insights
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if api_key:
                claude = ClaudeIntegration(api_key)
                
                interpretation = claude.interpret_findings(results)
                if interpretation:
                    results['ai_interpretation'] = interpretation
                
                recommendations = claude.generate_recommendations(results)
                if recommendations:
                    results['ai_recommendations'] = recommendations
            
            st.success("✅ Gap Analysis Complete!")
            
            st.markdown("---")
            st.subheader("📊 Analysis Results")
            
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Matching Columns",
                    len(results['structure_comparison'].get('matching_columns', []))
                )
            
            with col2:
                st.metric(
                    "Type Mismatches",
                    len(results['structure_comparison'].get('type_mismatches', []))
                )
            
            with col3:
                st.metric(
                    "Flagged Issues",
                    results['metadata']['total_flags']
                )
            
            with col4:
                st.metric(
                    "Recommendations",
                    len(results['recommendations'])
                )
            
            st.markdown("---")
            
            # Structure comparison
            st.subheader("🏗️ Structure Comparison")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write(f"**Matching Columns:** {len(results['structure_comparison'].get('matching_columns', []))}")
                for col in results['structure_comparison'].get('matching_columns', []):
                    st.caption(f"✓ {col}")
            
            with col2:
                st.write(f"**Only in Dataset 1:** {len(results['structure_comparison'].get('only_in_dataset_1', []))}")
                for col in results['structure_comparison'].get('only_in_dataset_1', []):
                    st.caption(f"• {col}")
            
            with col3:
                st.write(f"**Only in Dataset 2:** {len(results['structure_comparison'].get('only_in_dataset_2', []))}")
                for col in results['structure_comparison'].get('only_in_dataset_2', []):
                    st.caption(f"• {col}")
            
            st.markdown("---")
            
            # Data quality
            st.subheader("📈 Data Quality")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric(
                    "Dataset 1 Duplicates",
                    f"{results['content_analysis'].get('dataset_1_duplicate_percent', 0):.1f}%"
                )
            
            with col2:
                st.metric(
                    "Dataset 2 Duplicates",
                    f"{results['content_analysis'].get('dataset_2_duplicate_percent', 0):.1f}%"
                )
            
            st.markdown("---")
            
            # Flagged issues
            if results['flagged_issues']:
                st.subheader("⚠️ Flagged Issues")
                for issue in results['flagged_issues']:
                    with st.expander(f"🔴 {issue['type']} - {issue['severity']}"):
                        st.write(f"**Column:** {issue.get('column', 'N/A')}")
                        st.write(f"**Detail:** {issue['detail']}")
                        st.write(f"**Action:** {issue['action']}")
            
            st.markdown("---")
            
            # Recommendations
            st.subheader("💡 Recommendations")
            
            for i, rec in enumerate(results['recommendations'], 1):
                st.write(f"**{i}. {rec}**")
            
            # AI insights
            if results.get('ai_interpretation'):
                st.markdown("---")
                st.subheader("🤖 AI Interpretation")
                st.info(results['ai_interpretation'])
            
            if results.get('ai_recommendations'):
                st.markdown("---")
                st.subheader("🤖 AI-Powered Recommendations")
                ai_recs = results['ai_recommendations']
                if isinstance(ai_recs, list):
                    for rec in ai_recs:
                        st.write(f"• {rec}")
                else:
                    st.write(ai_recs)
            
            st.markdown("---")
            
            # Download results
            st.subheader("📥 Download Results")
            
            col1, col2 = st.columns(2)
            
            with col1:
                json_str = json.dumps(results, indent=2)
                st.download_button(
                    label="📄 Download JSON",
                    data=json_str,
                    file_name="gap_analysis_results.json",
                    mime="application/json"
                )
            
            with col2:
                if results['flagged_issues']:
                    csv_data = "Issue Type,Severity,Column,Detail,Action\n"
                    for issue in results['flagged_issues']:
                        csv_data += f"{issue['type']},{issue['severity']},{issue.get('column', 'N/A')},\"{issue['detail']}\",\"{issue['action']}\"\n"
                    
                    st.download_button(
                        label="📊 Download CSV",
                        data=csv_data,
                        file_name="gap_analysis_issues.csv",
                        mime="text/csv"
                    )
            
            # Clean up
            try:
                os.remove("temp_1.csv")
                os.remove("temp_2.csv")
            except:
                pass

# ============================================================================
# FEATURE 2: COMPARISON ANALYSIS
# ============================================================================

else:  # Comparison Analysis
    st.subheader("📈 Comparison Analysis Tool")
    st.markdown("Compare metrics across two periods (Q1 vs Q2, Period 1 vs Period 2, etc.)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Upload Period 1 Data")
        file1 = st.file_uploader("Choose first period CSV", type="csv", key="comp_file1")
    
    with col2:
        st.subheader("📊 Upload Period 2 Data")
        file2 = st.file_uploader("Choose second period CSV", type="csv", key="comp_file2")
    
    if st.button("📊 Run Comparison Analysis", use_container_width=True):
        if file1 is None or file2 is None:
            st.error("❌ Please upload both files")
        else:
            # Save uploaded files temporarily
            with open("temp_p1.csv", "wb") as f:
                f.write(file1.getbuffer())
            with open("temp_p2.csv", "wb") as f:
                f.write(file2.getbuffer())
            
            st.info("⏳ Analyzing period comparison...")
            
            # Load data
            df1 = pd.read_csv("temp_p1.csv")
            df2 = pd.read_csv("temp_p2.csv")
            
            # Find numeric columns for comparison
            numeric_cols_1 = df1.select_dtypes(include=['number']).columns.tolist()
            numeric_cols_2 = df2.select_dtypes(include=['number']).columns.tolist()
            numeric_cols = list(set(numeric_cols_1) & set(numeric_cols_2))
            
            st.success("✅ Comparison Analysis Complete!")
            
            st.markdown("---")
            st.subheader("📊 Period Comparison Results")
            
            # Overall metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Period 1 Rows", len(df1))
            with col2:
                st.metric("Period 2 Rows", len(df2))
            with col3:
                st.metric("Matching Columns", len(numeric_cols))
            
            st.markdown("---")
            
            # Calculate changes
            st.subheader("📈 Metric Changes")
            
            changes = {}
            for col in numeric_cols:
                p1_total = df1[col].sum()
                p2_total = df2[col].sum()
                change_pct = ((p2_total - p1_total) / p1_total * 100) if p1_total != 0 else 0
                changes[col] = {
                    'p1': p1_total,
                    'p2': p2_total,
                    'change': p2_total - p1_total,
                    'change_pct': change_pct
                }
            
            # Display changes in table
            change_data = []
            for col, vals in changes.items():
                change_data.append({
                    'Metric': col,
                    'Period 1': f"${vals['p1']:,.0f}" if vals['p1'] > 1000 else f"{vals['p1']:.0f}",
                    'Period 2': f"${vals['p2']:,.0f}" if vals['p2'] > 1000 else f"{vals['p2']:.0f}",
                    'Change': f"${vals['change']:+,.0f}" if abs(vals['change']) > 1000 else f"{vals['change']:+.0f}",
                    'Growth %': f"{vals['change_pct']:+.1f}%"
                })
            
            st.dataframe(change_data, use_container_width=True)
            
            st.markdown("---")
            
            # Identify key drivers
            st.subheader("🎯 Key Performance Drivers")
            
            sorted_changes = sorted(changes.items(), key=lambda x: x[1]['change_pct'], reverse=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**📈 Top Growth Areas:**")
                for col, vals in sorted_changes[:3]:
                    st.success(f"✓ {col}: {vals['change_pct']:+.1f}%")
            
            with col2:
                st.write("**📉 Areas of Concern:**")
                for col, vals in sorted_changes[-3:]:
                    if vals['change_pct'] < 0:
                        st.warning(f"⚠️ {col}: {vals['change_pct']:+.1f}%")
            
            st.markdown("---")
            
            # If data has location/store column, do store comparison
            location_cols = [col for col in df1.columns if 'location' in col.lower() or 'store' in col.lower()]
            
            if location_cols and len(numeric_cols) > 0:
                st.subheader("🏪 Store/Location Performance Comparison")
                
                location_col = location_cols[0]
                metric_col = numeric_cols[0]  # Use first numeric column
                
                store_comparison = []
                
                for store in df1[location_col].unique():
                    p1_val = df1[df1[location_col] == store][metric_col].sum()
                    p2_val = df2[df2[location_col] == store][metric_col].sum()
                    change_pct = ((p2_val - p1_val) / p1_val * 100) if p1_val != 0 else 0
                    
                    store_comparison.append({
                        'Store': store,
                        'Period 1': f"${p1_val:,.0f}",
                        'Period 2': f"${p2_val:,.0f}",
                        'Growth %': f"{change_pct:+.1f}%"
                    })
                
                st.dataframe(store_comparison, use_container_width=True)
            
            st.markdown("---")
            
            # AI Analysis
            st.subheader("🤖 AI-Powered Analysis")
            
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if api_key:
                claude = ClaudeIntegration(api_key)
                
                # Create analysis prompt
                analysis_text = f"""
                Period 1 Summary:
                {df1.describe().to_string()}
                
                Period 2 Summary:
                {df2.describe().to_string()}
                
                Key Changes:
                {json.dumps(changes, indent=2, default=str)}
                """
                
                prompt = f"""Analyze these period comparisons and provide 5 specific business recommendations:
                
{analysis_text}

Provide actionable insights based on the metric changes."""
                
                response = claude.client.messages.create(
                    model="claude-opus-4-1",
                    max_tokens=800,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                ai_insights = response.content[0].text
                st.info(ai_insights)
            
            st.markdown("---")
            
            # Download results
            st.subheader("📥 Download Results")
            
            # Create summary CSV
            summary_csv = "Metric,Period_1,Period_2,Change,Growth_Percent\n"
            for col, vals in changes.items():
                summary_csv += f"{col},{vals['p1']:.2f},{vals['p2']:.2f},{vals['change']:.2f},{vals['change_pct']:.2f}\n"
            
            st.download_button(
                label="📊 Download Comparison CSV",
                data=summary_csv,
                file_name="period_comparison.csv",
                mime="text/csv"
            )
            
            # Clean up
            try:
                os.remove("temp_p1.csv")
                os.remove("temp_p2.csv")
            except:
                pass

st.markdown("---")
st.markdown("**Built with Python, Claude AI, and Streamlit** 🚀")