import cv2
import time
import numpy as np
from HandGestureDetector import HandDetector
import math
import traceback
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


class VolumeControl:
    def __init__(self, wCam=1280, hCam=720):
        self.wCam = wCam
        self.hCam = hCam
        self.detector = HandDetector(maxHands=1)
        self.volume, self.minVolume, self.maxVolume = self.initialize_volume_control()
        self.selected = 1  # Default to mode 2 (horizontal slider)
        self.pTime = 0
        self.volBar = 400
        self.vol = 0
        self.volPer = 0
        self.volbar1 = 150
        self.volbar2 = 157
        self.is_running = True
        self.current_description = ''
        self.last_mute_time = 0
        self.mute_cooldown = 1.0  # 1 second cooldown for mute toggle

        # Initialize current volume
        try:
            current_vol = self.volume.GetMasterVolumeLevel()
            self.volPer = int(np.interp(current_vol, [self.minVolume, self.maxVolume], [0, 100]))
            self.volBar = np.interp(self.volPer, [0, 100], [400, 150])
            self.volbar1 = int(np.interp(self.volPer, [0, 100], [150, 950]))
            self.volbar2 = self.volbar1 + 7
        except Exception as e:
            print(f"Error initializing volume: {e}")

    @staticmethod
    def initialize_volume_control():
        try:
            device = AudioUtilities.GetSpeakers()
            interface = device.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None
            )
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            minVolume = volume.GetVolumeRange()[0]
            maxVolume = volume.GetVolumeRange()[1]
            return volume, minVolume, maxVolume
        except Exception as e:
            print(f"Error initializing volume control: {e}")
            return None, -65.25, 0.0  # Default values

    @staticmethod
    def draw_hand_landmarks(img, lmlist):
        if len(lmlist) < 9:
            return 0, 0, 0, 0, 0, 0

        x1, y1 = lmlist[4][1], lmlist[4][2]
        x2, y2 = lmlist[8][1], lmlist[8][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
        cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

        return x1, y1, x2, y2, cx, cy

    def update_volume(self, length):
        try:
            vol = np.interp(length, [50, 300], [self.minVolume, self.maxVolume])
            volBar = np.interp(length, [50, 300], [400, 150])
            volPer = int(np.interp(length, [50, 300], [0, 100]) // 5) * 5
            return vol, volBar, volPer
        except Exception as e:
            print(f"Error updating volume: {e}")
            return self.vol, self.volBar, self.volPer

    @staticmethod
    def display_options(img):
        # Mode selection boxes
        cv2.rectangle(img, (100, 100), (200, 200), (0, 0, 0), -1)
        cv2.rectangle(img, (300, 100), (400, 200), (0, 0, 0), -1)
        cv2.putText(img, '1', (130, 160), cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 3)
        cv2.putText(img, '2', (330, 160), cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 3)

        # Mode descriptions
        cv2.putText(img, 'Pinch Control', (80, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(img, 'Slide Control', (280, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    def selected_option(self, fingers, lmList):
        if len(lmList) < 9:
            return self.selected

        x, y = lmList[8][1], lmList[8][2]

        if fingers[1] and 100 < x < 200 and 100 < y < 200:
            return 0
        elif fingers[1] and 300 < x < 400 and 100 < y < 200:
            return 1
        return self.selected

    def display_volume_bar(self, img):
        if not self.selected:
            # Vertical volume bar (Mode 1)
            cv2.rectangle(img, (50, 150), (85, 400), (0, 255, 0), 1)
            cv2.rectangle(img, (50, int(self.volBar)), (85, 400), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, f'{int(self.volPer)}%', (10, 470), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
        else:
            # Horizontal volume bar (Mode 2)
            cv2.rectangle(img, (150, 300), (950, 400), (0, 255, 0), 5)
            cv2.rectangle(img, (150, 300), (self.volbar1, 400), (0, 255, 0), -1)
            cv2.rectangle(img, (self.volbar1, 295), (self.volbar2, 405), (0, 255, 255), -1)
            cv2.putText(img, '0%', (80, 368), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
            cv2.putText(img, '100%', (960, 365), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
            cv2.putText(img, f'{int(self.volPer)}%', (self.volbar1 - 25, 450), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0),
                        2)

    @staticmethod
    def display_fps(img, fps):
        cv2.putText(img, f'FPS: {int(fps)}', (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)

    def toggle_mute(self):
        try:
            current_time = time.time()
            if current_time - self.last_mute_time < self.mute_cooldown:
                return

            self.last_mute_time = current_time

            if self.volume is None:
                return

            current_volume = self.volume.GetMasterVolumeLevel()
            if abs(current_volume - self.minVolume) < 1:  # Currently muted
                # Unmute to 50% volume
                target_vol = np.interp(50, [0, 100], [self.minVolume, self.maxVolume])
                self.volume.SetMasterVolumeLevel(target_vol, None)
                self.volPer = 50
            else:
                # Mute
                self.volume.SetMasterVolumeLevel(self.minVolume, None)
                self.volPer = 0

            # Update visual indicators
            self.volBar = np.interp(self.volPer, [0, 100], [400, 150])
            self.volbar1 = int(np.interp(self.volPer, [0, 100], [150, 950]))
            self.volbar2 = self.volbar1 + 7

        except Exception as e:
            print(f"Error toggling mute: {e}")

    def draw_text_with_background(self, img, text, position, font_scale=0.7, thickness=2):
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]

        # Draw background rectangle
        cv2.rectangle(img,
                      (position[0], position[1] - 25),
                      (position[0] + text_size[0] + 10, position[1] + 10),
                      (0, 0, 0),
                      -1)

        # Draw text
        cv2.putText(img,
                    text,
                    (position[0] + 5, position[1]),
                    font,
                    font_scale,
                    (255, 255, 255),
                    thickness)

    def process_frame(self, frame):
        """Main processing method called by the backend"""
        if not self.is_running or frame is None:
            return None

        try:
            # Resize frame to expected dimensions
            img = cv2.resize(frame, (self.wCam, self.hCam))
            img = cv2.flip(img, 1)

            hands, img = self.detector.findHands(img)
            description = 'Volume Control - Show gestures to control'

            # Always display the mode selection options
            self.display_options(img)

            # Highlight selected mode
            if self.selected == 0:
                cv2.rectangle(img, (98, 98), (202, 202), (0, 255, 0), 3)
            else:
                cv2.rectangle(img, (298, 98), (402, 202), (0, 255, 0), 3)

            if hands and len(hands) > 0:
                lmlist = self.detector.findPosition(img)
                fingers = self.detector.fingersUp(hands[0])

                if len(fingers) >= 5 and len(lmlist) >= 21:
                    # Mode selection gesture (3 fingers up)
                    if fingers[1] and fingers[2] and fingers[3] and not fingers[0] and not fingers[4]:
                        description = 'Mode Selection: Point to option 1 or 2'
                        new_selected = self.selected_option(fingers, lmlist)
                        if new_selected != self.selected:
                            self.selected = new_selected
                            description = f'Switched to Mode {self.selected + 1}'

                    # Volume control gestures
                    elif not self.selected and fingers[1] and not fingers[2]:  # Mode 1: Index finger only
                        description = 'Mode 1: Pinch thumb and index to control volume'
                        x1, y1, x2, y2, cx, cy = self.draw_hand_landmarks(img, lmlist)
                        length = math.hypot(x2 - x1, y2 - y1)

                        if length < 50:
                            cv2.circle(img, (cx, cy), 15, (0, 255, 0), cv2.FILLED)

                        new_vol, new_volBar, new_volPer = self.update_volume(length)

                        # Apply volume change if thumb is also up
                        if fingers[0]:  # Thumb up confirms the volume change
                            try:
                                if self.volume:
                                    self.volume.SetMasterVolumeLevel(new_vol, None)
                                    self.vol = new_vol
                                    self.volBar = new_volBar
                                    self.volPer = new_volPer
                                    description = f'Volume set to {self.volPer}%'
                            except Exception as e:
                                print(f"Error setting volume: {e}")

                    elif self.selected and fingers[1] and fingers[2]:  # Mode 2: Two fingers for sliding
                        description = 'Mode 2: Slide two fingers horizontally to control volume'
                        x11, y11 = lmlist[8][1], lmlist[8][2]

                        if 300 <= y11 <= 400 and 150 <= x11 <= 950:
                            self.volbar1 = int(np.clip(x11, 150, 950))
                            self.volbar2 = self.volbar1 + 7
                            self.volPer = int(np.interp(self.volbar1, [150, 950], [0, 100]) // 5) * 5
                            new_vol = np.interp(self.volbar1, [150, 950], [self.minVolume, self.maxVolume])

                            try:
                                if self.volume:
                                    self.volume.SetMasterVolumeLevel(new_vol, None)
                                    self.vol = new_vol
                                    description = f'Volume: {self.volPer}%'
                            except Exception as e:
                                print(f"Error setting volume: {e}")

                    # Mute gesture (only pinky finger)
                    elif fingers == [0, 0, 0, 0, 1]:
                        description = 'Mute/Unmute Toggle'
                        self.toggle_mute()

                    else:
                        description = 'Available gestures: 3 fingers (mode select), pinch (mode 1), slide (mode 2), pinky (mute)'

            # Display current description
            self.draw_text_with_background(img, description, (10, 40))

            # Display current mode
            mode_text = f'Current Mode: {self.selected + 1} - {"Pinch Control" if not self.selected else "Slide Control"}'
            self.draw_text_with_background(img, mode_text, (10, 80))

            # Display volume bar
            self.display_volume_bar(img)

            # Calculate and display FPS
            cTime = time.time()
            fps = 1 / (cTime - self.pTime) if (cTime - self.pTime) > 0 else 60
            self.pTime = cTime
            self.display_fps(img, fps)

            return img

        except Exception as e:
            print(f"Error in volume control process_frame: {e}")
            traceback.print_exc()
            return frame

    def handle_key_press(self, data):
        """Handle key press events from the frontend"""
        try:
            key = data.get('key', '').lower()

            if key == '1':
                self.selected = 0
                print("Switched to Mode 1 - Pinch Control")
            elif key == '2':
                self.selected = 1
                print("Switched to Mode 2 - Slide Control")
            elif key == 'm':
                self.toggle_mute()
                print("Mute toggled")
            elif key == 'r':
                # Reset volume to 50%
                try:
                    if self.volume:
                        target_vol = np.interp(50, [0, 100], [self.minVolume, self.maxVolume])
                        self.volume.SetMasterVolumeLevel(target_vol, None)
                        self.volPer = 50
                        self.volBar = np.interp(50, [0, 100], [400, 150])
                        self.volbar1 = int(np.interp(50, [0, 100], [150, 950]))
                        self.volbar2 = self.volbar1 + 7
                        print("Volume reset to 50%")
                except Exception as e:
                    print(f"Error resetting volume: {e}")

        except Exception as e:
            print(f"Error handling key press: {e}")

    def stop(self):
        """Clean up resources"""
        self.is_running = False
        print("Volume control stopped")