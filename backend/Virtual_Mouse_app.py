import cv2
import numpy as np
import time
import pyautogui
import math
from cvzone.HandTrackingModule import HandDetector as hd


class VirtualMouse:
    def __init__(self, wCam=1280, hCam=720, smoothing=10):
        self.wCam = wCam
        self.hCam = hCam
        self.smoothing = smoothing
        self.prevX = 0
        self.prevY = 0
        self.curX = 0
        self.curY = 0
        self.detector = hd(maxHands=1)
        self.wScr, self.hScr = pyautogui.size()
        self.mode = 'normal'  # Can be 'normal' or 'finger'
        self.cTime = 0
        self.pTime = 0
        self.over = False
        self.is_running = True
        self.lmList = []
        self.fingers = []
        self.last_frame = None

        # Flag to enable/disable actual mouse control
        self.control_enabled = False

    def set_mode(self, mode):
        if mode in ['normal', 'finger']:
            self.mode = mode
            print(f"Mode set to: {mode}")

    def toggle_control(self, enabled=None):
        if enabled is not None:
            self.control_enabled = enabled
        else:
            self.control_enabled = not self.control_enabled
        print(f"Mouse control {'enabled' if self.control_enabled else 'disabled'}")

    def process_frame(self, img=None):
        """
        Process a frame for hand tracking and mouse control.

        Args:
            img: Input frame from client. If None, uses last frame or returns a blank frame.

        Returns:
            Processed frame with visual overlays
        """
        if not self.is_running:
            return None

        if img is None:
            return self.last_frame if self.last_frame is not None else np.zeros((self.hCam, self.wCam, 3), np.uint8)

        # Flip the image horizontally for a more intuitive mirror view
        img = cv2.flip(img, 1)

        # Find hands in the frame
        hands, img = self.detector.findHands(img)

        if hands:
            # Get the landmark list for the first hand
            hand = hands[0]
            self.lmList = hand["lmList"]

            if len(self.lmList) > 0:
                # Get index and middle finger tips
                x1, y1 = self.lmList[8][0:2]
                x2, y2 = self.lmList[12][0:2]

                # Check which fingers are up
                self.fingers = self.detector.fingersUp(hand)

                # Draw rectangle for the interactive area
                cv2.rectangle(img, (100, 100), (self.wCam - 50, self.hCam - 50), (255, 255, 0), 3)

                if self.mode == 'normal':
                    # Moving mode - Index finger up, middle finger down
                    if self.fingers[1] and not self.fingers[2]:
                        self.move_mouse(x1, y1, img)

                    # Clicking mode - Both index and middle fingers up
                    if self.fingers[1] and self.fingers[2]:
                        self.click_mouse(x1, y1, x2, y2, img)

                elif self.mode == 'finger':
                    # Alternate mode with finger visualization
                    if self.fingers[1] and not self.fingers[2]:
                        self.move_mouse(x1, y1, img, finger_only=True)

                    if self.fingers[1] and self.fingers[2]:
                        self.click_mouse(x1, y1, x2, y2, img)

                    # Exit condition (all fingers up)
                    if self.fingers == [1, 1, 1, 1, 1] or self.fingers == [0, 1, 1, 1, 1]:
                        self.over = True

        # Display FPS
        self.display_fps(img)

        # Display current mode on the image
        cv2.putText(img, f"Mode: {self.mode}", (self.wCam - 200, 50), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)

        # Display control status
        status = "Control: ON" if self.control_enabled else "Control: OFF"
        cv2.putText(img, status, (self.wCam - 200, 90), cv2.FONT_HERSHEY_PLAIN, 2,
                    (0, 255, 0) if self.control_enabled else (0, 0, 255), 2)

        self.last_frame = img
        return img

    def move_mouse(self, x1, y1, img, finger_only=False):
        # Map the finger coordinates to screen coordinates
        x3, y3 = np.interp(x1, (100, self.wCam - 100), (0, self.wScr)), np.interp(y1, (100, self.hCam - 100),
                                                                                  (0, self.hScr))

        if finger_only:
            if self.fingers[1] and self.fingers[2]:
                cv2.circle(img, (x1, y1), 20, (0, 0, 255), -1)
        else:
            # Only move the actual system mouse if control is enabled
            if self.control_enabled:
                pyautogui.moveTo(x3, y3)

        # Visual feedback - draw a circle at the finger tip
        cv2.circle(img, (x1, y1), 15, (255, 0, 0), cv2.FILLED)

    def click_mouse(self, x1, y1, x2, y2, img):
        # Draw a line between index and middle finger
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)

        # Calculate distance between fingers
        length = math.hypot(x2 - x1, y2 - y1)

        # If fingers are close enough, perform click
        if length < 60:
            # Only perform the actual click if control is enabled
            if self.control_enabled:
                pyautogui.click()

            # Visual feedback for click
            cv2.circle(img, ((x1 + x2) // 2, (y1 + y2) // 2), 15, (0, 255, 0), cv2.FILLED)

    def display_fps(self, img):
        self.cTime = time.time()
        fps = 1 / (self.cTime - self.pTime) if (self.cTime - self.pTime) > 0 else 60
        self.pTime = self.cTime
        cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)

    def handle_key_press(self, data):
        """Handle key press events from the client"""
        key = data.get('key')
        print(f"Key pressed: {key}")

        if key == 'n':
            self.set_mode('normal')
        elif key == 'f':
            self.set_mode('finger')
        elif key == 'c':
            self.toggle_control()
        elif key == 'q':
            self.stop()

    def stop(self):
        """Clean up resources"""
        self.is_running = False
        print("Virtual Mouse stopped")