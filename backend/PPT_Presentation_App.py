import cv2
import numpy as np
import os
import traceback
from cvzone.HandTrackingModule import HandDetector as hd


class PresentationController:
    def __init__(self, wCam=1280, hCam=720):
        self.wCam = wCam
        self.hCam = hCam
        self.detector = hd(maxHands=1)

        # Setup presentation folder and images
        self.project_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
        self.folder = os.path.join(self.project_root, 'Images', 'Presentations')
        # Create directory if it doesn't exist
        os.makedirs(self.folder, exist_ok=True)

        # Get list of images in the folder
        try:
            self.images = [f for f in os.listdir(self.folder)
                           if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff'))]

            if not self.images:
                # Create a default blank slide if no images found
                self.create_default_slides()

            # Sort images for consistent ordering
            self.images.sort()
            print(f"Loaded {len(self.images)} presentation slides")

        except Exception as e:
            print(f"Error loading images: {e}")
            self.create_default_slides()

        self.img_number = 0

        # Controller settings
        self.ws, self.hs = 213, 120  # Webcam preview size
        self.threshold = 425  # Gesture threshold line
        self.buttonPressed = False
        self.buttonCounter = 0
        self.buttonDelay = 15  # Increased delay to prevent rapid switching

        # Annotation variables
        self.annotations = [[]]
        self.annotationsNumber = -1
        self.annotationsFlag = False

        # Status variables
        self.is_running = True

        # Current slide cache
        self.current_slide = None
        self.last_img_number = -1

    def create_default_slides(self):
        """Create default presentation slides if none exist"""
        try:
            # Create a few sample slides
            slides_data = [
                ("Welcome to Presentation Mode", "Use hand gestures to control slides"),
                ("Navigation", "Thumb up: Previous slide\nPinky up: Next slide"),
                ("Drawing", "Index finger: Draw annotations\nTwo fingers: Pointer mode"),
                ("Clear Annotations", "Peace sign (3 fingers): Clear last annotation"),
                ("Keyboard Controls", "Arrow keys: Navigate slides\nC key: Clear all annotations")
            ]

            for i, (title, content) in enumerate(slides_data):
                slide = np.ones((self.hCam, self.wCam, 3), dtype=np.uint8) * 240

                # Add title
                cv2.putText(slide, title, (50, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 50, 100), 3)

                # Add content (handle multiline)
                y_offset = 200
                for line in content.split('\n'):
                    cv2.putText(slide, line, (50, y_offset),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (50, 50, 50), 2)
                    y_offset += 50

                # Add slide number
                cv2.putText(slide, f"Slide {i + 1}", (self.wCam - 200, self.hCam - 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 100, 100), 2)

                filename = f"slide_{i + 1:02d}.jpg"
                cv2.imwrite(os.path.join(self.folder, filename), slide)

            self.images = [f"slide_{i + 1:02d}.jpg" for i in range(len(slides_data))]
            print(f"Created {len(self.images)} default slides")

        except Exception as e:
            print(f"Error creating default slides: {e}")
            self.images = []

    def load_image(self):
        """Load the current presentation slide"""
        try:
            if not self.images:
                return self.create_blank_slide("No slides available")

            # Use cached slide if same slide number
            if self.img_number == self.last_img_number and self.current_slide is not None:
                return self.current_slide.copy()

            current_image_path = os.path.join(self.folder, self.images[self.img_number])

            if not os.path.exists(current_image_path):
                print(f"Image not found: {current_image_path}")
                return self.create_blank_slide(f"Slide {self.img_number + 1} not found")

            img_current = cv2.imread(current_image_path)
            if img_current is None:
                print(f"Failed to load image: {current_image_path}")
                return self.create_blank_slide(f"Failed to load slide {self.img_number + 1}")

            # Resize to fit screen
            img_current = cv2.resize(img_current, (self.wCam, self.hCam))

            # Cache the slide
            self.current_slide = img_current.copy()
            self.last_img_number = self.img_number

            return img_current

        except Exception as e:
            print(f"Error loading image: {e}")
            return self.create_blank_slide("Error loading slide")

    def create_blank_slide(self, message):
        """Create a blank slide with a message"""
        slide = np.ones((self.hCam, self.wCam, 3), dtype=np.uint8) * 240
        cv2.putText(slide, message, (self.wCam // 4, self.hCam // 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 2)
        return slide

    def process_frame(self, frame):
        """Process a frame and return the combined presentation frame"""
        if not self.is_running or frame is None:
            return None

        try:
            # Resize and flip the input frame
            img = cv2.resize(frame, (self.wCam, self.hCam))
            img = cv2.flip(img, 1)

            # Load the current presentation slide
            img_current = self.load_image()

            # Find hands in the webcam feed
            hands, img = self.detector.findHands(img)

            # Draw threshold line for gesture area
            cv2.line(img, (0, self.threshold), (self.wCam, self.threshold), (0, 255, 0), 10)

            # Add instruction text
            cv2.putText(img, "Gesture Area (above green line)", (10, self.threshold - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            # Process hand gestures
            if hands and len(hands) > 0:
                fingers = self.detector.fingersUp(hands[0])

                if not self.buttonPressed:
                    cx, cy = hands[0]['center']

                    # Check if hand is above threshold line (for slide navigation)
                    if cy <= self.threshold:
                        if fingers[0] and not any(fingers[1:]):  # Only thumb up
                            self.change_slide(-1)
                            cv2.putText(img, "Previous Slide", (50, 50),
                                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        elif fingers[4] and not any(fingers[:4]):  # Only pinky up
                            self.change_slide(1)
                            cv2.putText(img, "Next Slide", (50, 50),
                                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                    # Handle drawing and annotations (anywhere on screen)
                    if len(hands[0]['lmList']) >= 9:  # Make sure we have finger positions
                        x1, y1 = self.map_coordinates(hands[0]['lmList'][8][0], hands[0]['lmList'][8][1])

                        # Different gestures for different actions
                        if fingers[1] and fingers[2] and not fingers[3] and not fingers[
                            4]:  # Index and middle fingers up - pointer
                            self.annotationsFlag = False
                            cv2.circle(img_current, (x1, y1), 20, (0, 255, 0), 3)
                            cv2.circle(img_current, (x1, y1), 5, (0, 255, 0), -1)
                            cv2.putText(img, "Pointer Mode", (50, 100),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

                        elif fingers[1] and not fingers[2] and not fingers[3] and not fingers[
                            4]:  # Only index finger up - draw
                            self.draw_annotation(x1, y1, img_current)
                            cv2.putText(img, "Drawing Mode", (50, 100),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                        else:
                            # No specific drawing gesture - stop drawing
                            self.annotationsFlag = False

                        # Clear last annotation - peace sign (index, middle, ring fingers)
                        if fingers == [0, 1, 1, 1, 0]:
                            self.remove_last_annotation()
                            cv2.putText(img, "Cleared Last Annotation", (50, 150),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)

                        # Clear all annotations - all fingers up
                        elif fingers == [1, 1, 1, 1, 1]:
                            self.clear_all_annotations()
                            cv2.putText(img, "Cleared All Annotations", (50, 150),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)

            # Handle button cooldown
            if self.buttonPressed:
                self.buttonCounter += 1
                if self.buttonCounter > self.buttonDelay:
                    self.buttonCounter = 0
                    self.buttonPressed = False

            # Draw all saved annotations
            self.draw_annotations(img_current)

            # Add webcam preview to presentation (top-right corner)
            img_small = cv2.resize(img, (self.ws, self.hs))
            h, w = img_small.shape[:2]

            # Add border to webcam preview
            cv2.rectangle(img_current, (self.wCam - w - 5, 0), (self.wCam, h + 5), (255, 255, 255), 2)
            img_current[5:h + 5, self.wCam - w:self.wCam] = img_small

            # Display slide information
            slide_info = f"Slide: {self.img_number + 1}/{len(self.images)}"
            cv2.putText(img_current, slide_info, (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            # Display current slide name
            if self.images:
                slide_name = os.path.splitext(self.images[self.img_number])[0]
                cv2.putText(img_current, slide_name, (50, 85),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

            # Display controls help
            help_text = "Controls: Thumb=Prev | Pinky=Next | Index=Draw | 2Fingers=Point"
            cv2.putText(img_current, help_text, (50, self.hCam - 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)

            return img_current

        except Exception as e:
            print(f"Error in presentation process_frame: {e}")
            traceback.print_exc()
            return self.create_blank_slide("Processing Error")

    def change_slide(self, direction):
        """Change the current slide number"""
        if self.buttonPressed:
            return

        self.buttonPressed = True
        old_number = self.img_number

        if direction > 0:  # Next slide
            self.img_number = min(self.img_number + 1, len(self.images) - 1)
        else:  # Previous slide
            self.img_number = max(self.img_number - 1, 0)

        # Only reset annotations if the slide actually changed
        if old_number != self.img_number:
            self.annotations = [[]]
            self.annotationsNumber = -1
            self.annotationsFlag = False
            print(f"Changed to slide {self.img_number + 1}/{len(self.images)}")

    def map_coordinates(self, x1, y1):
        """Map hand coordinates to presentation coordinates"""
        # Map the coordinates from webcam space to slide space
        x1 = int(np.interp(x1, [0, self.wCam], [0, self.wCam]))
        y1 = int(np.interp(y1, [0, self.hCam], [0, self.hCam]))

        # Ensure coordinates are within bounds
        x1 = max(0, min(x1, self.wCam - 1))
        y1 = max(0, min(y1, self.hCam - 1))

        return x1, y1

    def draw_annotation(self, x1, y1, img_current):
        """Draw annotation at the specified coordinates"""
        try:
            if not self.annotationsFlag:
                self.annotationsFlag = True
                self.annotationsNumber += 1
                self.annotations.append([])

            # Draw the annotation point
            cv2.circle(img_current, (x1, y1), 8, (0, 0, 255), -1)
            self.annotations[self.annotationsNumber].append((x1, y1))

        except Exception as e:
            print(f"Error drawing annotation: {e}")

    def remove_last_annotation(self):
        """Remove the last annotation"""
        try:
            if self.annotations and len(self.annotations) > 1:
                self.annotations.pop(-1)
                self.annotationsNumber = max(0, self.annotationsNumber - 1)
                self.buttonPressed = True
                print("Removed last annotation")
        except Exception as e:
            print(f"Error removing annotation: {e}")

    def clear_all_annotations(self):
        """Clear all annotations"""
        try:
            self.annotations = [[]]
            self.annotationsNumber = -1
            self.annotationsFlag = False
            self.buttonPressed = True
            print("Cleared all annotations")
        except Exception as e:
            print(f"Error clearing annotations: {e}")

    def draw_annotations(self, img_current):
        """Draw all saved annotations on the current slide"""
        try:
            for i in range(len(self.annotations)):
                for j in range(1, len(self.annotations[i])):
                    if j > 0:
                        pt1 = tuple(map(int, self.annotations[i][j - 1]))
                        pt2 = tuple(map(int, self.annotations[i][j]))
                        cv2.line(img_current, pt1, pt2, (0, 0, 200), 8)
        except Exception as e:
            print(f"Error drawing annotations: {e}")

    def handle_key_press(self, data):
        """Handle keyboard input"""
        try:
            key = data.get('key', '').lower()

            if key in ['arrowleft', 'left']:
                self.change_slide(-1)
                print("Previous slide (keyboard)")
            elif key in ['arrowright', 'right']:
                self.change_slide(1)
                print("Next slide (keyboard)")
            elif key in ['c']:
                self.clear_all_annotations()
                print("Cleared all annotations (keyboard)")
            elif key in ['u', 'z']:  # Undo last annotation
                self.remove_last_annotation()
                print("Removed last annotation (keyboard)")
            elif key in ['home']:
                # Go to first slide
                self.img_number = 0
                self.clear_all_annotations()
                print("Went to first slide")
            elif key in ['end']:
                # Go to last slide
                self.img_number = len(self.images) - 1
                self.clear_all_annotations()
                print("Went to last slide")
            elif key.isdigit():
                # Go to specific slide number
                slide_num = int(key) - 1
                if 0 <= slide_num < len(self.images):
                    self.img_number = slide_num
                    self.clear_all_annotations()
                    print(f"Went to slide {slide_num + 1}")

        except Exception as e:
            print(f"Error handling key press: {e}")

    def stop(self):
        """Clean up resources"""
        self.is_running = False
        print("Presentation controller stopped")