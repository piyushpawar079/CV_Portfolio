'use client';

import React, { useState, useEffect, useRef } from 'react';
import io, { Socket } from 'socket.io-client';
import { Alert, AlertDescription, AlertTitle } from './ui/alert';
import { AlertCircle, Play, RefreshCw, Camera } from 'lucide-react';
import { Button } from './ui/button';
import config from '@/lib/config';

interface FrameData {
  image: string;
}

function FeatureStream({ featureName }: { featureName: string }) {
  const [frameData, setFrameData] = useState<string | null>(null);
  const socketRef = useRef<Socket | null>(null);
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [loading, setLoading] = useState(true);
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showInstructions, setShowInstructions] = useState(true);
  const [connectionAttempt, setConnectionAttempt] = useState(0);
  const frameIntervalRef = useRef<number | null>(null);

  const toggleConnect = () => {
    if (connected) {
      // If connected, disconnect
      socketRef.current?.emit('stop_feature');
      socketRef.current?.disconnect();
      setConnected(false);
      if (frameIntervalRef.current) {
        window.clearInterval(frameIntervalRef.current);
        frameIntervalRef.current = null;
      }
    } else {
      // If disconnected, reconnect
      reconnect();
    }
  };

  const reconnect = () => {
    // Clean up existing socket if any
    if (socketRef.current) {
      try {
        socketRef.current.emit('stop_feature');
        socketRef.current.disconnect();
      } catch (e) {
        console.error("Error cleaning up socket:", e);
      }
    }
    
    setLoading(true);
    setError(null);
    setConnected(false);
    
    // Trigger a re-render and new socket connection by updating the connectionAttempt state
    setConnectionAttempt(prev => prev + 1);
  };

  // Function to capture frame from user's camera and send to backend
  const captureAndSendFrame = () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    
    if (!video || !canvas || !socketRef.current?.connected) return;
    
    const context = canvas.getContext('2d');
    if (!context) return;
    
    // Set canvas dimensions to match video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    // Draw the current video frame to the canvas
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    // Convert canvas to base64 image
    try {
      // Get image data as JPEG base64 string
      const imageData = canvas.toDataURL('image/jpeg', 0.8).split(',')[1];
      
      // Send to server for processing
      socketRef.current.emit('process_frame', { image: imageData });
    } catch (err) {
      console.error("Error capturing frame:", err);
    }
  };

  useEffect(() => {
    // Setup video stream first
    const setupCamera = async () => {
      try {
        const video = videoRef.current;
        if (!video) return;
        
        const stream = await navigator.mediaDevices.getUserMedia({ 
          video: { 
            width: { ideal: 1280 },
            height: { ideal: 720 },
            facingMode: 'user' 
          } 
        });
        
        video.srcObject = stream;
        await video.play();
        
        console.log("Camera initialized successfully");
        return true;
      } catch (err) {
        console.error("Error accessing camera:", err);
        setError(`Camera access error: ${err instanceof Error ? err.message : String(err)}`);
        setLoading(false);
        return false;
      }
    };
    
    // Set up socket connection after camera is initialized
    const setupSocket = () => {
      console.log(`Setting up connection attempt ${connectionAttempt}`);
      
      let connectionTimeout = setTimeout(() => {
        if (!connected && !error) {
          setError("Connection timed out. Is the server running?");
          setLoading(false);
        }
      }, 15000);
      
      try {
        // Replace with your actual server URL in production
        const socket = io(config.backendUrl, {
          reconnection: true,
          reconnectionAttempts: 5,
          reconnectionDelay: 1000,
          timeout: 10000,
        });

        socketRef.current = socket;

        socket.on('connect', () => {
          console.log(`Connected to server. Starting feature: ${featureName}`);
          socket.emit('start_feature', { feature: featureName });
          // Don't set connected=true yet, wait for ready_for_frames signal
        });

        socket.on('disconnect', () => {
          console.log('Disconnected from server.');
          setConnected(false);
          setError("Connection lost. The server has disconnected.");
          setLoading(false);
          if (frameIntervalRef.current) {
            window.clearInterval(frameIntervalRef.current);
            frameIntervalRef.current = null;
          }
        });

        socket.on('processed_frame', (data: FrameData) => {
          setFrameData(data.image);
          setLoading(false);
          setConnected(true);
          setError(null);
          clearTimeout(connectionTimeout);
        });

        socket.on('error', (data: {message: string}) => {
          console.error('Server error:', data.message);
          setError(`Server error: ${data.message}`);
        });

        socket.on('connect_error', (error: Error) => {
          console.error('Connection error:', error);
          setError(`Connection error: ${error.message}`);
          setLoading(false);
        });

        // Start sending frames once connected
        socket.on('ready_for_frames', () => {
          console.log("Server ready for frames, starting capture");
          // Only start the interval if it doesn't already exist
          if (!frameIntervalRef.current) {
            frameIntervalRef.current = window.setInterval(captureAndSendFrame, 33); // ~30fps
          }
          setConnected(true);
          setLoading(false);
        });

        return () => {
          clearTimeout(connectionTimeout);
          if (frameIntervalRef.current) {
            window.clearInterval(frameIntervalRef.current);
            frameIntervalRef.current = null;
          }
          if (socketRef.current) {
            try {
              socketRef.current.emit('stop_feature');
              socketRef.current.disconnect();
            } catch (e) {
              console.error("Error during cleanup:", e);
            }
          }
        };
      } catch (err) {
        console.error("Error creating socket connection:", err);
        setError(`Failed to initialize socket: ${err instanceof Error ? err.message : String(err)}`);
        setLoading(false);
        return () => clearTimeout(connectionTimeout);
      }
    };

    // First setup camera, then socket
    setupCamera().then(success => {
      if (success) {
        return setupSocket();
      }
    });
    
    // Cleanup function
    return () => {
      if (frameIntervalRef.current) {
        window.clearInterval(frameIntervalRef.current);
        frameIntervalRef.current = null;
      }
      // Stop any active camera streams
      if (videoRef.current && videoRef.current.srcObject) {
        const stream = videoRef.current.srcObject as MediaStream;
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, [featureName, connectionAttempt]);

  const handleKeyDown = (event: React.KeyboardEvent) => {
    console.log('Key pressed:', event.key);
    if (socketRef.current?.connected) {
      socketRef.current.emit('key_press', { key: event.key });
    }
  };

  return (
    <div 
      className="feature-stream-container w-full h-full" 
      tabIndex={0} 
      onKeyDown={handleKeyDown}
    >
      {/* Hidden video element for camera capture */}
      <video 
        ref={videoRef} 
        style={{ display: 'none' }} 
        playsInline 
        muted
      />
      
      {/* Hidden canvas for processing frames */}
      <canvas 
        ref={canvasRef} 
        style={{ display: 'none' }} 
      />
      
      <div className="canvas-container w-full h-full">
        {loading ? (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="flex flex-col items-center gap-4">
              <div className="h-12 w-12 rounded-full border-4 border-primary border-t-transparent animate-spin" />
              <p className="text-muted-foreground">Connecting to server...</p>
            </div>
          </div>
        ) : error ? (
          <div className="absolute inset-0 flex items-center justify-center p-6">
            <Alert variant="destructive" className="max-w-md">
              <AlertCircle className="h-4 w-4" />
              <AlertTitle>Connection Error</AlertTitle>
              <AlertDescription>
                {error}
                <Button variant="outline" className="mt-4 w-full" onClick={reconnect}>
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Try Again
                </Button>
              </AlertDescription>
            </Alert>
          </div>
        ) : connected ? (
          <div className="absolute inset-0 flex items-center justify-center">
            {frameData ? (
              <img
                src={`data:image/jpeg;base64,${frameData}`}
                alt={`${featureName} Stream`}
                className="video-stream w-full h-full object-contain"
              />
            ) : (
              <div className="flex flex-col items-center gap-4">
                <Camera className="h-12 w-12 text-muted-foreground" />
                <p className="text-muted-foreground">Waiting for processed frame...</p>
              </div>
            )}
            
            {showInstructions && (
              <div className="absolute inset-0 bg-black/70 flex items-center justify-center">
                <div className="max-w-md text-center p-6">
                  <h3 className="text-xl font-bold mb-4">Ready to Start</h3>
                  <p className="mb-6">
                    Position yourself in view of the camera. Use your index finger to navigate and 
                    both index and middle finger to select.
                  </p>
                  <Button onClick={() => setShowInstructions(false)} className="cursor-pointer">
                    <Play className="h-4 w-4 mr-2" />
                    Start Demo
                  </Button>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="absolute inset-0 flex items-center justify-center p-6">
            <Alert variant="default" className="max-w-md">
              <AlertCircle className="h-4 w-4" />
              <AlertTitle>Disconnected</AlertTitle>
              <AlertDescription>
                The demo is not connected.
                <Button variant="outline" className="mt-4 w-full" onClick={reconnect}>
                  <Play className="h-4 w-4 mr-2" />
                  Connect
                </Button>
              </AlertDescription>
            </Alert>
          </div>
        )}
      </div>
    </div>
  );
}

export default FeatureStream;