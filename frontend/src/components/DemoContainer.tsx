"use client";

import { useState, useEffect, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { AlertCircle, ChevronRight, Maximize2, Minimize2, Volume2, VolumeX } from 'lucide-react';
import Link from 'next/link';
import { ProjectData } from '@/lib/projectData';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import FeatureStream from './MainStreaming';

export default function DemoContainer({ project }: { project: ProjectData }) {
  const [loading, setLoading] = useState(true);
  const [connected, setConnected] = useState(false);
  const [fullscreen, setFullscreen] = useState(false);
  const [muted, setMuted] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const socketRef = useRef<WebSocket | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Simulating connection to backend
    setConnected(true);
    const timer = setTimeout(() => {
      setLoading(false);
    }, 8000);

    return () => {
      clearTimeout(timer);
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, []);

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      containerRef.current?.requestFullscreen().catch(err => {
        setError(`Error attempting to enable fullscreen: ${err.message}`);
      });
      setFullscreen(true);
    } else {
      document.exitFullscreen();
      setFullscreen(false);
    }
  };

  return (
    <div className="py-28 bg-gradient-to-b from-slate-900 to-slate-950 relative overflow-hidden min-h-screen">
      {/* Subtle grid overlay */}
      <div className="absolute inset-0 bg-grid-white/[0.03] bg-[length:40px_40px]"></div>
      
      {/* Glowing accents */}
      <div className="absolute top-1/4 -left-20 w-80 h-80 bg-blue-500/10 rounded-full blur-3xl"></div>
      <div className="absolute bottom-1/4 -right-20 w-80 h-80 bg-purple-500/10 rounded-full blur-3xl"></div>
      
      <div className="max-w-6xl mx-auto px-4 relative z-10">
        <div className="mb-8 ">
          <Link 
            href={`/projects/${project.id}`} 
            className="max-w-[18%] flex items-center gap-1 text-sm text-slate-400 mb-4 hover:text-cyan-400 transition-colors duration-300"
          >
            <p className="flex gap-1 border border-slate-700 px-3 py-1.5 rounded-md backdrop-blur bg-slate-800/30 hover:border-cyan-500/30 hover:bg-slate-800/50 transition-all duration-300">
              <ChevronRight className="h-4 w-4 rotate-180 mt-0.5" />
              <span>Back to project details</span>
            </p>
          </Link>
          
          <h1 className="text-3xl md:text-4xl font-bold mb-2 bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-blue-500">{project.title} Demo</h1>
          <p className="text-slate-300">
            Interact with the application using hand gestures tracked by your webcam
          </p>
        </div>
        
        <div className="grid lg:grid-cols-4 gap-8">
          <div className="lg:col-span-3" ref={containerRef}>
            <Card className="overflow-hidden bg-slate-900/80 backdrop-blur border border-slate-800/70 hover:border-blue-500/30 hover:shadow-xl hover:shadow-blue-500/10 transition-all duration-300">
              <CardHeader className="p-4 border-b border-slate-800/50">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg text-slate-200">Live Demo</CardTitle>
                  <div className="flex items-center gap-2">
                    <Button 
                      variant="ghost" 
                      size="icon" 
                      onClick={() => setMuted(!muted)}
                      aria-label={muted ? "Unmute" : "Mute"}
                      className="text-slate-300 hover:text-cyan-400 hover:bg-slate-800/50"
                    >
                      {muted ? <VolumeX className="h-5 w-5" /> : <Volume2 className="h-5 w-5" />}
                    </Button>
                    <Button 
                      variant="ghost" 
                      size="icon" 
                      onClick={toggleFullscreen}
                      aria-label={fullscreen ? "Exit fullscreen" : "Enter fullscreen"}
                      className="text-slate-300 hover:text-cyan-400 hover:bg-slate-800/50"
                    >
                      {fullscreen ? <Minimize2 className="h-5 w-5" /> : <Maximize2 className="h-5 w-5" />}
                    </Button>
                  </div>
                </div>
              </CardHeader>
              
              <CardContent className="p-0 aspect-video bg-black relative">
                {loading ? (
                  <div className="absolute inset-0 flex flex-col items-center justify-center bg-slate-900">
                    <div className="w-16 h-16 border-4 border-t-4 border-blue-500 border-solid rounded-full animate-spin mb-4"></div>
                    <p className="text-slate-300">Loading camera feed...</p>
                  </div>
                ) : (
                  <FeatureStream featureName={project.id} />
                )}
              </CardContent>
              
              <CardFooter className="p-4 border-t border-slate-800/50">
                <p className="text-sm text-slate-400">
                  For the best experience, ensure good lighting and position yourself 1-2 feet from the camera.
                </p>
              </CardFooter>
            </Card>
          </div>
          
          <div className="space-y-6">
            <Card className="hover:scale-105 transition-all duration-300 bg-slate-900/80 backdrop-blur border border-slate-800/70 hover:border-blue-500/30 hover:shadow-xl hover:shadow-blue-500/10">
              <CardHeader>
                <CardTitle className="text-slate-200">Instructions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <Dialog>
                  <DialogTrigger asChild>
                    <Button 
                      className="w-full bg-gradient-to-r from-blue-500/20 to-purple-500/20 hover:from-blue-500/30 hover:to-purple-500/30 text-white border border-blue-500/30 rounded-lg shadow-sm shadow-blue-500/10"
                    >
                      View Detailed Instructions
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="max-w-lg bg-slate-900 border border-slate-800">
                    <DialogHeader>
                      <DialogTitle className="text-slate-200">How to Use the Demo</DialogTitle>
                      <DialogDescription className="text-slate-400">
                        Follow these instructions to interact with the {project.title} demo.
                      </DialogDescription>
                    </DialogHeader>
                    <div className="space-y-4 mt-4">
                      <div>
                        <h4 className="font-bold mb-2 text-slate-200">Navigation</h4>
                        <ul className="space-y-2 text-sm text-slate-300">
                          <li>• Use your index finger to move the cursor</li>
                          <li>• Raise both index and middle fingers to click/select</li>
                          <li>• Lower all fingers to reset</li>
                        </ul>
                      </div>
                      
                      <div>
                        <h4 className="font-bold mb-2 text-slate-200">Controls</h4>
                        <ul className="space-y-2 text-sm text-slate-300">
                          <li>• Select tools from the top menu</li>
                          <li>• Draw by moving your finger with the tool selected</li>
                          <li>• Use the slider to adjust brush size</li>
                          <li>• Click the Undo button to remove the last action</li>
                        </ul>
                      </div>
                      
                      <div>
                        <h4 className="font-bold mb-2 text-slate-200">Tips</h4>
                        <ul className="space-y-2 text-sm text-slate-300">
                          <li>• Ensure good lighting for better tracking</li>
                          <li>• Position yourself 1-2 feet from the camera</li>
                          <li>• Make deliberate gestures for better recognition</li>
                          <li>• Keep your hand within the camera frame</li>
                        </ul>
                      </div>
                    </div>
                  </DialogContent>
                </Dialog>
                
                <div className="space-y-3">
                  <h3 className="font-bold text-slate-200">Quick Guide:</h3>
                  <div className="space-y-2 text-sm">
                    {project.QuickGuide && Object.entries(project.QuickGuide).map(([key, value]) => (
                      <p key={key} className="flex items-start gap-2 text-slate-300">
                        <span className="bg-blue-500/20 border border-blue-500/30 p-1 rounded text-xs text-cyan-400">{key}</span>
                        <span>{value}</span>
                      </p>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
            
            {/* Added feature highlights card */}
            <Card className="hover:scale-105 transition-all duration-300 bg-slate-900/80 backdrop-blur border border-slate-800/70 hover:border-blue-500/30 hover:shadow-xl hover:shadow-blue-500/10">
              <CardHeader>
                <CardTitle className="text-slate-200">Feature Highlights</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  {['Real-time tracking', 'Gesture recognition', 'Interactive UI', 'No additional hardware needed'].map((feature, i) => (
                    <div key={i} className="flex items-center gap-2">
                      <div className="w-2 h-2 rounded-full bg-cyan-400"></div>
                      <p className="text-slate-300 text-sm">{feature}</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
        
        {/* Error display */}
        {error && (
          <Alert className="mt-6 bg-red-900/20 border-red-800 text-red-300">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}
      </div>
    </div>
  );
}