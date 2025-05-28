import cv2
import numpy as np
import time
import os
import math
from cvzone.HandTrackingModule import HandDetector as hd
import subprocess
import platform

class VolumeControl:
    def __init__(self, wCam=1280, hCam=720):
        self.wCam = wCam
        self.hCam = hCam
        self.detector = hd(maxHands=1)
        self.minVol = 0
        self.maxVol = 100
        self.vol = 0
        self.volBar = 400
        self.volPer = 0
        self.area = 0
        self.smoothness = 10
        self.is_running = True
        self.last_frame = None
        
        # Detect platform and setup volume control
        self.platform = platform.system().lower()
        self.setup_volume_control()

    def setup_volume_control(self):
        """Setup volume control based on the platform"""
        if self.platform == 'windows':
            try:
                from comtypes import CLSCTX_ALL
                from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
                
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                self.volume = interface.QueryInterface(IAudioEndpointVolume)
                self.minVol, self.maxVol, _ = self.volume.GetVolumeRange()
                self.volume_available = True
                print("Windows volume control initialized")
            except ImportError:
                print("pycaw not available, using mock volume control")
                self.volume_available = False
        elif self.platform == 'linux':
            # Check if ALSA is available
            try:
                result = subprocess.run(['which', 'amixer'], capture_output=True, text=True)
                if result.returncode == 0:
                    self.volume_available = True
                    print("Linux ALSA volume control available")
                else:
                    self.volume_available = False
                    print("ALSA not available, using mock volume control")
            except:
                self.volume_available = False
                print("Volume control not available, using mock")
        else:
            self.volume_available = False
            print(f"Volume control not supported on {self.platform}, using mock")

    def set_volume(self, volume_percent):
        """Set system volume based on platform"""
        if not self.volume_available:
            print(f"Mock volume set to: {volume_percent}%")
            return
            
        try:
            if self.platform == 'windows':
                volume = np.interp(volume_percent, [0, 100], [self.minVol, self.maxVol])
                self.volume.SetScalarVolume(volume, None)
            elif self.platform == 'linux':
                # Use ALSA amixer to set volume
                subprocess.run(['amixer', 'set', 'Master', f'{int(volume_percent)}%'], 
                             capture_output=True, check=True)
        except Exception as e:
            print(f"Error setting volume: {e}")

    def get_volume(self):
        """Get current system volume"""
        if not self.volume_available:
            return self.volPer
            
        try:
            if self.platform == 'windows':
                current_vol = self.volume.GetScalarVolume()
                return int(np.interp(current_vol, [self.minVol, self.maxVol], [0, 100]))
            elif self.platform == 'linux':
                result = subprocess.run(['amixer', 'get', 'Master'], 
                                      capture_output=True, text=True, check=True)
                # Parse volume from amixer output
                for line in result.stdout.split('\n'):
                    if '[' in line and '%' in line:
                        vol_str = line.split('[')[1].split('%')[0]
                        return int(vol_str)
        except Exception as e:
            print(f"Error getting volume: {e}")
        
        return self.volPer

    def process_frame(self, img=None):
        """Process frame for hand tracking and volume control"""
        if not self.is_running:
            return None

        if img is None:
            return self.last_frame if self.last_frame is not None else np.zeros((self.hCam, self.wCam, 3), np.uint8)

        # Flip the image horizontally for mirror view
        img = cv2.flip(img, 1)

        # Find hands
        try:
            hands, img = self.detector.findHands(img)
        except Exception as e:
            print(f"Hand detection error: {e}")
            hands = []

        if hands:
            hand = hands[0]
            lmList = hand["lmList"]
            
            if len(lmList) != 0:
                self.area = (hand['bbox'][2] - hand['bbox'][0]) * (hand['bbox'][3] - hand['bbox'][1]) // 100
                
                if 250 < self.area < 1000:
                    # Get thumb and index finger positions
                    x1, y1 = lmList[4][0], lmList[4][1]
                    x2, y2 = lmList[8][0], lmList[8][1]
                    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

                    # Draw circles on finger tips
                    cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
                    cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
                    cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
                    cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

                    # Calculate distance between fingers
                    length = math.hypot(x2 - x1, y2 - y1)

                    # Convert hand range to volume range
                    self.vol = np.interp(length, [50, 300], [self.minVol, self.maxVol])
                    self.volBar = np.interp(length, [50, 300], [400, 150])
                    self.volPer = np.interp(length, [50, 300], [0, 100])

                    # Set volume (smoothened)
                    self.set_volume(self.volPer)

                    # Visual feedback for volume level
                    if length < 50:
                        cv2.circle(img, (cx, cy), 15, (0, 255, 0), cv2.FILLED)

        # Draw volume bar
        cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 0), 3)
        cv2.rectangle(img, (50, int(self.volBar)), (85, 400), (255, 0, 0), cv2.FILLED)
        cv2.putText(img, f'{int(self.volPer)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)

        # Display current volume from system
        current_vol = self.get_volume()
        cv2.putText(img, f'System Vol: {current_vol}%', (self.wCam - 300, 50), 
                   cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)

        # Display platform info
        cv2.putText(img, f'Platform: {self.platform.title()}', (self.wCam - 300, 90), 
                   cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)

        # Display volume control status
        status = "Volume: ON" if self.volume_available else "Volume: MOCK"
        cv2.putText(img, status, (self.wCam - 300, 130), cv2.FONT_HERSHEY_PLAIN, 2,
                   (0, 255, 0) if self.volume_available else (255, 0, 0), 2)

        self.last_frame = img
        return img

    def handle_key_press(self, data):
        """Handle key press events"""
        key = data.get('key')
        print(f"Key pressed: {key}")
        
        if key == 'q':
            self.stop()
        elif key == '+':
            # Increase volume by 10%
            new_vol = min(100, self.volPer + 10)
            self.set_volume(new_vol)
            self.volPer = new_vol
        elif key == '-':
            # Decrease volume by 10%
            new_vol = max(0, self.volPer - 10)
            self.set_volume(new_vol)
            self.volPer = new_vol

    def stop(self):
        """Clean up resources"""
        self.is_running = False
        print("Volume Control stopped")