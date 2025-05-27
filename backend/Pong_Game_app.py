import cv2
import cvzone
import numpy as np
import time
import os
import random
from cvzone.HandTrackingModule import HandDetector
import threading
from collections import deque


class PongGame:
    def __init__(self):
        # Initialize camera
        self.cam = cv2.VideoCapture(0)
        self.cam.set(3, 1280)
        self.cam.set(4, 720)

        # Set up paths
        self.project_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
        self.folder = os.path.join(self.project_root, 'Images', 'Game_Resources')

        # Load game resources
        self.img_background = self.load_image('Background.png')
        self.img_game_over = self.load_image('gameOver.png')
        self.img_ball = self.load_image('Ball.png', alpha=True)
        self.img_bat1 = self.load_image('bat1.png', alpha=True)
        self.img_bat2 = self.load_image('bat2.png', alpha=True)

        # Game state variables
        self.ball_pos = [100, 100]
        self.speed_x = 20
        self.speed_y = 20
        self.score = [0, 0]
        self.game_over = False
        self.is_running = True

        # Countdown variables
        self.countdown_active = False
        self.countdown_time = 3
        self.countdown_start = 0
        self.countdownFlag = False

        # Hand detector with optimized settings for performance
        self.detector = HandDetector(detectionCon=0.6, maxHands=2)
        self.last_frame = None

        # Powerup variables
        self.powerup_active = False
        self.powerup_timer = 0
        self.powerup_hand = None
        self.powerup_timer2 = 0

        # Performance optimization variables
        self.frame_skip_counter = 0
        self.last_hands = []
        self.last_hand_time = time.time()
        self.hand_detection_interval = 0.1  # Detect hands every 100ms instead of every frame

        # Frame rate control
        self.target_fps = 30
        self.frame_time = 1.0 / self.target_fps
        self.last_process_time = time.time()

        # Threading for hand detection
        self.hand_detection_thread = None
        self.hand_detection_active = False
        self.current_hands = []
        self.hands_lock = threading.Lock()
        self.frame_queue = deque(maxlen=2)  # Keep only latest frames

        # Performance monitoring
        self.frame_count = 0
        self.fps_start_time = time.time()
        self.current_fps = 0

    def load_image(self, filename, alpha=False):
        """Load image with fallback to placeholder if file doesn't exist"""
        full_path = os.path.join(self.folder, filename)

        # Create a fallback image if the file doesn't exist
        if not os.path.exists(full_path):
            print(f"Warning: Image not found: {full_path}")
            if alpha:
                # Create a transparent placeholder image
                if filename == 'Ball.png':
                    img = np.zeros((50, 50, 4), dtype=np.uint8)
                    cv2.circle(img, (25, 25), 20, (255, 255, 255, 255), -1)
                elif 'bat' in filename:
                    img = np.zeros((100, 20, 4), dtype=np.uint8)
                    img[:, :, :3] = (255, 255, 255)
                    img[:, :, 3] = 255
                else:
                    img = np.zeros((100, 100, 4), dtype=np.uint8)
                    img[:, :, 3] = 255
            else:
                if filename == 'Background.png':
                    # Create a simple game background
                    img = np.zeros((720, 1280, 3), dtype=np.uint8)
                    # Draw center line
                    cv2.line(img, (640, 0), (640, 720), (255, 255, 255), 5)
                    # Draw borders
                    cv2.rectangle(img, (0, 0), (1280, 720), (255, 255, 255), 5)
                elif filename == 'gameOver.png':
                    # Create game over screen
                    img = np.zeros((720, 1280, 3), dtype=np.uint8)
                    cv2.putText(img, "GAME OVER", (400, 300), cv2.FONT_HERSHEY_COMPLEX, 3, (0, 0, 255), 5)
                    cv2.putText(img, "Press 'R' to restart", (450, 400), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255),
                                2)
                    cv2.putText(img, "Final Score:", (500, 500), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                else:
                    img = np.zeros((720, 1280, 3), dtype=np.uint8)
                    cv2.putText(img, f"Missing: {filename}", (50, 360), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            return img

        if alpha:
            img = cv2.imread(full_path, cv2.IMREAD_UNCHANGED)
            if img is None:
                # Fallback for failed load
                img = np.zeros((100, 100, 4), dtype=np.uint8)
                img[:, :, 3] = 255
        else:
            img = cv2.imread(full_path)
            if img is None:
                # Fallback for failed load
                img = np.zeros((720, 1280, 3), dtype=np.uint8)

        return img

    def hand_detection_worker(self):
        """Background thread worker for hand detection"""
        while self.hand_detection_active:
            try:
                if len(self.frame_queue) > 0:
                    frame = self.frame_queue[-1]  # Get latest frame
                    hands, _ = self.detector.findHands(frame, draw=False, flipType=False)

                    with self.hands_lock:
                        self.current_hands = hands if hands else []

                # Control detection frequency
                time.sleep(self.hand_detection_interval)

            except Exception as e:
                print(f"Hand detection error: {e}")
                time.sleep(0.1)

    def start_hand_detection_thread(self):
        """Start the background hand detection thread"""
        if self.hand_detection_thread is None or not self.hand_detection_thread.is_alive():
            self.hand_detection_active = True
            self.hand_detection_thread = threading.Thread(target=self.hand_detection_worker, daemon=True)
            self.hand_detection_thread.start()

    def stop_hand_detection_thread(self):
        """Stop the background hand detection thread"""
        self.hand_detection_active = False
        if self.hand_detection_thread and self.hand_detection_thread.is_alive():
            self.hand_detection_thread.join(timeout=1.0)

    def reset(self):
        """Reset game state"""
        self.ball_pos = [100, 100]
        self.speed_x = 25
        self.speed_y = 25
        self.score = [0, 0]
        self.game_over = False
        self.countdownFlag = False
        self.countdown_active = False
        self.countdown_time = 3
        self.countdown_start = 0
        self.powerup_active = False
        self.powerup_timer = 0
        self.powerup_hand = None
        self.powerup_timer2 = 0

        # Reset performance variables
        self.frame_skip_counter = 0
        self.last_hands = []
        self.last_hand_time = time.time()
        self.last_process_time = time.time()
        self.frame_count = 0
        self.fps_start_time = time.time()

        print("Game reset!")

    def start_countdown(self):
        """Start the countdown timer"""
        self.countdown_active = True
        self.countdown_time = 3
        self.countdown_start = time.time()

    def update_countdown(self):
        """Update countdown timer"""
        if not self.countdown_active:
            return

        elapsed = time.time() - self.countdown_start
        remaining = 3 - int(elapsed)

        if remaining <= 0:
            self.countdown_active = False
            self.countdownFlag = True
        else:
            self.countdown_time = remaining

    def draw_bats(self, img, hands):
        """Draw player bats based on hand positions"""
        for hand in hands:
            x, y, w, h = hand['bbox']
            h1, w1 = self.img_bat1.shape[:2]
            y1 = y - h1 // 2
            y1 = np.clip(y1, 20, 415)

            if hand['type'] == 'Left':
                if self.powerup_hand == 'Left':
                    # Double bat for powerup
                    img = cvzone.overlayPNG(img, self.img_bat1, (59, y1))
                    img = cvzone.overlayPNG(img, self.img_bat1, (59, y1 + (h1 - 30)))
                    # Collision detection for double bat
                    if 59 - 10 < self.ball_pos[0] < 59 + w1 and y1 - (h1 // 2) < self.ball_pos[1] < y1 + (h1 * 2):
                        self.speed_x = abs(self.speed_x)  # Ensure ball goes right
                        self.ball_pos[0] = 59 + w1 + 5  # Move ball away from bat
                        self.score[0] += 1
                else:
                    # Normal bat
                    img = cvzone.overlayPNG(img, self.img_bat1, (59, y1))
                    # Collision detection
                    if 59 - 10 < self.ball_pos[0] < 59 + w1 and y1 - (h1 // 2) < self.ball_pos[1] < y1 + (h1 // 2):
                        self.speed_x = abs(self.speed_x)  # Ensure ball goes right
                        self.ball_pos[0] = 59 + w1 + 5  # Move ball away from bat
                        self.score[0] += 1

            if hand['type'] == 'Right':
                if self.powerup_hand == 'Right':
                    # Double bat for powerup
                    img = cvzone.overlayPNG(img, self.img_bat2, (1195, y1))
                    img = cvzone.overlayPNG(img, self.img_bat2, (1195, y1 + (h1 - 30)))
                    # Collision detection for double bat
                    if 1120 < self.ball_pos[0] < 1170 + w1 and y1 - (h1 // 2) < self.ball_pos[1] < y1 + (h1 * 2):
                        self.speed_x = -abs(self.speed_x)  # Ensure ball goes left
                        self.ball_pos[0] = 1120 - 5  # Move ball away from bat
                        self.score[1] += 1
                else:
                    # Normal bat
                    img = cvzone.overlayPNG(img, self.img_bat2, (1195, y1))
                    # Collision detection
                    if 1120 < self.ball_pos[0] < 1170 + w1 and y1 - (h1 // 2) < self.ball_pos[1] < y1 + (h1 // 2):
                        self.speed_x = -abs(self.speed_x)  # Ensure ball goes left
                        self.ball_pos[0] = 1120 - 5  # Move ball away from bat
                        self.score[1] += 1

        return img

    def calculate_fps(self):
        """Calculate and update current FPS"""
        self.frame_count += 1
        current_time = time.time()
        elapsed = current_time - self.fps_start_time

        if elapsed >= 1.0:  # Update FPS every second
            self.current_fps = self.frame_count / elapsed
            self.frame_count = 0
            self.fps_start_time = current_time

    def process_frame(self, frame):
        """Process a single frame - main method called by the backend"""
        if not self.is_running:
            return self.last_frame if self.last_frame is not None else np.zeros((720, 1280, 3), np.uint8)

        # Frame rate control - skip processing if too soon
        current_time = time.time()
        if current_time - self.last_process_time < self.frame_time:
            return self.last_frame if self.last_frame is not None else np.zeros((720, 1280, 3), np.uint8)

        self.last_process_time = current_time

        # Calculate FPS
        self.calculate_fps()

        # Use the provided frame instead of capturing from camera
        img = frame.copy()
        img = cv2.flip(img, 1)
        img = cv2.resize(img, (1280, 720))  # Ensure consistent size
        img_raw = img.copy()

        # Start hand detection thread if not already running
        if not self.hand_detection_active:
            self.start_hand_detection_thread()

        # Add frame to queue for hand detection
        self.frame_queue.append(img_raw.copy())

        # Get current hands from background thread
        with self.hands_lock:
            hands = self.current_hands.copy()

        # Add background
        img = cv2.addWeighted(img, 0.2, self.img_background, 0.8, 0)

        # Handle countdown
        if not self.countdownFlag:
            if not self.countdown_active:
                self.start_countdown()
            self.update_countdown()

            if self.countdown_active:
                cv2.putText(img, str(self.countdown_time), (600, 360), cv2.FONT_HERSHEY_COMPLEX, 5, (0, 255, 0), 10)
            else:
                self.countdownFlag = True  # Countdown finished

        # Draw bats if hands are detected
        if hands:
            img = self.draw_bats(img, hands)

        # Only update game state if countdown is finished
        if self.countdownFlag and not self.game_over:
            # Ball movement
            self.ball_pos[0] += self.speed_x
            self.ball_pos[1] += self.speed_y

            # Ball collision with top and bottom walls
            if self.ball_pos[1] >= 500 or self.ball_pos[1] <= 10:
                self.speed_y *= -1

            # Check for game over (ball out of bounds)
            if self.ball_pos[0] < 10:
                # Player 2 wins
                self.game_over = True
                print(f"Game Over! Player 2 wins with score: {max(self.score)}")
            elif self.ball_pos[0] > 1200:
                # Player 1 wins
                self.game_over = True
                print(f"Game Over! Player 1 wins with score: {max(self.score)}")

        # Draw game elements
        if self.game_over:
            img = self.img_game_over.copy()
            cv2.putText(img, str(max(self.score[0], self.score[1])).zfill(2), (585, 360), cv2.FONT_HERSHEY_COMPLEX, 3,
                        (200, 0, 200), 5)
        else:
            # Draw scores
            cv2.putText(img, str(self.score[0]), (300, 650), cv2.FONT_HERSHEY_COMPLEX, 3, (255, 255, 255), 5)
            cv2.putText(img, str(self.score[1]), (900, 650), cv2.FONT_HERSHEY_COMPLEX, 3, (255, 255, 255), 5)

            # Draw ball
            if self.countdownFlag:  # Only show ball after countdown
                img = cvzone.overlayPNG(img, self.img_ball, self.ball_pos)

        # Show webcam thumbnail (smaller to reduce processing)
        try:
            thumbnail = cv2.resize(img_raw, (160, 90))  # Smaller thumbnail
            img[620:710, 20:180] = thumbnail
        except Exception as e:
            print(f"Thumbnail error: {e}")

        # Add instructions and performance info
        cv2.putText(img, "Press 'R' to reset", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(img, "Use hands as paddles", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(img, f"FPS: {self.current_fps:.1f}", (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(img, f"Hands: {len(hands)}", (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        self.last_frame = img
        return img

    def handle_key_press(self, data):
        """Handle key press events from the frontend"""
        key = data.get('key', '').lower()
        print(f"Pong Game - Key pressed: {key}")

        if key == 'r':
            self.reset()
        elif key == 'q':
            self.stop()
        elif key == 'p':
            # Toggle powerup for testing
            if self.powerup_active:
                self.powerup_active = False
                self.powerup_hand = None
                self.powerup_timer = 0
                print("Powerup deactivated")
            else:
                self.powerup_active = True
                self.powerup_hand = 'Left'  # Default to left hand
                self.powerup_timer = time.time()
                print("Powerup activated for Left hand")

    def stop(self):
        """Stop the game and cleanup resources"""
        print("Stopping Pong Game...")
        self.is_running = False

        # Stop hand detection thread
        self.stop_hand_detection_thread()

        if hasattr(self, 'cam') and self.cam and self.cam.isOpened():
            self.cam.release()


# Example usage and testing
if __name__ == "__main__":
    # This section is for testing the PongGame class independently
    game = PongGame()

    # Test with webcam
    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)
    cap.set(4, 720)

    print("Testing Optimized Pong Game - Press 'q' to quit, 'r' to reset")

    try:
        while True:
            success, frame = cap.read()
            if not success:
                break

            processed_frame = game.process_frame(frame)

            cv2.imshow("Pong Game Test", processed_frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                game.handle_key_press({'key': 'r'})
            elif key == ord('p'):
                game.handle_key_press({'key': 'p'})

    except KeyboardInterrupt:
        print("Interrupted by user")
    finally:
        game.stop()
        cap.release()
        cv2.destroyAllWindows()