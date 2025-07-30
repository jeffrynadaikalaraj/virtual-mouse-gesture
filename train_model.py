#!/usr/bin/env python3
"""
Train SVM model for gesture recognition
Based on the existing Jupyter notebook code
"""

import pandas as pd
import numpy as np
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

def check_dataset():
    """Check if the dataset exists"""
    if not os.path.exists("gesture_data_svm.csv"):
        print("❌ Dataset 'gesture_data_svm.csv' not found!")
        print("📋 Please ensure you have the gesture dataset in the current directory.")
        print("\n🔧 If you don't have the dataset, you can:")
        print("1. Create synthetic data for testing")
        print("2. Collect real gesture data using MediaPipe")
        print("3. Download a hand gesture dataset from Kaggle or similar sources")
        return False
    return True

def create_synthetic_dataset():
    """Create a synthetic dataset for testing purposes"""
    print("🎲 Creating synthetic gesture dataset for testing...")
    
    # Create synthetic features (simulating MediaPipe landmarks)
    np.random.seed(42)
    n_samples = 1200
    n_features = 42  # 21 landmarks * 2 coordinates (x, y) - simplified
    
    # Define gesture classes
    gestures = ['Move Cursor', 'Left Click', 'Right Click', 'Screenshot', 'Dragging', 'Idle']
    samples_per_class = n_samples // len(gestures)
    
    data = []
    labels = []
    
    for i, gesture in enumerate(gestures):
        # Create distinct feature patterns for each gesture
        base_pattern = np.random.normal(i * 0.5, 0.2, n_features)
        
        for _ in range(samples_per_class):
            # Add noise to create variations
            sample = base_pattern + np.random.normal(0, 0.1, n_features)
            data.append(sample)
            labels.append(gesture)
    
    # Create DataFrame
    feature_columns = [f'feature_{i}' for i in range(n_features)]
    df = pd.DataFrame(data, columns=feature_columns)
    df['label'] = labels
    
    # Shuffle the dataset
    df = df.sample(frac=1).reset_index(drop=True)
    
    # Save the dataset
    df.to_csv('gesture_data_svm.csv', index=False)
    print(f"✅ Synthetic dataset created with {len(df)} samples and {len(gestures)} gesture classes")
    return True

def load_and_preprocess_data():
    """Load and preprocess the gesture dataset"""
    print("📊 Loading gesture dataset...")
    
    # Load data
    df = pd.read_csv("gesture_data_svm.csv")
    print(f"Dataset shape: {df.shape}")
    
    # Check for missing values
    if df.isnull().sum().any():
        print("⚠️ Found missing values, cleaning...")
        df = df.dropna()
    
    # Display basic info
    print(f"Features: {df.shape[1] - 1}")
    print(f"Samples: {df.shape[0]}")
    print(f"Classes: {df['label'].nunique()}")
    print(f"Class distribution:\n{df['label'].value_counts()}")
    
    return df

def train_svm_model(df):
    """Train the SVM model"""
    print("\n🤖 Training SVM model...")
    
    # Separate features and labels
    X = df.drop("label", axis=1)
    y = df["label"]
    
    # Encode labels
    encoder = LabelEncoder()
    y_encoded = encoder.fit_transform(y)
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )
    
    print(f"Training samples: {X_train.shape[0]}")
    print(f"Testing samples: {X_test.shape[0]}")
    
    # Train SVM model with different kernels and find the best one
    kernels = ['rbf', 'linear', 'poly']
    best_accuracy = 0
    best_model = None
    best_kernel = None
    
    for kernel in kernels:
        print(f"\n🔄 Testing {kernel} kernel...")
        if kernel == 'rbf':
            model = SVC(kernel=kernel, C=10, gamma=0.1, random_state=42)
        elif kernel == 'poly':
            model = SVC(kernel=kernel, C=1, degree=3, random_state=42)
        else:
            model = SVC(kernel=kernel, C=1, random_state=42)
        
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"{kernel} kernel accuracy: {accuracy:.4f}")
        
        if accuracy > best_accuracy:
            best_accuracy = accuracy
            best_model = model
            best_kernel = kernel
    
    print(f"\n🎯 Best model: {best_kernel} kernel with accuracy: {best_accuracy:.4f}")
    
    # Final predictions for evaluation
    y_pred = best_model.predict(X_test)
    
    # Print detailed classification report
    print("\n📈 Classification Report:")
    target_names = encoder.classes_
    print(classification_report(y_test, y_pred, target_names=target_names))
    
    return best_model, scaler, encoder, X_test, y_test, y_pred, target_names

def save_models(model, scaler, encoder):
    """Save the trained model and preprocessing objects"""
    print("\n💾 Saving models...")
    
    # Create models directory
    os.makedirs("models", exist_ok=True)
    
    # Save model and preprocessing objects
    joblib.dump(model, "models/gesture_svm_model.pkl")
    joblib.dump(scaler, "models/gesture_scaler.pkl")
    joblib.dump(encoder, "models/gesture_label_encoder.pkl")
    
    print("✅ Models saved successfully!")
    print("   - models/gesture_svm_model.pkl")
    print("   - models/gesture_scaler.pkl")
    print("   - models/gesture_label_encoder.pkl")

def create_confusion_matrix(y_test, y_pred, target_names):
    """Create and save confusion matrix visualization"""
    print("\n📊 Creating confusion matrix...")
    
    # Compute confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    
    # Create visualization
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=target_names, yticklabels=target_names)
    plt.title('Gesture Recognition Confusion Matrix', fontsize=16, fontweight='bold')
    plt.xlabel('Predicted Label', fontsize=12)
    plt.ylabel('True Label', fontsize=12)
    plt.xticks(rotation=45)
    plt.yticks(rotation=0)
    plt.tight_layout()
    
    # Save the plot
    plt.savefig('confusion_matrix_svm.png', dpi=300, bbox_inches='tight')
    print("✅ Confusion matrix saved as 'confusion_matrix_svm.png'")
    
    # Show accuracy per class
    accuracy_per_class = cm.diagonal() / cm.sum(axis=1)
    print("\n📊 Accuracy per class:")
    for i, acc in enumerate(accuracy_per_class):
        print(f"   {target_names[i]}: {acc:.4f}")

def main():
    """Main training function"""
    print("🖐️ Hand Gesture Recognition - Model Training")
    print("=" * 50)
    
    # Check if dataset exists, create synthetic if not
    if not check_dataset():
        create_synthetic = input("\n❓ Create synthetic dataset for testing? (y/n): ").lower().strip()
        if create_synthetic == 'y':
            if not create_synthetic_dataset():
                return
        else:
            print("❌ Cannot proceed without dataset. Exiting...")
            return
    
    try:
        # Load and preprocess data
        df = load_and_preprocess_data()
        
        # Train model
        model, scaler, encoder, X_test, y_test, y_pred, target_names = train_svm_model(df)
        
        # Save models
        save_models(model, scaler, encoder)
        
        # Create visualization
        create_confusion_matrix(y_test, y_pred, target_names)
        
        print("\n🎉 Training completed successfully!")
        print("🚀 You can now run the Flask app with: python app.py")
        
    except Exception as e:
        print(f"\n❌ Error during training: {str(e)}")
        print("Please check your dataset and try again.")

if __name__ == "__main__":
    main()