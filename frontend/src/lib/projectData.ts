export interface ProjectData {
    id: string;
    title: string;
    description: string;
    shortDescription: string;
    // tech: string[];
    features: string[];
    useCases?: string[];
    implementation?: string;
    howItWorks?: string;
    thumbnail: string;
    demoPath: string;
    startTime: number;
    QuickGuide: object;
  }
  
  export function getProjectData(): ProjectData[] {
    return [
      {
      id: 'virtual-painter',
      title: 'Virtual Painter',
      description: 'An interactive drawing application that allows users to create digital art using hand gestures. The Virtual Painter tracks hand movements through a webcam and translates them into brush strokes on a digital canvas.',
      shortDescription: 'Draw on your webcam feed using hand gestures',
      // tech: ['OpenCV', 'MediaPipe', 'Python', 'Flask', 'Socket.IO'],
      features: [
        'Draw with finger movements',
        'Multiple brush colors and sizes',
        'Circle and line shape tools',
        'Eraser functionality',
        'Fill options for circle',
        'Undo capability',
        'Real-time processing'
      ],
      thumbnail: '/api/placeholder/600/400',
      demoPath: "/videos/Virtual_Paint.mp4",
      startTime: 8,
      QuickGuide: {
        "✓": "Index finger = Navigate",
        "✓✓": "Index + Middle = Select",
        "Q": "Press Q to quit"
      }
      },
      {
      id: 'pong-game',
      title: 'CV Pong Game',
      description: 'A reimagined version of the classic Pong game controlled by hand gestures. Players can move paddles using their index finger to bounce the ball back and forth.',
      shortDescription: 'Play the classic Pong game using hand gestures',
      // tech: ['OpenCV', 'MediaPipe', 'Python', 'PyGame', 'Flask'],
      features: [
        'Two-player mode',
        'Hand gesture controls',
        'Real-time performance',
        'Score tracking'
      ],
      thumbnail: '/api/placeholder/600/400',
      demoPath: "/videos/Pong_Game.mp4",
      startTime: 8,
      QuickGuide: {
        "✓": "Index finger = Paddle Control",
        "R": "Press R to restart",
        "Q": "Press Q to quit"
      }
      },
      {
      id: 'ppt-presenter',
      title: 'Gesture Presentation',
      description: 'A tool that enables users to control PowerPoint presentations using hand gestures. Navigate between slides, draw annotations, and highlight key points without touching any device.',
      shortDescription: 'Control presentations with hand gestures',
      // tech: ['OpenCV', 'MediaPipe', 'Python', 'Flask', 'Socket.IO'],
      features: [
        'Navigate slides with gestures',
        'Draw annotations on slides',
        'Highlight key points',
        'Smooth transition effects',
      ],
      thumbnail: '/api/placeholder/600/400',
      demoPath: "/videos/PPT_Presentation.mp4",
      startTime: 7,
      QuickGuide: {
        "1": "Little finger = Next Slide",
        "2": "Only Thumb = Previous Slide",
        "3": "Index finger = Draw",
        "4": "Index + Middle = Highlight",
        "5": "Index + Middle + Ring = Erase",
        "Q": "Press Q to quit"
      }
      },
      {
      id: 'virtual-mouse',
      title: 'Virtual Mouse',
      description: 'A computer vision-based tool that allows users to control their computer mouse using hand gestures. Perform clicks, and scrolls without touching any physical device.',
      shortDescription: 'Control your computer mouse with hand gestures',
      // tech: ['OpenCV', 'MediaPipe', 'Python', 'Flask'],
      features: [
        'Hand gesture-based mouse control',
        // 'Left and right click functionality',
        // 'Drag and drop support',
        'Scroll using gestures',
        'Real-time performance'
      ],
      thumbnail: '/api/placeholder/600/400',
      demoPath: "/videos/Virtual_Mouse.mp4",
      startTime: 7,
      QuickGuide: {
        "✓": "Index finger = Navigate",
        "✓✓": "Index + Middle = Click",
        "Q": "Press Q to quit"
      }
      },
      {
      id: 'volume-control',
      title: 'Volume Control',
      description: 'Control your computer\'s volume using hand gestures. Pinch gestures adjust the volume level, providing a touchless way to manage audio during presentations or while working.',
      shortDescription: 'Adjust system volume with hand gestures',
      // tech: ['OpenCV', 'MediaPipe', 'Python', 'System APIs'],
      features: [
        'Touchless volume control',
        'Visual feedback',
        'System integration',
      ],
      thumbnail: '/api/placeholder/600/400',
      demoPath: "/videos/Volume_Control.mp4",
      startTime: 11,
      QuickGuide: {
        "✓": "Index + Middle + Ring finger = Mode Selection",
        "✓✓": "Index + Middle = Volume Up/Down",
        "✓✓✓": "Index + Thumb + Little Finger = Volume Up/Down",
        "Q": "Press Q to quit"
      }
      },
      {
      id: 'fitness-tracker',
      title: 'Fitness Tracker',
      description: 'A computer vision-based fitness tracker that monitors your workout routines and provides real-time feedback. It can count repetitions',
      shortDescription: 'Track your fitness activities with real-time feedback',
      // tech: ['OpenCV', 'MediaPipe', 'Python', 'Flask', 'TensorFlow'],
      features: [
        'Real-time exercise tracking',
        'Repetition counting',
      ],
      thumbnail: '/api/placeholder/600/400',
      demoPath: "/videos/Fitness_Tracker.mp4",
      startTime: 10,
      QuickGuide: {
        "✓": "Thumb + Little Finger = Hand Change",
        "Q": "Press Q to quit"
      }
      }
    ];
  }