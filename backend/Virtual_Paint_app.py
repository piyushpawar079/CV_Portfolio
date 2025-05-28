import cv2
import os
import numpy as np
import time
import math
from cvzone.HandTrackingModule import HandDetector
from threading import Lock


class VirtualPainter:
    def __init__(self):
        # Reduce detection confidence for better performance
        self.detector = HandDetector(detectionCon=0.6, maxHands=2)

        # Define standard header dimensions
        self.HEADER_HEIGHT = 104
        self.HEADER_WIDTH = 1007

        # Try to load header images from Images folder
        self.project_root = os.path.abspath(os.path.dirname(__file__))
        self.folder = os.path.join(self.project_root, 'Images')

        # Create default header if folder doesn't exist
        if not os.path.exists(self.folder):
            os.makedirs(self.folder, exist_ok=True)
            # Create default headers
            self.header = self.create_default_header()
            self.header_images = [self.header]
        else:
            try:
                # Load and resize all header images to standard dimensions
                self.header_images = []
                for img_name in os.listdir(self.folder):
                    img_path = os.path.join(self.folder, img_name)
                    img = cv2.imread(img_path)
                    if img is not None:
                        # Resize to standard header dimensions
                        img_resized = cv2.resize(img, (self.HEADER_WIDTH, self.HEADER_HEIGHT), 
                                               interpolation=cv2.INTER_AREA)
                        self.header_images.append(img_resized)

                if not self.header_images:
                    self.header = self.create_default_header()
                    self.header_images = [self.header]
                else:
                    self.header = self.header_images[0]
            except Exception as e:
                print(f"Error loading header images: {e}")
                self.header = self.create_default_header()
                self.header_images = [self.header]

        # Initialize the canvas
        self.img_canvas = np.zeros((720, 1280, 3), np.uint8)

        # Drawing parameters
        self.xp, self.yp = 0, 0
        self.brush_thickness = 30
        self.eraser_thickness = 100
        self.color1 = (255, 192, 203)  # Default brush color
        self.color2 = self.color3 = (0, 0, 0)
        self.selected = ''

        # Feature flags
        self.circle_flag = False
        self.done = False
        self.doneL = False
        self.line_flag = False
        self.show_options = False
        self.lm_list = []

        # Shape properties
        self.circle_x1, self.circle_y1, self.radius = 0, 0, 0
        self.line_start, self.line_end = (0, 0), (0, 0)

        # Brush size control
        self.brush_size = 15
        self.min_brush_size = 5
        self.max_brush_size = 50

        # Undo functionality - limit states to reduce memory usage
        self.canvas_states = []
        self.max_states = 20  # Reduced from 70
        self.undo_button_active = False

        # Fill options
        self.fill_type = None
        self.fill_start_angle = 0
        self.fill_end_angle = 0

        # Tracking
        self.last_hand_detected_time = 0
        self.hand_detection_timeout = 0.5
        self.last_frame = None
        self.last_processed_time = time.time()
        self.processing_fps = 30  # Target FPS for processing
        self.min_processing_interval = 1.0 / self.processing_fps

        # Thread-safe flag for running
        self.is_running = True
        self.lock = Lock()  # Add a lock for thread safety

        # Skip counter for performance optimization
        self.skip_frames = 0
        self.max_skip_frames = 1  # Process every other frame

    def create_default_header(self):
        """Create a default header with drawing tools"""
        # Use the standard dimensions
        header = np.zeros((self.HEADER_HEIGHT, self.HEADER_WIDTH, 3), np.uint8)
        header[:] = (50, 50, 50)  # Dark gray background

        # Pink brush
        cv2.rectangle(header, (10, 10), (100, 90), (255, 192, 203), -1)
        cv2.putText(header, "Pink", (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

        # Red brush
        cv2.rectangle(header, (200, 10), (300, 90), (0, 0, 255), -1)
        cv2.putText(header, "Red", (230, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # Circle tool
        cv2.rectangle(header, (450, 10), (550, 90), (255, 0, 255), -1)
        cv2.putText(header, "Circle", (465, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # Line tool
        cv2.rectangle(header, (600, 10), (700, 90), (0, 255, 0), -1)
        cv2.putText(header, "Line", (625, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

        # Eraser
        cv2.rectangle(header, (800, 10), (900, 90), (0, 0, 0), -1)
        cv2.putText(header, "Eraser", (815, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        return header

    def process_frame(self, img):
        """Process a frame with hand detection for virtual painting"""
        if not self.is_running:
            return self.last_frame if self.last_frame is not None else np.zeros((720, 1280, 3), np.uint8)

        if img is None:
            return self.last_frame if self.last_frame is not None else np.zeros((720, 1280, 3), np.uint8)

        # Skip frames for better performance
        current_time = time.time()
        if current_time - self.last_processed_time < self.min_processing_interval:
            return self.last_frame

        # Increment skip counter
        self.skip_frames += 1
        if self.skip_frames < self.max_skip_frames:
            # Return the last processed frame without doing heavy processing
            return self.last_frame if self.last_frame is not None else img

        # Reset skip counter
        self.skip_frames = 0
        self.last_processed_time = current_time

        # Flip the image horizontally for a more intuitive mirror view
        img = cv2.flip(img, 1)

        # Create a copy for drawing UI elements
        ui_layer = img.copy()

        # Find hands in the frame - use a lighter version if no hands were detected recently
        if current_time - self.last_hand_detected_time > 1.0:
            # Quick check first (faster)
            hands_check, _ = self.detector.findHands(img, draw=False, flipType=False)
            if hands_check:
                # If hands are found, do the full detection
                hands, img = self.detector.findHands(img, flipType=False)
            else:
                hands = []
        else:
            # Full detection when we expect hands to be present
            hands, img = self.detector.findHands(img, flipType=False)

        # Draw UI elements
        self.draw_undo_button(ui_layer)
        self.draw_brush_slider(ui_layer)

        if hands:
            self.last_hand_detected_time = current_time

            with self.lock:  # Thread safety for hand processing
                if hands and len(hands) > 0 and "lmList" in hands[0]:
                    self.lm_list = hands[0]["lmList"]
                    if self.lm_list:
                        self.process_hand_gestures(ui_layer, hands)

                        # Menu and options logic
                        if len(self.lm_list) > 8:  # Make sure we have enough landmarks
                            x1, y1 = self.lm_list[8][0], self.lm_list[8][1]  # Index finger tip

                            # Show fill options if needed
                            if self.show_options:
                                ui_layer = self.draw_options(ui_layer)

                            # Fill preview
                            if self.fill_type:
                                cv2.ellipse(ui_layer, (self.circle_x1, self.circle_y1), (self.radius, self.radius),
                                            0, self.fill_start_angle, self.fill_end_angle, self.color2, 2)
        else:
            if current_time - self.last_hand_detected_time > self.hand_detection_timeout:
                self.xp, self.yp = 0, 0

        # Canvas rendering - optimize by doing this less frequently
        img_gray = cv2.cvtColor(self.img_canvas, cv2.COLOR_BGR2GRAY)
        _, img_inv = cv2.threshold(img_gray, 50, 255, cv2.THRESH_BINARY_INV)
        img_inv = cv2.cvtColor(img_inv, cv2.COLOR_GRAY2BGR)

        # Combine layers efficiently
        result = cv2.bitwise_and(img, img_inv)
        result = cv2.bitwise_or(result, self.img_canvas)

        # Apply UI layer
        alpha = 0.7
        cv2.addWeighted(result, alpha, ui_layer, 1 - alpha, 0, result)

        # Add header - ensure dimensions match exactly
        if self.header.shape == (self.HEADER_HEIGHT, self.HEADER_WIDTH, 3):
            result[:self.HEADER_HEIGHT, :self.HEADER_WIDTH] = self.header
        else:
            # If header dimensions don't match, resize it
            header_resized = cv2.resize(self.header, (self.HEADER_WIDTH, self.HEADER_HEIGHT), 
                                      interpolation=cv2.INTER_AREA)
            result[:self.HEADER_HEIGHT, :self.HEADER_WIDTH] = header_resized

        self.last_frame = result
        return result

    def process_hand_gestures(self, img, hands):
        """Process hand gestures to determine actions"""
        if not self.lm_list or len(self.lm_list) < 12:
            return

        # Get finger positions
        x1, y1 = self.lm_list[8][0], self.lm_list[8][1]  # Index finger tip
        x2, y2 = self.lm_list[12][0], self.lm_list[12][1]  # Middle finger tip

        # Check finger states - this is an expensive operation
        try:
            fingers = self.detector.fingersUp(hands[0])

            if fingers[1] and fingers[2]:  # Selection mode (index and middle finger up)
                self.xp, self.yp = 0, 0
                if 1090 < x1 < 1180 and 10 < y1 < 60 and self.undo_button_active:
                    self.undo()
                elif 130 < y1 < 160:
                    self.adjust_brush_size(x1)
                elif x1 < 1000:
                    self.select_tool(x1, y1, x2, y2, img)
            elif fingers[1] and not fingers[2]:  # Drawing mode (only index finger up)
                if self.show_options:
                    self.select_fill_option(x1, y1)
                elif self.fill_type:
                    self.select_fill_area(x1, y1, img)
                else:
                    self.draw_on_canvas(img, hands)
            elif not fingers[1] and not fingers[2]:  # Complete fill operation
                if self.fill_type:
                    self.apply_selected_fill()
                    self.save_canvas_state()
                self.xp, self.yp = 0, 0
            else:
                self.xp, self.yp = 0, 0
        except Exception as e:
            print(f"Error in processing hand gestures: {e}")
            self.xp, self.yp = 0, 0

    def draw_brush_slider(self, img):
        """Draw the brush size slider"""
        cv2.rectangle(img, (10, 130), (260, 160), (200, 200, 200), -1)
        cv2.rectangle(img, (10, 130), (
            10 + int(250 * (self.brush_size - self.min_brush_size) / (self.max_brush_size - self.min_brush_size)), 160),
                      (0, 255, 0), -1)
        cv2.putText(img, f"Brush Size: {self.brush_size}", (10, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    def adjust_brush_size(self, x):
        """Adjust brush size based on slider position"""
        if 10 <= x <= 260:
            self.brush_size = int(self.min_brush_size + (x - 10) * (self.max_brush_size - self.min_brush_size) / 250)
            self.brush_thickness = self.brush_size

    def save_canvas_state(self):
        """Save the current canvas state for undo functionality"""
        # Only save state periodically to reduce overhead
        current_time = time.time()
        if not hasattr(self, 'last_save_time') or current_time - self.last_save_time > 0.5:
            if len(self.canvas_states) >= self.max_states:
                self.canvas_states.pop(0)
            self.canvas_states.append(self.img_canvas.copy())
            self.undo_button_active = True
            self.last_save_time = current_time

    def undo(self):
        """Undo the last drawing action"""
        if len(self.canvas_states) > 0:
            self.img_canvas = self.canvas_states.pop()
        if len(self.canvas_states) == 0:
            self.undo_button_active = False

    def draw_undo_button(self, img):
        """Draw the undo button on the interface"""
        if self.undo_button_active:
            cv2.rectangle(img, (1090, 10), (1180, 60), (0, 255, 0), -1)
            cv2.putText(img, "Undo", (1105, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        else:
            cv2.rectangle(img, (1090, 10), (1180, 60), (200, 200, 200), -1)
            cv2.putText(img, "Undo", (1105, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 100, 100), 2)

    def select_fill_option(self, x, y):
        """Select a fill option for the circle"""
        if 900 < x < 1250:
            if 100 < y < 200:
                self.fill_type = "full"
            elif 200 < y < 300:
                self.fill_type = "half"
            elif 300 < y < 400:
                self.fill_type = "quarter"

            if self.fill_type:
                self.show_options = False

    def select_fill_area(self, x, y, img):
        """Select fill area and parameters"""
        dx = x - self.circle_x1
        dy = self.circle_y1 - y  # Invert y-axis
        angle = math.degrees(math.atan2(dy, dx))
        if angle < 0:
            angle += 360

        if self.fill_type == "full":
            self.fill_start_angle = 0
            self.fill_end_angle = 360
        elif self.fill_type == "half":
            self.fill_start_angle = angle
            self.fill_end_angle = (angle + 180) % 360
        elif self.fill_type == "quarter":
            self.fill_start_angle = angle
            self.fill_end_angle = (angle + 90) % 360

        # Just preview the selection for now, don't render to canvas yet
        cv2.ellipse(img, (self.circle_x1, self.circle_y1), (self.radius, self.radius),
                    0, self.fill_start_angle, self.fill_end_angle, self.color2, 2)

    def apply_selected_fill(self):
        """Apply the selected fill to the circle"""
        if self.fill_type:
            mask = np.zeros(self.img_canvas.shape[:2], dtype=np.uint8)
            cv2.ellipse(mask, (self.circle_x1, self.circle_y1), (self.radius, self.radius),
                        0, self.fill_start_angle, self.fill_end_angle, 255, -1)
            self.img_canvas[mask == 255] = self.color2
            self.fill_type = None  # Reset fill type after applying

    def draw_options(self, img):
        """Draw fill options menu"""
        overlay = img.copy()
        cv2.rectangle(overlay, (900, 100), (1250, 400), (50, 50, 50), -1)  # Options background
        cv2.putText(overlay, "Fill full circle", (920, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(overlay, "Fill half circle", (920, 250), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(overlay, "Fill quarter circle", (920, 350), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # Blend the overlay with the original image
        img = cv2.addWeighted(overlay, 0.7, img, 0.3, 0)
        return img

    def select_tool(self, x1, y1, x2, y2, img):
        """Select drawing tool based on position"""
        if y1 < 130:
            if 10 < x1 < 100:  # Pink brush
                self.header = self.header_images[0]
                self.color1 = (255, 192, 203)
                self.color2 = (0, 0, 255)
                self.color3 = (255, 192, 203)
                self.selected = 'brush1'
            elif 200 < x1 < 300:  # Red brush
                if len(self.header_images) > 1:
                    # Ensure the header is properly resized
                    self.header = cv2.resize(self.header_images[1], (self.HEADER_WIDTH, self.HEADER_HEIGHT), 
                                           interpolation=cv2.INTER_AREA)
                else:
                    # Use default header if no second image available
                    self.header = self.header_images[0]
                self.color1 = (0, 0, 255)
                self.color2 = (0, 0, 255)
                self.color3 = (0, 0, 255)
                self.selected = 'brush2'
            elif 450 < x1 < 550:  # Circle tool
                self.select_circle()
            elif 600 < x1 < 700:  # Line tool
                self.select_line()
            elif 800 < x1 < 900:  # Eraser
                self.color1 = (0, 0, 0)
                self.color2 = (0, 0, 255)
                self.selected = 'eraser'

        cv2.line(img, (x1, y1), (x2, y2), self.color3, 3)

    def select_circle(self):
        """Select circle drawing tool"""
        self.color2 = (0, 0, 0)
        self.color1 = (0, 0, 0)
        self.color3 = (255, 0, 255)
        self.selected = 'circle'
        self.circle_flag = True
        self.done = False

    def select_line(self):
        """Select line drawing tool"""
        self.color2 = (0, 0, 0)
        self.color1 = (0, 0, 0)
        self.color3 = (0, 255, 0)
        self.selected = 'line'
        self.line_flag = True
        self.doneL = False

    def draw_line(self, x1, y1, img):
        """Draw a brush line"""
        cv2.line(img, (self.xp, self.yp), (x1, y1), self.color1, self.brush_thickness)
        cv2.line(self.img_canvas, (self.xp, self.yp), (x1, y1), self.color1, self.brush_thickness)

    def draw_eraser(self, x1, y1, img):
        """Draw with eraser (black)"""
        cv2.line(img, (self.xp, self.yp), (x1, y1), self.color1, self.eraser_thickness)
        cv2.line(self.img_canvas, (self.xp, self.yp), (x1, y1), self.color1, self.eraser_thickness)

    def draw_circle(self, x1, y1, img, hands):
        """Draw a circle with two hands"""
        if len(hands) == 2 and self.circle_flag:
            self.circle_x1, self.circle_y1 = x1, y1
            hand2_lmlist = hands[1]["lmList"] if "lmList" in hands[1] else []

            if hand2_lmlist and len(hand2_lmlist) > 8:
                thumbX, thumbY = hand2_lmlist[8][0], hand2_lmlist[8][1]
                self.radius = int(((thumbX - x1) ** 2 + (thumbY - y1) ** 2) ** 0.5)

                if len(self.lm_list) > 4:
                    x3, y3 = self.lm_list[4][0], self.lm_list[4][1]  # Thumb tip
                    length = int(((x3 - x1) ** 2 + (y3 - y1) ** 2) ** 0.5)

                    if length < 160:
                        self.circle_flag = False
                        self.done = True
                        self.show_options = True
                        self.color2 = (255, 0, 0)
                        cv2.circle(img, (self.circle_x1, self.circle_y1), self.radius, self.color2, 5)
                        cv2.circle(self.img_canvas, (self.circle_x1, self.circle_y1), self.radius, self.color2, 5)

        if not self.done:
            cv2.circle(img, (self.circle_x1, self.circle_y1), self.radius, self.color2, 5)
            cv2.circle(self.img_canvas, (self.circle_x1, self.circle_y1), self.radius, self.color2, 5)

    def draw_line_shape(self, x1, y1, img, hands):
        """Draw a straight line with two hands"""
        if len(hands) == 2 and self.line_flag:
            self.line_start = (x1, y1)
            hand2_lmlist = hands[1]["lmList"] if "lmList" in hands[1] else []

            if hand2_lmlist and len(hand2_lmlist) > 8:
                self.line_end = (hand2_lmlist[8][0], hand2_lmlist[8][1])

                if len(self.lm_list) > 4:
                    x3, y3 = self.lm_list[4][0], self.lm_list[4][1]  # Thumb tip
                    length = int(((x3 - x1) ** 2 + (y3 - y1) ** 2) ** 0.5)

                    if length < 160:
                        self.line_flag = False
                        self.doneL = True
                        self.color2 = (255, 0, 0)
                        cv2.line(img, self.line_start, self.line_end, self.color2, 5)
                        cv2.line(self.img_canvas, self.line_start, self.line_end, self.color2, 5)

        if not self.doneL:
            cv2.line(img, self.line_start, self.line_end, self.color2, 5)
            cv2.line(self.img_canvas, self.line_start, self.line_end, self.color2, 5)

    def draw_on_canvas(self, img, hands):
        """Handle drawing on the canvas with finger movements"""
        if not self.lm_list or len(self.lm_list) < 8:
            return

        x1, y1 = self.lm_list[8][0], self.lm_list[8][1]  # Index finger tip
        cv2.circle(img, (x1, y1), 10, (255, 255, 255), -1)

        # Check if the finger was just lowered
        if self.xp == 0 and self.yp == 0:
            self.xp, self.yp = x1, y1
            return  # Don't draw a dot

        # Calculate the distance between current and previous point
        distance = ((x1 - self.xp) ** 2 + (y1 - self.yp) ** 2) ** 0.5

        # If the distance is too large, assume the finger was lifted and reset the previous point
        if distance > 50:  # Threshold for gap in drawing
            self.xp, self.yp = x1, y1
            return

        if self.selected == 'brush1' or self.selected == 'brush2':
            self.draw_line(x1, y1, img)
        elif self.selected == 'eraser':
            self.draw_eraser(x1, y1, img)
        elif self.selected == 'circle':
            self.draw_circle(x1, y1, img, hands)
        elif self.selected == 'line':
            self.draw_line_shape(x1, y1, img, hands)

        self.xp, self.yp = x1, y1

        # Don't save canvas state on every draw operation
        # Only save periodically through the throttled save_canvas_state method
        self.save_canvas_state()

    def handle_key_press(self, data):
        """Handle key press events"""
        key = data.get('key')
        if key == 'c':  # Clear canvas
            self.img_canvas = np.zeros((720, 1280, 3), np.uint8)
            self.canvas_states = []
            self.undo_button_active = False
        elif key == 'z' and (data.get('ctrl') or data.get('meta')):  # Ctrl+Z for undo
            self.undo()

    def stop(self):
        """Stop the painter app"""
        self.is_running = False

    def reset(self):
        """Reset the canvas and states"""
        self.img_canvas = np.zeros((720, 1280, 3), np.uint8)
        self.canvas_states = []
        self.undo_button_active = False
        self.xp, self.yp = 0, 0
        self.selected = ''
        self.circle_flag = False
        self.line_flag = False
        self.done = False
        self.doneL = False
        self.show_options = False
        self.fill_type = None