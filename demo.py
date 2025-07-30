#!/usr/bin/env python3
"""
Demo script for Gesture Recognition Hackathon Project
Automates setup, training, and running the application
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def print_banner():
    """Print project banner"""
    banner = """
🖐️  AI GESTURE RECOGNITION - HACKATHON PROJECT 🖐️
═══════════════════════════════════════════════════
    Real-time Hand Gesture Recognition System
    Built with SVM, MediaPipe, Flask & OpenCV
═══════════════════════════════════════════════════
"""
    print(banner)

def check_python_version():
    """Check if Python version is compatible"""
    print("🔍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required. Please upgrade your Python installation.")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def install_dependencies():
    """Install required packages"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies. Please check your internet connection.")
        return False

def check_camera():
    """Check if camera is available"""
    print("\n📷 Checking camera access...")
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            cap.release()
            print("✅ Camera access confirmed!")
            return True
        else:
            print("⚠️ Camera not accessible. Please check camera permissions.")
            return False
    except ImportError:
        print("⚠️ OpenCV not installed. Will attempt to install...")
        return False

def train_model():
    """Train the SVM model"""
    print("\n🤖 Training gesture recognition model...")
    print("This may take a few minutes...")
    
    try:
        # Run training script
        result = subprocess.run([sys.executable, "train_model.py"], 
                              input="y\n", text=True, capture_output=True)
        
        if result.returncode == 0:
            print("✅ Model training completed successfully!")
            return True
        else:
            print("❌ Model training failed:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error during training: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating project directories...")
    
    directories = ['models', 'screenshots', 'templates']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    print("✅ Directories created!")

def start_web_app():
    """Start the Flask web application"""
    print("\n🚀 Starting web application...")
    print("The gesture recognition interface will open in your browser...")
    
    try:
        # Start Flask app in the background
        import threading
        import time
        
        def run_app():
            os.system(f"{sys.executable} app.py")
        
        # Start app in separate thread
        app_thread = threading.Thread(target=run_app, daemon=True)
        app_thread.start()
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Open browser
        webbrowser.open('http://localhost:5000')
        
        print("✅ Web application started!")
        print("🌐 Opening http://localhost:5000 in your browser...")
        print("\n" + "="*50)
        print("🎯 DEMO INSTRUCTIONS:")
        print("1. Allow camera access when prompted")
        print("2. Position your hand in front of the camera")
        print("3. Try different gestures and see real-time recognition")
        print("4. Click 'Enable Mouse Control' to control your mouse")
        print("5. View live statistics and confidence scores")
        print("="*50)
        print("\n⏹️  Press Ctrl+C to stop the application")
        
        # Keep the main thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n👋 Stopping application... Thanks for trying our demo!")
            return True
            
    except Exception as e:
        print(f"❌ Error starting web application: {e}")
        return False

def run_quick_demo():
    """Run a quick camera test demo"""
    print("\n🎥 Running quick camera demo...")
    print("Press 'q' to quit the camera test...")
    
    try:
        import cv2
        import mediapipe as mp
        
        # Initialize MediaPipe
        mp_hands = mp.solutions.hands
        hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        mp_drawing = mp.solutions.drawing_utils
        
        # Start camera
        cap = cv2.VideoCapture(0)
        
        print("✅ Camera demo started! Show your hand to see landmark detection.")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Flip frame horizontally
            frame = cv2.flip(frame, 1)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process with MediaPipe
            results = hands.process(frame_rgb)
            
            # Draw hand landmarks
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            # Add text
            cv2.putText(frame, "Camera Test - Press 'q' to quit", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            cv2.imshow('Gesture Recognition Camera Test', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        print("✅ Camera demo completed!")
        return True
        
    except Exception as e:
        print(f"❌ Camera demo failed: {e}")
        return False

def main():
    """Main demo function"""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        return
    
    # Create directories
    create_directories()
    
    # Install dependencies
    if not install_dependencies():
        return
    
    # Check camera
    camera_ok = check_camera()
    
    # Ask user what they want to do
    print("\n🎮 What would you like to do?")
    print("1. 🚀 Full Demo (Train model + Start web app)")
    print("2. 🎥 Quick Camera Test")
    print("3. 🤖 Train Model Only")
    print("4. 🌐 Start Web App Only (requires trained model)")
    
    try:
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            # Full demo
            if train_model():
                if camera_ok:
                    start_web_app()
                else:
                    print("⚠️ Camera issues detected. Please check camera permissions.")
            
        elif choice == "2":
            # Quick camera test
            if camera_ok:
                run_quick_demo()
            else:
                print("❌ Camera not available for demo.")
        
        elif choice == "3":
            # Train model only
            train_model()
        
        elif choice == "4":
            # Start web app only
            if os.path.exists("models/gesture_svm_model.pkl"):
                if camera_ok:
                    start_web_app()
                else:
                    print("⚠️ Camera issues detected. Please check camera permissions.")
            else:
                print("❌ No trained model found. Please run option 1 or 3 first.")
        
        else:
            print("❌ Invalid choice. Please run the script again.")
    
    except KeyboardInterrupt:
        print("\n\n👋 Demo cancelled by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()