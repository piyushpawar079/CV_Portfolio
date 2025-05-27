# Computer Vision Portfolio

A real-time computer vision web application featuring multiple interactive demos including virtual mouse, virtual painter, volume control, pong game, fitness tracker, and presentation controller.

## Features

- 🖱️ **Virtual Mouse**: Control your cursor with hand gestures
- 🎨 **Virtual Painter**: Draw in the air with finger tracking
- 🔊 **Volume Control**: Adjust system volume with hand gestures
- 🏓 **Pong Game**: Play pong using hand movements
- 💪 **Fitness Tracker**: Count arm curls automatically
- 📽️ **PPT Controller**: Control presentations with gestures

## Tech Stack

- **Backend**: Flask, SocketIO, OpenCV, MediaPipe
- **Frontend**: Next.js, React, TypeScript, Tailwind CSS
- **Real-time Communication**: WebSocket

## Local Development

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py