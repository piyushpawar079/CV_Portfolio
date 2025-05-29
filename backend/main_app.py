# import traceback
# from flask import Flask, request
# from flask_socketio import SocketIO
# from flask_cors import CORS
# import base64
# import cv2
# import numpy as np
# import os

# from Virtual_Mouse_app import VirtualMouse
# from Virtual_Paint_app import VirtualPainter
# from Pong_Game_app import PongGame
# from Fitness_Tracker_App import ArmCurlsCounter
# from PPT_Presentation_App import PresentationController
# from Volume_Controll_App import VolumeControl
# from dotenv import load_dotenv

# load_dotenv()
# app = Flask(__name__)

# # Configure CORS for Render deployment
# cors_origins = os.getenv('CORS_ORIGINS', '*')
# if cors_origins != '*':
#     cors_origins = cors_origins.split(',')

# CORS(app, origins=cors_origins)
# app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_secret_key')

# # Configure SocketIO for production
# socketio = SocketIO(
#     app, 
#     cors_allowed_origins=cors_origins,
#     ping_timeout=60,
#     ping_interval=25,
#     logger=False,
#     engineio_logger=False
# )

# # Dictionary to store active feature instances and their stream threads
# active_features = {}

# # Feature registry - maps feature names to their class
# feature_registry = {
#     'virtual-mouse': VirtualMouse,
#     'virtual-painter': VirtualPainter,
#     'volume-control': VolumeControl,
#     'pong-game': PongGame,
#     'fitness-tracker': ArmCurlsCounter,
#     'ppt-presenter': PresentationController
# }

# # Add a health check endpoint for Render
# @app.route('/')
# def health_check():
#     return {'status': 'healthy', 'service': 'cv-portfolio-backend'}, 200

# @app.route('/health')
# def health():
#     return {'status': 'ok'}, 200

# @socketio.on('process_frame')
# def process_frame(data):
#     """Process a frame sent from the client"""
#     session_id = request.sid

#     if session_id not in active_features or 'instance' not in active_features[session_id]:
#         socketio.emit('error', {'message': 'No active feature to process frame'}, room=session_id)
#         return

#     try:
#         # Decode the base64 image
#         image_data = data.get('image')
#         if not image_data:
#             return

#         # Convert base64 string to image
#         img_bytes = base64.b64decode(image_data)
#         nparr = np.frombuffer(img_bytes, np.uint8)
#         frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

#         if frame is None or frame.size == 0:
#             print("Received invalid frame")
#             return

#         # Process the frame with the active feature
#         feature = active_features[session_id]['instance']
#         processed_frame = feature.process_frame(frame)

#         if processed_frame is not None:
#             # Encode the processed frame
#             processed_encoded = encode_frame(processed_frame)
#             if processed_encoded:
#                 # Send back to client
#                 socketio.emit('processed_frame', {'image': processed_encoded}, room=session_id)
#     except Exception as e:
#         print(f"Error processing frame: {e}")
#         traceback.print_exc()
#         socketio.emit('error', {'message': f'Error processing frame: {str(e)}'}, room=session_id)


# @socketio.on('start_feature')
# def start_feature(data):
#     """Start a specific CV feature"""
#     feature_name = data.get('feature')
#     session_id = request.sid

#     # Stop any running feature for this session
#     stop_feature({'session_id': session_id})

#     if feature_name in feature_registry:
#         try:
#             print(f"Starting feature: {feature_name}")
#             # Create new instance of the requested feature
#             feature_class = feature_registry[feature_name]
#             feature_instance = feature_class()

#             # Disable actual mouse control by default for safety
#             if feature_name == 'virtual-mouse' and hasattr(feature_instance, 'toggle_control'):
#                 feature_instance.toggle_control(False)

#             # Store the feature instance
#             active_features[session_id] = {
#                 'name': feature_name,
#                 'instance': feature_instance,
#                 'running': True
#             }

#             # Notify client that we're ready to receive frames
#             socketio.emit('ready_for_frames', {}, room=session_id)

#             print(f"Feature {feature_name} started successfully")
#             return {'status': 'success', 'message': f'{feature_name} started'}

#         except Exception as e:
#             print(f"Error starting feature {feature_name}: {e}")
#             traceback.print_exc()
#             socketio.emit('error', {'message': f'Error starting feature: {str(e)}'}, room=session_id)
#             return {'status': 'error', 'message': f'Error starting feature: {str(e)}'}
#     else:
#         print(f"Feature not found: {feature_name}")
#         return {'status': 'error', 'message': 'Feature not found'}


# @socketio.on('stop_feature')
# def stop_feature(data):
#     """Stop the currently running feature"""
#     session_id = data.get('session_id', request.sid)

#     if session_id in active_features:
#         try:
#             feature_name = active_features[session_id]['name']
#             print(f"Stopping feature: {feature_name}")

#             active_features[session_id]['running'] = False
#             if 'instance' in active_features[session_id]:
#                 active_features[session_id]['instance'].stop()

#             del active_features[session_id]
#             return {'status': 'success', 'message': 'Feature stopped'}
#         except Exception as e:
#             print(f"Error stopping feature: {e}")
#             traceback.print_exc()
#             return {'status': 'error', 'message': f'Error stopping feature: {str(e)}'}
#     return {'status': 'info', 'message': 'No feature running'}


# @socketio.on('key_press')
# def handle_key_press(data):
#     """Forward key presses to the active feature"""
#     session_id = request.sid
#     if session_id in active_features and 'instance' in active_features[session_id]:
#         try:
#             feature = active_features[session_id]['instance']
#             # Check if the feature has a method to handle key presses
#             if hasattr(feature, 'handle_key_press'):
#                 print(data.get('key'))
#                 feature.handle_key_press(data)
#             # Handle global key commands
#             if data.get('key') == 'q':
#                 stop_feature({'session_id': session_id})
#         except Exception as e:
#             print(f"Error handling key press: {e}")
#             traceback.print_exc()


# def encode_frame(frame):
#     try:
#         if frame is None or not isinstance(frame, np.ndarray):
#             print("Invalid frame type:", type(frame))
#             return None

#         # Check if frame is a valid image
#         if frame.size == 0 or len(frame.shape) < 2:
#             print("Invalid frame dimensions:", frame.shape)
#             return None

#         # Ensure frame is resized to expected dimensions
#         frame = cv2.resize(frame, (1280, 720))
#         _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
#         return base64.b64encode(buffer).decode('utf-8')
#     except Exception as e:
#         print(f"Frame encoding error: {e}")
#         traceback.print_exc()  # Print the full traceback
#         return None


# @socketio.on('connect')
# def handle_connect():
#     print(f"Client connected: {request.sid}")


# @socketio.on('disconnect')
# def handle_disconnect():
#     print(f"Client disconnected: {request.sid}")
#     stop_feature({'session_id': request.sid})


# if __name__ == '__main__':
#     try:
#         print("Starting Computer Vision server...")
#         port = int(os.getenv('PORT', 5000))
#         debug = os.getenv('DEBUG', 'False').lower() == 'true'
        
#         # Use different configurations for development vs production
#         if os.getenv('RENDER'):
#             # Production on Render
#             socketio.run(app, host='0.0.0.0', port=port, debug=False)
#         else:
#             # Development
#             socketio.run(app, host='0.0.0.0', port=port, debug=debug, allow_unsafe_werkzeug=True)
#     except Exception as e:
#         print(f"Failed to start server: {e}")
#         traceback.print_exc()
#     finally:
#         # Clean up any active features
#         for session_id in list(active_features.keys()):
#             try:
#                 if 'instance' in active_features[session_id]:
#                     active_features[session_id]['instance'].stop()
#             except:
#                 pass


import traceback
from flask import Flask, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import base64
import cv2
import numpy as np
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor

from Virtual_Mouse_app import VirtualMouse
from Virtual_Paint_app import VirtualPainter
from Pong_Game_app import PongGame
from Fitness_Tracker_App import ArmCurlsCounter
from PPT_Presentation_App import PresentationController
from Volume_Controll_App import VolumeControl
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# Configure CORS for Render deployment
cors_origins = os.getenv('CORS_ORIGINS', '*')
if cors_origins != '*':
    cors_origins = cors_origins.split(',')

CORS(app, origins=cors_origins)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_secret_key')

# Configure SocketIO for production with proper threading
socketio = SocketIO(
    app, 
    cors_allowed_origins=cors_origins,
    ping_timeout=60,
    ping_interval=25,
    logger=False,
    engineio_logger=False,
    async_mode='threading'  # Important for handling multiple clients
)

# Thread pool for processing frames
executor = ThreadPoolExecutor(max_workers=4)

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

# Pre-loaded feature instances to avoid loading during requests
preloaded_features = {}

def preload_features():
    """Pre-load all feature classes to avoid initialization delays"""
    print("Pre-loading CV features...")
    
    for feature_name, feature_class in feature_registry.items():
        try:
            print(f"Loading {feature_name}...")
            
            # Create instance but don't start it yet
            instance = feature_class()
            
            # Disable camera initialization if it's a cloud environment
            if hasattr(instance, 'setup_camera') and os.getenv('RENDER'):
                instance.setup_camera = lambda: None
            
            # Store the class for later instantiation (not the instance)
            preloaded_features[feature_name] = feature_class
            print(f"✓ {feature_name} loaded successfully")
            
        except Exception as e:
            print(f"✗ Failed to load {feature_name}: {e}")
            # Don't let one failure stop the server
            preloaded_features[feature_name] = feature_class

    print("Feature pre-loading completed!")

# Add a health check endpoint for Render
@app.route('/')
def health_check():
    return {'status': 'healthy', 'service': 'cv-portfolio-backend', 'features': list(preloaded_features.keys())}, 200

@app.route('/health')
def health():
    return {'status': 'ok'}, 200

def process_frame_async(session_id, image_data):
    """Process frame asynchronously to avoid blocking SocketIO"""
    try:
        if session_id not in active_features or 'instance' not in active_features[session_id]:
            socketio.emit('error', {'message': 'No active feature to process frame'}, room=session_id)
            return

        # Convert base64 string to image
        img_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if frame is None or frame.size == 0:
            print("Received invalid frame")
            return

        # Check if feature is still running
        if not active_features[session_id].get('running', False):
            return

        # Process the frame with the active feature
        feature = active_features[session_id]['instance']
        processed_frame = feature.process_frame(frame)

        if processed_frame is not None and active_features[session_id].get('running', False):
            # Encode the processed frame
            processed_encoded = encode_frame(processed_frame)
            if processed_encoded:
                # Send back to client
                socketio.emit('processed_frame', {'image': processed_encoded}, room=session_id)
                
    except Exception as e:
        print(f"Error processing frame: {e}")
        traceback.print_exc()
        socketio.emit('error', {'message': f'Error processing frame: {str(e)}'}, room=session_id)

@socketio.on('process_frame')
def process_frame(data):
    """Process a frame sent from the client"""
    session_id = request.sid
    
    # Quick validation
    image_data = data.get('image')
    if not image_data:
        return

    if session_id not in active_features or 'instance' not in active_features[session_id]:
        emit('error', {'message': 'No active feature to process frame'})
        return

    # Process frame in background thread to avoid blocking
    executor.submit(process_frame_async, session_id, image_data)

@socketio.on('start_feature')
def start_feature(data):
    """Start a specific CV feature"""
    feature_name = data.get('feature')
    session_id = request.sid

    print(f"=== STARTING FEATURE: {feature_name} for session {session_id} ===")

    # Stop any running feature for this session
    stop_feature({'session_id': session_id})

    if feature_name in preloaded_features:
        try:
            print(f"Creating new instance of {feature_name}")
            
            # Create new instance of the requested feature
            feature_class = preloaded_features[feature_name]
            feature_instance = feature_class()

            # Handle cloud environment setup
            if os.getenv('RENDER'):
                # Disable camera-related features for cloud deployment
                if hasattr(feature_instance, 'setup_camera'):
                    feature_instance.setup_camera = lambda: None
                
                # For features that might try to access camera during initialization
                if hasattr(feature_instance, 'cap'):
                    feature_instance.cap = None

            # Disable actual mouse control by default for safety
            if feature_name == 'virtual-mouse' and hasattr(feature_instance, 'toggle_control'):
                feature_instance.toggle_control(False)

            # Store the feature instance
            active_features[session_id] = {
                'name': feature_name,
                'instance': feature_instance,
                'running': True
            }

            print(f"✓ Feature {feature_name} started successfully")
            
            # Notify client that we're ready to receive frames
            emit('ready_for_frames', {'feature': feature_name, 'status': 'ready'})
            emit('feature_started', {'feature': feature_name, 'status': 'success'})

        except Exception as e:
            print(f"✗ Error starting feature {feature_name}: {e}")
            traceback.print_exc()
            emit('error', {'message': f'Error starting feature: {str(e)}'})
            
    else:
        print(f"✗ Feature not found: {feature_name}")
        emit('error', {'message': 'Feature not found'})

@socketio.on('stop_feature')
def stop_feature(data):
    """Stop the currently running feature"""
    session_id = data.get('session_id', request.sid)

    if session_id in active_features:
        try:
            feature_name = active_features[session_id]['name']
            print(f"=== STOPPING FEATURE: {feature_name} for session {session_id} ===")

            active_features[session_id]['running'] = False
            
            if 'instance' in active_features[session_id]:
                try:
                    active_features[session_id]['instance'].stop()
                except:
                    pass  # Some features might not have a stop method

            del active_features[session_id]
            print(f"✓ Feature {feature_name} stopped successfully")
            
        except Exception as e:
            print(f"✗ Error stopping feature: {e}")
            traceback.print_exc()

@socketio.on('key_press')
def handle_key_press(data):
    """Forward key presses to the active feature"""
    session_id = request.sid
    if session_id in active_features and 'instance' in active_features[session_id]:
        try:
            feature = active_features[session_id]['instance']
            # Check if the feature has a method to handle key presses
            if hasattr(feature, 'handle_key_press'):
                print(f"Key press: {data.get('key')}")
                feature.handle_key_press(data)
            
            # Handle global key commands
            if data.get('key') == 'q':
                stop_feature({'session_id': session_id})
                
        except Exception as e:
            print(f"Error handling key press: {e}")
            traceback.print_exc()

def encode_frame(frame):
    """Encode frame to base64 with error handling"""
    try:
        if frame is None or not isinstance(frame, np.ndarray):
            return None

        # Check if frame is a valid image
        if frame.size == 0 or len(frame.shape) < 2:
            return None

        # Resize frame for consistent output
        frame = cv2.resize(frame, (1280, 720))
        
        # Encode with lower quality for better performance
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 70]
        _, buffer = cv2.imencode('.jpg', frame, encode_param)
        
        return base64.b64encode(buffer).decode('utf-8')
        
    except Exception as e:
        print(f"Frame encoding error: {e}")
        return None

@socketio.on('connect')
def handle_connect():
    print(f"=== CLIENT CONNECTED: {request.sid} ===")
    emit('connection_status', {'status': 'connected', 'available_features': list(preloaded_features.keys())})

@socketio.on('disconnect')
def handle_disconnect():
    print(f"=== CLIENT DISCONNECTED: {request.sid} ===")
    stop_feature({'session_id': request.sid})

@socketio.on('ping')
def handle_ping():
    """Handle ping from client to keep connection alive"""
    emit('pong')

# Test endpoint for debugging
@socketio.on('test_connection')
def handle_test():
    print(f"=== TEST CONNECTION from {request.sid} ===")
    emit('test_response', {'message': 'Backend is working!', 'timestamp': time.time()})

if __name__ == '__main__':
    try:
        print("=== STARTING COMPUTER VISION SERVER ===")
        
        # Pre-load features before starting server
        preload_features()
        
        port = int(os.getenv('PORT', 5000))
        debug = os.getenv('DEBUG', 'False').lower() == 'true'
        
        print(f"Server starting on port {port}")
        
        # Use different configurations for development vs production
        if os.getenv('RENDER'):
            print("Running in PRODUCTION mode (Render)")
            socketio.run(app, host='0.0.0.0', port=port, debug=False)
        else:
            print("Running in DEVELOPMENT mode")
            socketio.run(app, host='0.0.0.0', port=port, debug=debug, allow_unsafe_werkzeug=True)
            
    except Exception as e:
        print(f"✗ Failed to start server: {e}")
        traceback.print_exc()
    finally:
        print("=== CLEANING UP ===")
        # Clean up any active features
        for session_id in list(active_features.keys()):
            try:
                if 'instance' in active_features[session_id]:
                    active_features[session_id]['instance'].stop()
            except:
                pass
        
        # Shutdown thread pool
        executor.shutdown(wait=True)