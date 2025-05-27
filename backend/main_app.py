import traceback
from flask import Flask, request
from flask_socketio import SocketIO
from flask_cors import CORS
import base64
import cv2
import numpy as np
import os

from Virtual_Mouse_app import VirtualMouse
from Virtual_Paint_app import VirtualPainter
from Pong_Game_app import PongGame
from Fitness_Tracker_App import ArmCurlsCounter
from PPT_Presentation_App import PresentationController
from Volume_Controll_App import VolumeControl
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
CORS(app, origins=os.getenv('CORS_ORIGINS', '*').split(','))
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_secret_key')
socketio = SocketIO(app, cors_allowed_origins="*", ping_timeout=10, ping_interval=5)

# Dictionary to store active feature instances and their stream threads
active_features = {}

# Feature registry - maps feature names to their class
feature_registry = {
    'virtual-mouse': VirtualMouse,
    'virtual-painter': VirtualPainter,
    'volume-control': VolumeControl,
    'pong-game': PongGame,
    'fitness-tracker': ArmCurlsCounter,
    'ppt-presenter': PresentationController
}


@socketio.on('process_frame')
def process_frame(data):
    """Process a frame sent from the client"""
    session_id = request.sid

    if session_id not in active_features or 'instance' not in active_features[session_id]:
        socketio.emit('error', {'message': 'No active feature to process frame'}, room=session_id)
        return

    try:
        # Decode the base64 image
        image_data = data.get('image')
        if not image_data:
            return

        # Convert base64 string to image
        img_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if frame is None or frame.size == 0:
            print("Received invalid frame")
            return

        # Process the frame with the active feature
        feature = active_features[session_id]['instance']
        processed_frame = feature.process_frame(frame)

        if processed_frame is not None:
            # Encode the processed frame
            processed_encoded = encode_frame(processed_frame)
            if processed_encoded:
                # Send back to client
                socketio.emit('processed_frame', {'image': processed_encoded}, room=session_id)
    except Exception as e:
        print(f"Error processing frame: {e}")
        traceback.print_exc()
        socketio.emit('error', {'message': f'Error processing frame: {str(e)}'}, room=session_id)


@socketio.on('start_feature')
def start_feature(data):
    """Start a specific CV feature"""
    feature_name = data.get('feature')
    session_id = request.sid

    # Stop any running feature for this session
    stop_feature({'session_id': session_id})

    if feature_name in feature_registry:
        try:
            print(f"Starting feature: {feature_name}")
            # Create new instance of the requested feature
            feature_class = feature_registry[feature_name]
            feature_instance = feature_class()

            # Disable actual mouse control by default for safety
            if feature_name == 'virtual-mouse' and hasattr(feature_instance, 'toggle_control'):
                feature_instance.toggle_control(False)

            # Store the feature instance
            active_features[session_id] = {
                'name': feature_name,
                'instance': feature_instance,
                'running': True
            }

            # Notify client that we're ready to receive frames
            socketio.emit('ready_for_frames', {}, room=session_id)

            print(f"Feature {feature_name} started successfully")
            return {'status': 'success', 'message': f'{feature_name} started'}

        except Exception as e:
            print(f"Error starting feature {feature_name}: {e}")
            traceback.print_exc()
            socketio.emit('error', {'message': f'Error starting feature: {str(e)}'}, room=session_id)
            return {'status': 'error', 'message': f'Error starting feature: {str(e)}'}
    else:
        print(f"Feature not found: {feature_name}")
        return {'status': 'error', 'message': 'Feature not found'}


@socketio.on('stop_feature')
def stop_feature(data):
    """Stop the currently running feature"""
    session_id = data.get('session_id', request.sid)

    if session_id in active_features:
        try:
            feature_name = active_features[session_id]['name']
            print(f"Stopping feature: {feature_name}")

            active_features[session_id]['running'] = False
            if 'instance' in active_features[session_id]:
                active_features[session_id]['instance'].stop()

            del active_features[session_id]
            return {'status': 'success', 'message': 'Feature stopped'}
        except Exception as e:
            print(f"Error stopping feature: {e}")
            traceback.print_exc()
            return {'status': 'error', 'message': f'Error stopping feature: {str(e)}'}
    return {'status': 'info', 'message': 'No feature running'}


@socketio.on('key_press')
def handle_key_press(data):
    """Forward key presses to the active feature"""
    session_id = request.sid
    if session_id in active_features and 'instance' in active_features[session_id]:
        try:
            feature = active_features[session_id]['instance']
            # Check if the feature has a method to handle key presses
            if hasattr(feature, 'handle_key_press'):
                print(data.get('key'))
                feature.handle_key_press(data)
            # Handle global key commands
            if data.get('key') == 'q':
                stop_feature({'session_id': session_id})
        except Exception as e:
            print(f"Error handling key press: {e}")
            traceback.print_exc()


def encode_frame(frame):
    try:
        if frame is None or not isinstance(frame, np.ndarray):
            print("Invalid frame type:", type(frame))
            return None

        # Check if frame is a valid image
        if frame.size == 0 or len(frame.shape) < 2:
            print("Invalid frame dimensions:", frame.shape)
            return None

        # Ensure frame is resized to expected dimensions
        frame = cv2.resize(frame, (1280, 720))
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        return base64.b64encode(buffer).decode('utf-8')
    except Exception as e:
        print(f"Frame encoding error: {e}")
        traceback.print_exc()  # Print the full traceback
        return None


@socketio.on('connect')
def handle_connect():
    print(f"Client connected: {request.sid}")


@socketio.on('disconnect')
def handle_disconnect():
    print(f"Client disconnected: {request.sid}")
    stop_feature({'session_id': request.sid})


if __name__ == '__main__':
    try:
        print("Starting Computer Vision server on port 5000...")
        port = int(os.getenv('PORT', 5000))
        debug = os.getenv('DEBUG', 'False').lower() == 'true'
        socketio.run(app, host='0.0.0.0', port=port, debug=debug, allow_unsafe_werkzeug=True)
    except Exception as e:
        print(f"Failed to start server: {e}")
        traceback.print_exc()
    finally:
        # Clean up any active features
        for session_id in list(active_features.keys()):
            try:
                if 'instance' in active_features[session_id]:
                    active_features[session_id]['instance'].stop()
            except:
                pass