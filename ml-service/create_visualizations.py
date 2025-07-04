#!/usr/bin/env python3
"""
Enhanced Visualization Generator for Forecast My Park ML Service
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import os
import sys

# Add app to path
sys.path.append('app')
from app.database import db_manager
from app.model_trainer import ParkVisitorPredictor

class EnhancedVisualizer:
    def __init__(self, output_dir="visualizations"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        print(f"📊 Visualizer ready. Output: {output_dir}/")
    
    def create_dataset_overview(self):
        """Create overview of enhanced dataset."""
        print("Creating dataset overview...")
        
        # Get sample data
        parks = db_manager.get_all_parks()[:3]
        data_samples = []
        
        for park in parks:
            park_data = db_manager.get_park_data(park)
            if not park_data.empty:
                park_data['park_id'] = park
                data_samples.append(park_data.sample(min(100, len(park_data))))
        
        if not data_samples:
            print("❌ No data available")
            return None
        
        df = pd.concat(data_samples, ignore_index=True)
        
        # Create 2x2 subplot
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Enhanced Dataset Analysis', fontsize=16, fontweight='bold')
        
        # Plot 1: Visitor trends
        for park in parks:
            park_data = df[df['park_id'] == park]
            if not park_data.empty:
                ax1.plot(park_data['date'], park_data['visitor_count'], 
                        label=park, linewidth=2)
        ax1.set_title('Daily Visitor Trends')
        ax1.set_ylabel('Visitors')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Temperature correlation
        if 'temperature_high' in df.columns:
            ax2.scatter(df['temperature_high'], df['visitor_count'], alpha=0.6)
            correlation = df['temperature_high'].corr(df['visitor_count'])
            ax2.set_title(f'Temperature vs Visitors (r={correlation:.3f})')
            ax2.set_xlabel('Temperature (°F)')
            ax2.set_ylabel('Visitors')
            ax2.grid(True, alpha=0.3)
        
        # Plot 3: Weekend patterns
        if 'is_weekend' in df.columns:
            weekend_data = df[df['is_weekend'] == True]['visitor_count']
            weekday_data = df[df['is_weekend'] == False]['visitor_count']
            ax3.boxplot([weekday_data, weekend_data], labels=['Weekdays', 'Weekends'])
            ax3.set_title('Weekend vs Weekday Patterns')
            ax3.set_ylabel('Visitors')
            ax3.grid(True, alpha=0.3)
        
        # Plot 4: Monthly patterns
        df['month'] = pd.to_datetime(df['date']).dt.month
        monthly_avg = df.groupby('month')['visitor_count'].mean()
        ax4.bar(monthly_avg.index, monthly_avg.values, alpha=0.7)
        ax4.set_title('Monthly Visitor Patterns')
        ax4.set_xlabel('Month')
        ax4.set_ylabel('Average Visitors')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        output_path = os.path.join(self.output_dir, 'dataset_overview.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Overview saved: {output_path}")
        return output_path
    
    def create_predictions_plot(self, park_code='ACAD', days_ahead=14):
        """Create prediction visualization for a specific park."""
        print(f"Creating predictions for {park_code}...")
        
        try:
            # Load or train model
            predictor = ParkVisitorPredictor(park_code)
            model_path = f"models/prophet_model_{park_code}.joblib"
            
            if os.path.exists(model_path):
                predictor.load_model(model_path)
            else:
                print(f"Training model for {park_code}...")
                predictor.train()
                predictor.save_model()
            
            # Generate predictions
            predictions = predictor.predict(days_ahead)
            historical = db_manager.get_park_data(park_code)
            
            # Create plot
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # Plot historical (last 30 days)
            recent_history = historical.tail(30)
            ax.plot(recent_history['date'], recent_history['visitor_count'], 
                   'o-', label='Historical Data', linewidth=2, color='blue')
            
            # Plot predictions
            pred_dates = pd.to_datetime(predictions['ds'])
            ax.plot(pred_dates, predictions['yhat'], 
                   's-', label='Predictions', linewidth=2, color='red', markersize=6)
            
            # Add confidence intervals
            ax.fill_between(pred_dates, predictions['yhat_lower'], predictions['yhat_upper'],
                           alpha=0.3, color='red', label='80% Confidence')
            
            ax.set_title(f'Park {park_code}: Enhanced ML Predictions', fontweight='bold')
            ax.set_ylabel('Daily Visitors')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            output_path = os.path.join(self.output_dir, f'{park_code}_predictions.png')
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"✅ Predictions saved: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ Error creating predictions for {park_code}: {e}")
            return None
    
    def generate_all(self):
        """Generate all visualizations."""
        print("🚀 Generating all visualizations...")
        
        results = []
        
        # Dataset overview
        overview = self.create_dataset_overview()
        if overview:
            results.append(overview)
        
        # Predictions for sample parks
        sample_parks = ['ACAD', 'YELL', 'GRCA']
        for park in sample_parks:
            pred_plot = self.create_predictions_plot(park)
            if pred_plot:
                results.append(pred_plot)
        
        print(f"\n🎉 Generated {len(results)} visualizations:")
        for result in results:
            print(f"  📊 {result}")
        
        return results

def main():
    """Main execution function."""
    print("Enhanced Forecast My Park - Visualization Generator")
    print("=" * 50)
    
    visualizer = EnhancedVisualizer()
    visualizer.generate_all()
    
    print("\n✅ Visualization generation complete!")

if __name__ == "__main__":
    main() 