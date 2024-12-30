import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# import seaborn as sns
# from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import List, Dict, Any
from src.sentiment.base_analyzer import SentimentResult

class SentimentVisualizer:
    def __init__(self):
        self.colors = {
            'Extreme Fear': '#FF4136',
            'Fear': '#FF851B',
            'Neutral': '#FFDC00',
            'Greed': '#2ECC40',
            'Extreme Greed': '#01FF70'
        }
    
    def create_radar_chart(self, results: List[tuple[str, SentimentResult]]) -> go.Figure:
        """Create a radar chart comparing all sentiment sources"""
        categories = [name for name, _ in results]
        values = [result.value for _, result in results]
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='Current Sentiment'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[-1, 1]
                )),
            showlegend=False,
            title="Sentiment Radar Chart"
        )
        return fig
    
    def create_gauge_chart(self, aggregate_result: SentimentResult) -> go.Figure:
        """Create a gauge chart for the aggregate sentiment"""
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=(aggregate_result.value + 1) * 50,  # Convert from [-1,1] to [0,100]
            title={'text': f"Aggregate Sentiment: {aggregate_result.classification}"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': self.colors.get(aggregate_result.classification, '#FFFFFF')},
                'steps': [
                    {'range': [0, 20], 'color': self.colors['Extreme Fear']},
                    {'range': [20, 40], 'color': self.colors['Fear']},
                    {'range': [40, 60], 'color': self.colors['Neutral']},
                    {'range': [60, 80], 'color': self.colors['Greed']},
                    {'range': [80, 100], 'color': self.colors['Extreme Greed']}
                ]
            }
        ))
        return fig
    
    def create_correlation_heatmap(self, historical_data: List[Dict[str, Any]]) -> go.Figure:
        """Create a correlation heatmap between different sentiment sources"""
        # Convert historical data to DataFrame
        df = pd.DataFrame(historical_data)
        
        # Calculate correlation matrix
        corr_matrix = df[['fear_greed_value', 'reddit_value', 
                         'cointelegraph_value', 'cryptoslate_value']].corr()
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdYlGn',
            zmin=-1,
            zmax=1
        ))
        
        fig.update_layout(
            title="Sentiment Source Correlation Heatmap",
            xaxis_title="Source",
            yaxis_title="Source"
        )
        return fig
    
    def create_time_series(self, historical_data: List[Dict[str, Any]]) -> go.Figure:
        """Create time series plot of all sentiment sources"""
        df = pd.DataFrame(historical_data)
        
        fig = make_subplots(rows=2, cols=1,
                           subplot_titles=("Individual Sentiment Sources", "Aggregate Sentiment"))
        
        # Individual sources
        for col in ['fear_greed_value', 'reddit_value', 'cointelegraph_value', 'cryptoslate_value']:
            fig.add_trace(
                go.Scatter(x=df['timestamp'], y=df[col], name=col.replace('_value', '')),
                row=1, col=1
            )
        
        # Aggregate sentiment
        fig.add_trace(
            go.Scatter(x=df['timestamp'], y=df['aggregate_value'], 
                      name='aggregate', line=dict(width=3)),
            row=2, col=1
        )
        
        fig.update_layout(
            height=800,
            title_text="Sentiment Time Series Analysis",
            showlegend=True
        )
        return fig
    
    def create_source_contribution(self, results: List[tuple[str, SentimentResult]]) -> go.Figure:
        """Create a waterfall chart showing how each source contributes to the final sentiment"""
        names = [name for name, _ in results]
        values = [result.value for _, result in results]
        
        fig = go.Figure(go.Waterfall(
            name="Sentiment Contribution",
            orientation="v",
            measure=["relative"] * len(values) + ["total"],
            x=names + ["Aggregate"],
            y=values + [sum(values)/len(values)],
            connector={"line": {"color": "rgb(63, 63, 63)"}},
        ))
        
        fig.update_layout(
            title="Source Contribution to Aggregate Sentiment",
            showlegend=True,
            xaxis_title="Source",
            yaxis_title="Sentiment Value"
        )
        return fig

def save_analysis_report(results: List[tuple[str, SentimentResult]], 
                        aggregate_result: SentimentResult,
                        historical_data: List[Dict[str, Any]] = None):
    """Generate and save a complete analysis report"""
    visualizer = SentimentVisualizer()
    
    # Create all charts
    radar = visualizer.create_radar_chart(results)
    gauge = visualizer.create_gauge_chart(aggregate_result)
    contribution = visualizer.create_source_contribution(results)
    
    # Save charts
    radar.write_html("sentiment_radar.html")
    gauge.write_html("sentiment_gauge.html")
    contribution.write_html("sentiment_contribution.html")
    
    if historical_data:
        heatmap = visualizer.create_correlation_heatmap(historical_data)
        timeseries = visualizer.create_time_series(historical_data)
        heatmap.write_html("sentiment_correlation.html")
        timeseries.write_html("sentiment_timeseries.html")
        
    # Generate text report
    with open("sentiment_analysis_report.txt", "w") as f:
        f.write("Sentiment Analysis Report\n")
        f.write("=" * 50 + "\n\n")
        
        f.write("Current Sentiment Analysis:\n")
        f.write("-" * 30 + "\n")
        for name, result in results:
            f.write(f"\n{name}:\n")
            f.write(f"Value: {result.value:.2f}\n")
            f.write(f"Classification: {result.classification}\n")
            if result.raw_data.get('items_analyzed'):
                f.write(f"Items Analyzed: {result.raw_data['items_analyzed']}\n")
        
        f.write("\nAggregate Sentiment:\n")
        f.write("-" * 30 + "\n")
        f.write(f"Value: {aggregate_result.value:.2f}\n")
        f.write(f"Classification: {aggregate_result.classification}\n")
        
        if historical_data:
            f.write("\nHistorical Analysis:\n")
            f.write("-" * 30 + "\n")
            df = pd.DataFrame(historical_data)
            f.write("\nCorrelation Analysis:\n")
            f.write(df[['fear_greed_value', 'reddit_value', 
                       'cointelegraph_value', 'cryptoslate_value']].corr().to_string())
