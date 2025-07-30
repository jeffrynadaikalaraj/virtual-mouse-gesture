from flask import Flask, render_template, Response, jsonify, request
import cv2
import numpy as np
import joblib
import mediapipe as mp
import json
import os
import time
from datetime import datetime
import threading
import pyautogui
import pynput.mouse as mouse
import pynput.keyboard as keyboard

app = Flask(__name__)

# Global variables
camera = None
model = None
scaler = None
encoder = None
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)
mp_drawing = mp.solutions.drawing_utils

# Gesture statistics
gesture_stats = {
    'Move Cursor': 0,
    'Left Click': 0,
    'Right Click': 0,
    'Screenshot': 0,
    'Dragging': 0,
    'Idle': 0
}

# Mouse control state
mouse_control_enabled = False
last_gesture = "Idle"
gesture_confidence = 0.0

def load_models():
    """Load the trained SVM model and preprocessing objects"""
    global model, scaler, encoder
    try:
        if os.path.exists("models/gesture_svm_model.pkl"):
            model = joblib.load("models/gesture_svm_model.pkl")
            scaler = joblib.load("models/gesture_scaler.pkl")
            encoder = joblib.load("models/gesture_label_encoder.pkl")
            print("✅ Models loaded successfully!")
            return True
        else:
            print("❌ Model files not found. Please train the model first.")
            return False
    except Exception as e:
        print(f"❌ Error loading models: {e}")
        return False

def extract_hand_features(landmarks):
    """Extract features from MediaPipe hand landmarks"""
    features = []
    
    # Extract all landmark coordinates (x, y, z)
    for landmark in landmarks.landmark:
        features.extend([landmark.x, landmark.y, landmark.z])
    
    # Calculate distances between key points
    thumb_tip = landmarks.landmark[4]
    index_tip = landmarks.landmark[8]
    middle_tip = landmarks.landmark[12]
    ring_tip = landmarks.landmark[16]
    pinky_tip = landmarks.landmark[20]
    
    # Add some additional computed features
    features.append(np.sqrt((thumb_tip.x - index_tip.x)**2 + (thumb_tip.y - index_tip.y)**2))
    features.append(np.sqrt((index_tip.x - middle_tip.x)**2 + (index_tip.y - middle_tip.y)**2))
    
    return np.array(features)

def predict_gesture(features):
    """Predict gesture from extracted features"""
    global model, scaler, encoder
    
    if model is None or scaler is None or encoder is None:
        return "Model Not Loaded", 0.0
    
    try:
        # Ensure we have the right number of features
        if len(features) < 42:  # Pad if too few features
            features = np.pad(features, (0, 42 - len(features)), 'constant')
        elif len(features) > 42:  # Truncate if too many features
            features = features[:42]
        
        # Scale features
        features_scaled = scaler.transform([features])
        
        # Predict
        prediction = model.predict(features_scaled)[0]
        confidence = max(model.decision_function(features_scaled)[0])
        
        # Decode prediction
        gesture = encoder.inverse_transform([prediction])[0]
        
        return gesture, confidence
    except Exception as e:
        print(f"Prediction error: {e}")
        return "Error", 0.0

def execute_gesture_action(gesture):
    """Execute actions based on detected gesture"""
    global mouse_control_enabled
    
    if not mouse_control_enabled:
        return
    
    try:
        if gesture == "Left Click":
            pyautogui.click()
        elif gesture == "Right Click":
            pyautogui.rightClick()
        elif gesture == "Screenshot":
            screenshot = pyautogui.screenshot()
            timestamp = int(time.time())
            screenshot.save(f"screenshots/screenshot_{timestamp}.png")
        elif gesture == "Move Cursor":
            # Move cursor slightly (this would need more sophisticated tracking)
            current_x, current_y = pyautogui.position()
            pyautogui.moveTo(current_x + 10, current_y + 10)
    except Exception as e:
        print(f"Action execution error: {e}")

def generate_frames():
    """Generate frames for video streaming"""
    global camera, gesture_stats, last_gesture, gesture_confidence
    
    camera = cv2.VideoCapture(0)
    
    while True:
        success, frame = camera.read()
        if not success:
            break
        
        # Flip frame horizontally for mirror effect
        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process with MediaPipe
        results = hands.process(frame_rgb)
        
        gesture = "Idle"
        confidence = 0.0
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw hand landmarks
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                # Extract features and predict gesture
                features = extract_hand_features(hand_landmarks)
                gesture, confidence = predict_gesture(features)
                
                # Update statistics
                gesture_stats[gesture] += 1
                last_gesture = gesture
                gesture_confidence = confidence
                
                # Execute gesture action
                execute_gesture_action(gesture)
        
        # Add text overlay
        cv2.putText(frame, f"Gesture: {gesture}", (10, 40),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        cv2.putText(frame, f"Confidence: {confidence:.2f}", (10, 80),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        cv2.putText(frame, f"Mouse Control: {'ON' if mouse_control_enabled else 'OFF'}", 
                   (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, 
                   (0, 255, 0) if mouse_control_enabled else (0, 0, 255), 2)
        
        # Encode frame
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/stats')
def get_stats():
    """Get gesture statistics"""
    return jsonify({
        'gesture_stats': gesture_stats,
        'last_gesture': last_gesture,
        'confidence': gesture_confidence,
        'mouse_control': mouse_control_enabled
    })

@app.route('/api/toggle_mouse')
def toggle_mouse():
    """Toggle mouse control"""
    global mouse_control_enabled
    mouse_control_enabled = not mouse_control_enabled
    return jsonify({'mouse_control': mouse_control_enabled})

@app.route('/api/reset_stats')
def reset_stats():
    """Reset gesture statistics"""
    global gesture_stats
    gesture_stats = {key: 0 for key in gesture_stats}
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs("screenshots", exist_ok=True)
    os.makedirs("models", exist_ok=True)
    
    # Load models
    models_loaded = load_models()
    
    if not models_loaded:
        print("⚠️ Running without trained models. Train the model first for gesture recognition.")
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)