import cv2
import numpy as np
import time
import math
import mediapipe as mp
from cvzone.HandTrackingModule import HandDetector


class PoseDetector:
    def __init__(self, mode=False, upBody=False, smooth=True,
                 detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.upBody = upBody
        self.smooth = smooth
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpDraw = mp.solutions.drawing_utils
        self.mpPose = mp.solutions.pose
        self.pose = self.mpPose.Pose(static_image_mode=self.mode,
                                     model_complexity=1,
                                     smooth_landmarks=self.smooth,
                                     enable_segmentation=False,
                                     smooth_segmentation=True,
                                     min_detection_confidence=self.detectionCon,
                                     min_tracking_confidence=self.trackCon)

    def findPose(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.pose.process(imgRGB)
        if self.results.pose_landmarks:
            if draw:
                self.mpDraw.draw_landmarks(img, self.results.pose_landmarks,
                                           self.mpPose.POSE_CONNECTIONS)
        return img

    def findPosition(self, img, draw=True):
        self.lmList = []
        if self.results.pose_landmarks:
            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                self.lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)
        return self.lmList

    def findAngle(self, img, p1, p2, p3, draw=True):
        x1, y1 = self.lmList[p1][1:]
        x2, y2 = self.lmList[p2][1:]
        x3, y3 = self.lmList[p3][1:]
        angle = math.degrees(math.atan2(y3 - y2, x3 - x2) -
                             math.atan2(y1 - y2, x1 - x2))
        if angle < 0:
            angle += 360
        if draw:
            cv2.line(img, (x1, y1), (x2, y2), (255, 255, 255), 3)
            cv2.line(img, (x3, y3), (x2, y2), (255, 255, 255), 3)
            cv2.circle(img, (x1, y1), 10, (0, 0, 255), cv2.FILLED)
            cv2.circle(img, (x1, y1), 15, (0, 0, 255), 2)
            cv2.circle(img, (x2, y2), 10, (0, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 15, (0, 0, 255), 2)
            cv2.circle(img, (x3, y3), 10, (0, 0, 255), cv2.FILLED)
            cv2.circle(img, (x3, y3), 15, (0, 0, 255), 2)
            cv2.putText(img, str(int(angle)), (x2 - 50, y2 + 50),
                        cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)
        return angle


class ArmCurlsCounter:
    def __init__(self):
        """Initialize the Arm Curls Counter compatible with main backend"""
        # Initialize pose and hand detectors with optimized settings
        self.detector = PoseDetector(detectionCon=0.7, trackCon=0.5)
        self.hands_detector = HandDetector(maxHands=1, detectionCon=0.7 )

        # Counter variables
        self.count = 0
        self.dir = 0
        self.active_arm = 'right'  # Default to right arm

        # UI elements
        self.button_left = {'x1': 50, 'y1': 50, 'x2': 200, 'y2': 100}
        self.button_right = {'x1': 250, 'y1': 50, 'x2': 400, 'y2': 100}

        # Timing variables
        self.pTime = 0
        self.last_switch_time = 0
        self.switch_delay = 1.0

        # Performance optimization variables
        self.frame_skip_counter = 0
        self.hand_detection_interval = 3  # Process hands every 3rd frame
        self.last_hand_positions = None
        self.hand_detection_enabled = True

        # State management
        self.is_running = True

        print("ArmCurlsCounter initialized successfully")

    def process_frame(self, frame):
        """
        Process a single frame - main interface method expected by backend
        Args:
            frame: Input frame from camera
        Returns:
            Processed frame with UI elements
        """
        if not self.is_running or frame is None:
            return frame

        try:
            # Flip frame for mirror effect
            img = cv2.flip(frame, 1)

            # Optimize hand detection - only process every nth frame
            if self.hand_detection_enabled:
                self.frame_skip_counter += 1
                if self.frame_skip_counter >= self.hand_detection_interval:
                    self.frame_skip_counter = 0
                    # Process hand detection for UI interaction (lightweight)
                    hands, img = self.hands_detector.findHands(img, draw=False, flipType=False)
                    if hands and len(hands) > 0:
                        # Get hand landmarks efficiently
                        hand = hands[0]
                        lmlist = hand['lmList']
                        if lmlist and len(lmlist) > 8:
                            # Store positions for next frames
                            self.last_hand_positions = lmlist
                            # Only calculate fingers when needed
                            fingers = self.hands_detector.fingersUp(hand)
                            self.handle_click(lmlist, fingers)
                    else:
                        self.last_hand_positions = None

            # Always process pose detection (this is the main functionality)
            img = self.detector.findPose(img, False)
            lmList = self.detector.findPosition(img, False)

            if len(lmList) != 0:
                # Get angle based on active arm
                if self.active_arm == 'right':
                    shoulder, elbow, wrist = 15, 13, 11
                else:
                    shoulder, elbow, wrist = 12, 14, 16

                try:
                    angle = self.detector.findAngle(img, shoulder, elbow, wrist)

                    # Calculate percentage and progress bar position
                    per = np.interp(angle, (210, 310), (0, 100))
                    bar = np.interp(angle, (220, 310), (650, 100))

                    # Update counter based on movement
                    color = self.update_count(per)

                    # Draw UI elements
                    self.draw_ui(img, per, bar, color)
                except:
                    # If angle calculation fails, just draw basic UI
                    self.draw_basic_ui(img)
            else:
                # No pose detected, draw basic UI
                self.draw_basic_ui(img)

            # Add FPS display
            img = self.show_fps(img)

            return img

        except Exception as e:
            print(f"Error in process_frame: {e}")
            return frame

    def update_count(self, per):
        """Update the rep counter based on arm position percentage"""
        color = (255, 0, 255)  # Default magenta

        if per == 100:
            color = (0, 255, 0)  # Green when fully extended
            if self.dir == 0:
                self.count += 0.5
                self.dir = 1
        if per == 0:
            color = (0, 255, 0)  # Green when fully contracted
            if self.dir == 1:
                self.count += 0.5
                self.dir = 0
        return color

    def draw_ui(self, img, per, bar, color):
        """Draw all UI elements on the frame"""
        # Progress bar
        cv2.rectangle(img, (1100, 100), (1175, 650), (200, 200, 200), 3)
        cv2.rectangle(img, (1100, int(bar)), (1175, 650), color, cv2.FILLED)
        cv2.putText(img, f'{int(per)}%', (1120, 75), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

        # Count display
        cv2.rectangle(img, (0, 450), (250, 720), (245, 117, 16), cv2.FILLED)
        cv2.putText(img, str(int(self.count)), (45, 670), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 255, 255), 25)
        cv2.putText(img, "REPS", (40, 560), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 5)

        # Arm selection buttons
        self.draw_button(img, self.button_left, 'Left Arm', self.active_arm == 'left')
        self.draw_button(img, self.button_right, 'Right Arm', self.active_arm == 'right')

        # Show switching indicator
        if time.time() - self.last_switch_time < self.switch_delay:
            cv2.putText(img, "Switching...", (500, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    def draw_button(self, img, button, text, is_active):
        """Draw a button with text"""
        color = (0, 255, 0) if is_active else (200, 200, 200)
        cv2.rectangle(img, (button['x1'], button['y1']), (button['x2'], button['y2']), color, cv2.FILLED)
        cv2.putText(img, text, (button['x1'] + 10, button['y1'] + 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

    def show_fps(self, img):
        """Display FPS on the frame"""
        cTime = time.time()
        fps = 1 / (cTime - self.pTime) if (cTime - self.pTime) > 0 else 60
        self.pTime = cTime
        cv2.putText(img, f'FPS: {int(fps)}', (1100, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        return img

    def draw_basic_ui(self, img):
        """Draw basic UI when no pose is detected"""
        # Count display
        cv2.rectangle(img, (0, 450), (250, 720), (245, 117, 16), cv2.FILLED)
        cv2.putText(img, str(int(self.count)), (45, 670), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 255, 255), 25)
        cv2.putText(img, "REPS", (40, 560), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 5)

        # Arm selection buttons
        self.draw_button(img, self.button_left, 'Left Arm', self.active_arm == 'left')
        self.draw_button(img, self.button_right, 'Right Arm', self.active_arm == 'right')

        # Show switching indicator
        if time.time() - self.last_switch_time < self.switch_delay:
            cv2.putText(img, "Switching...", (500, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # Show instruction text
        cv2.putText(img, "Position yourself to start exercise", (400, 300),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

    def handle_click(self, lmlist, fingers):
        """Handle hand gesture clicks for UI interaction - optimized version"""
        current_time = time.time()

        # Skip if too soon after last switch
        if (current_time - self.last_switch_time) < self.switch_delay:
            return

        switch_arm = False

        try:
            # Check button clicks with bounds checking
            if len(lmlist) > 8:
                finger_tip_x, finger_tip_y = lmlist[8][1], lmlist[8][2]

                # Check left button
                if (self.button_left['x1'] < finger_tip_x < self.button_left['x2'] and
                        self.button_left['y1'] < finger_tip_y < self.button_left['y2']):
                    if fingers[1] == 1:  # Index finger up
                        switch_arm = True
                        self.active_arm = 'left'

                # Check right button
                elif (self.button_right['x1'] < finger_tip_x < self.button_right['x2'] and
                      self.button_right['y1'] < finger_tip_y < self.button_right['y2']):
                    if fingers[1] == 1:  # Index finger up
                        switch_arm = True
                        self.active_arm = 'right'

                # Gesture to switch arms (peace sign or thumbs up)
                elif fingers == [1, 0, 0, 0, 1] or fingers == [0, 0, 0, 0, 1]:
                    switch_arm = True
                    self.active_arm = 'right' if self.active_arm == 'left' else 'left'

            # Apply switch
            if switch_arm:
                self.last_switch_time = current_time
                print(f"Arm switched to: {self.active_arm}")

        except Exception as e:
            print(f"Error in handle_click: {e}")

    def handle_key_press(self, data):
        """Handle key press events from the client"""
        key = data.get('key', '').lower()
        print(f"Fitness tracker received key: {key}")

        if key == 'r':
            self.reset_counter()
            print("Counter reset")
        elif key == 's':
            # Switch arms
            self.active_arm = 'right' if self.active_arm == 'left' else 'left'
            self.last_switch_time = time.time()
            print(f"Arm switched to: {self.active_arm}")
        elif key == 'h':
            # Toggle hand detection for performance
            self.hand_detection_enabled = not self.hand_detection_enabled
            print(f"Hand detection {'enabled' if self.hand_detection_enabled else 'disabled'}")
        elif key == 'q':
            self.stop()

    def reset_counter(self):
        """Reset the rep counter"""
        self.count = 0
        self.dir = 0
        print("Rep counter reset")

    def stop(self):
        """Stop the fitness tracker"""
        self.is_running = False
        print("Fitness tracker stopped")

    def get_stats(self):
        """Get current statistics"""
        return {
            'count': int(self.count),
            'active_arm': self.active_arm,
            'is_running': self.is_running
        }