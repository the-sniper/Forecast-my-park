#!/usr/bin/env python3
"""
Test script for the ML service to verify setup and basic functionality.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from app.config import config
from app.database import db_manager

def test_config():
    """Test configuration loading."""
    print("🔧 Testing Configuration...")
    print(f"  Database URL: {config.database_url}")
    print(f"  Model Directory: {config.MODEL_DIR}")
    print("  ✅ Configuration OK")

def test_database():
    """Test database connection."""
    print("\n💾 Testing Database Connection...")
    try:
        parks = db_manager.get_all_parks()
        print(f"  Found {len(parks)} parks in database")
        
        if parks:
            # Test getting stats for first park
            first_park = parks[0]
            stats = db_manager.get_park_stats(first_park)
            print(f"  Sample park '{first_park}': {stats['total_days']} days of data")
            print("  ✅ Database connection OK")
        else:
            print("  ⚠️ No parks found in database")
            
    except Exception as e:
        print(f"  ❌ Database connection failed: {e}")
        return False
    
    return True

def test_model_training():
    """Test model training on a sample park."""
    print("\n🤖 Testing Model Training...")
    try:
        from app.model_trainer import ParkVisitorPredictor
        
        parks = db_manager.get_all_parks()
        if not parks:
            print("  ⚠️ No parks available for testing")
            return False
            
        # Test with first available park
        test_park = parks[0]
        print(f"  Training model for park: {test_park}")
        
        predictor = ParkVisitorPredictor(test_park)
        metrics = predictor.train()
        
        print(f"  Training completed:")
        print(f"    Training points: {metrics['training_points']}")
        print(f"    MAE: {metrics.get('mae', 'N/A')}")
        print(f"    MAPE: {metrics.get('mape', 'N/A')}")
        
        # Test prediction
        predictions = predictor.predict(7)
        print(f"  Generated {len(predictions)} predictions")
        print("  ✅ Model training and prediction OK")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Model training failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 ML Service Test Suite")
    print("=" * 40)
    
    test_config()
    
    db_ok = test_database()
    if not db_ok:
        print("\n❌ Database tests failed. Check your .env configuration.")
        return
    
    model_ok = test_model_training()
    if not model_ok:
        print("\n❌ Model tests failed. Check dependencies and data.")
        return
    
    print("\n🎉 All tests passed! ML service is ready.")
    print("\nNext steps:")
    print("1. Start the service: python main.py")
    print("2. View API docs: http://localhost:8000/docs")
    print("3. Test prediction: curl http://localhost:8000/health")

if __name__ == "__main__":
    main() 