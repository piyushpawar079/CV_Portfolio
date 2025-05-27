"use client";

import { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Check, ChevronRight, Play } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import Link from 'next/link';
import { ProjectData } from '@/lib/projectData';

export default function ProjectDetails({ project }: { project: ProjectData }) {
  const [videoErrors, setVideoErrors] = useState<{[key: string]: boolean}>({});
  const [videoLoaded, setVideoLoaded] = useState(false);
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const [isHovered, setIsHovered] = useState(false);
  
  // Handle video playback based on hover state
  useEffect(() => {
    if (videoRef.current && project.demoPath && !videoErrors[project.id]) {
      const video = videoRef.current;
      setVideoLoaded(true);
      if (isHovered) {
        // Play video when hovered
        if (video.readyState >= 2) { // HAVE_CURRENT_DATA or higher
          // Set start time if specified
          if (project.startTime) {
            video.currentTime = project.startTime;
          }
          
          video.play().catch(err => {
            console.warn(`Video play failed for ${project.id}:`, err);
            setVideoErrors(prev => ({...prev, [project.id]: true}));
          });
        } else {
          // If not loaded yet, add event listener to play when ready
          const handleCanPlay = () => {
            if (isHovered && video) {
              if (project.startTime) {
                video.currentTime = project.startTime;
              }
              video.play().catch(console.error);
            }
          };
          
          video.addEventListener('canplay', handleCanPlay, { once: true });
          return () => {
            video.removeEventListener('canplay', handleCanPlay);
          };
        }
      } else {
        // Pause video when not hovered
        video.pause();
      }
    }
  }, [isHovered, project.id, project.demoPath, project.startTime, videoErrors]);

  // Handle video loading
  useEffect(() => {
    if (videoRef.current && project.demoPath && !videoErrors[project.id]) {
      const video = videoRef.current;
      
      const handleLoadedData = () => {
        setVideoLoaded(true);
      };
      
      video.addEventListener('loadeddata', handleLoadedData);
      
      return () => {
        video.removeEventListener('loadeddata', handleLoadedData);
      };
    }
  }, [project.id, project.demoPath, videoErrors]);
  
  const handleMouseEnter = () => {
    setIsHovered(true);
  };

  const handleMouseLeave = () => {
    setIsHovered(false);
  };

  return (
    <div className="pt-28 pb-10 bg-gradient-to-b from-slate-900 to-slate-950 relative overflow-hidden min-h-screen">
      {/* Subtle grid overlay */}
      <div className="absolute inset-0 bg-grid-white/[0.03] bg-[length:40px_40px]"></div>
      
      {/* Glowing accents */}
      <div className="absolute top-1/4 -left-20 w-80 h-80 bg-blue-500/10 rounded-full blur-3xl"></div>
      <div className="absolute bottom-1/4 -right-20 w-80 h-80 bg-purple-500/10 rounded-full blur-3xl"></div>
      
      <div className="max-w-5xl mx-auto px-4 relative z-10">
        <div className="mb-8">
          <Link 
            href="/projects" 
            className="max-w-[16%] flex items-center gap-1 text-sm text-slate-400 mb-4 hover:text-cyan-400 transition-colors duration-300"
          >
            <p className="flex gap-1 border border-slate-700 px-3 py-1.5 rounded-md backdrop-blur bg-slate-800/30 hover:border-cyan-500/30 hover:bg-slate-800/50 transition-all duration-300">
              <ChevronRight className="h-4 w-4 rotate-180 mt-0.5" />
              Back to projects
            </p>
          </Link>
          
          <h1 className="text-3xl md:text-4xl font-bold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-blue-500">{project.title}</h1>
        </div>
        
        <div className="grid md:grid-cols-3 gap-8">
          <div className="md:col-span-2">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <div 
                className="aspect-video overflow-hidden relative rounded-lg mb-8 transition-all duration-300 transform hover:scale-105 bg-slate-800/40 border border-slate-700/50 hover:border-blue-500/30 hover:shadow-xl hover:shadow-blue-500/10"
                onMouseEnter={handleMouseEnter}
                onMouseLeave={handleMouseLeave}
              >
                {/* Video element with hover-controlled playback */}
                {project.demoPath && !videoErrors[project.id] ? (
                  <video
                    ref={videoRef}
                    className="absolute inset-0 w-full h-full object-cover rounded-lg"
                    muted
                    playsInline
                    loop
                    onLoadedMetadata={(e) => {
                      if (project.startTime) {
                        e.currentTarget.currentTime = project.startTime;
                      }
                      setVideoLoaded(true);
                    }}
                    onError={() => setVideoErrors(prev => ({...prev, [project.id]: true}))}
                  >
                    {/* Support multiple video formats */}
                    {project.demoPath.endsWith('.mp4') && (
                      <source src={project.demoPath} type="video/mp4" />
                    )}
                    {project.demoPath.endsWith('.webm') && (
                      <source src={project.demoPath} type="video/webm" />
                    )}
                    {!project.demoPath.endsWith('.mp4') && !project.demoPath.endsWith('.webm') && (
                      <source src={project.demoPath} />
                    )}
                    Your browser does not support the video tag.
                  </video>
                ) : (
                  // Fallback if video can't be loaded
                  <div className="absolute inset-0 flex items-center justify-center rounded-lg bg-gradient-to-br from-slate-800 to-slate-900">
                    <div className="text-center p-4">
                      <div className="w-16 h-16 mx-auto rounded-full bg-slate-800/80 border border-slate-700 flex items-center justify-center mb-3">
                        <Play className="h-6 w-6 text-blue-400" />
                      </div>
                      <p className="text-lg font-semibold bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-blue-500">
                        {project.title}
                      </p>
                    </div>
                  </div>
                )}

                {/* Show loading state until video is fully loaded */}
                {project.demoPath && !videoErrors[project.id] && !videoLoaded && (
                  <div className="absolute inset-0 bg-black/50 flex items-center justify-center rounded-lg">
                    <div className="w-8 h-8 border-4 border-t-4 border-blue-500 border-solid rounded-full animate-spin"></div>
                  </div>
                )}
              </div>

              <Tabs defaultValue="overview" className="backdrop-blur bg-slate-900/30 border border-slate-800/50 rounded-lg p-6">
                <TabsList className="gap-10 mb-8 bg-slate-800/50 p-1">
                  <TabsTrigger
                    value="overview"
                    className="data-[state=active]:bg-blue-500/20 data-[state=active]:text-cyan-400 data-[state=active]:font-bold data-[state=active]:border-b-2 data-[state=active]:border-cyan-400 transition-all transform hover:scale-105"
                  >
                    Overview
                  </TabsTrigger>
                  <TabsTrigger
                    value="features"
                    className="data-[state=active]:bg-blue-500/20 data-[state=active]:text-cyan-400 data-[state=active]:font-bold data-[state=active]:border-b-2 data-[state=active]:border-cyan-400 transition-all transform hover:scale-105"
                  >
                    Features
                  </TabsTrigger>
                </TabsList>
                
                <TabsContent value="overview" className="space-y-6">
                  <div>
                    <h3 className="text-xl font-bold mb-4 text-slate-200">Project Description</h3>
                    <p className="text-slate-300">{project.description}</p>
                  </div>
                  
                  <div>
                    <h3 className="text-xl font-bold mb-4 text-slate-200">How It Works</h3>
                    <p className="text-slate-300">
                      {project.howItWorks || `This project utilizes computer vision techniques to track hand movements through a webcam. 
                      The application processes video frames in real-time, identifies hand landmarks, and translates
                      gesture patterns into user interface actions.`}
                    </p>
                  </div>
                </TabsContent>
                
                <TabsContent value="features" className="space-y-6">
                  <div>
                    <h3 className="text-xl font-bold mb-4 text-slate-200">Key Features</h3>
                    <ul className="space-y-3">
                      {project.features.map((feature, index) => (
                        <li key={index} className="flex items-start gap-2 text-slate-300">
                          <Check className="h-5 w-5 text-cyan-400 mt-0.5 flex-shrink-0" />
                          <span>{feature}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                  
                  {/* <div>
                    <h3 className="text-xl font-bold mb-4 text-slate-200">Use Cases</h3>
                    <ul className="space-y-3">
                      {(project.useCases || [
                        "Educational environments for interactive learning",
                        "Accessibility applications for users with limited mobility",
                        "Interactive presentations and demos",
                        "Gaming and entertainment applications",
                        "Touchless interfaces for public kiosks"
                      ]).map((useCase, index) => (
                        <li key={index} className="flex items-start gap-2 text-slate-300">
                          <Check className="h-5 w-5 text-cyan-400 mt-0.5 flex-shrink-0" />
                          <span>{useCase}</span>
                        </li>
                      ))}
                    </ul>
                  </div> */}
                </TabsContent>
              </Tabs>
            </motion.div>
          </div>
          
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="space-y-6"
          >
            <Card className="transition-all duration-300 transform hover:scale-105 shadow-lg rounded-lg bg-slate-900/30 backdrop-blur border border-slate-800/50 hover:border-blue-500/30 hover:shadow-xl hover:shadow-blue-500/10">
              <CardContent className="p-6 space-y-6">
                <div>
                  <h3 className="text-lg font-bold mb-2 text-slate-200">Try It Out</h3>
                  <p className="text-sm text-slate-400 mb-4">
                    Launch the interactive demo and experience this project firsthand.
                  </p>
                  <Button 
                    asChild 
                    className="w-full bg-gradient-to-r from-blue-500/20 to-purple-500/20 hover:from-blue-500/30 hover:to-purple-500/30 text-white border border-blue-500/30 rounded-lg shadow-sm shadow-blue-500/10 transition-all transform hover:scale-105"
                  >
                    <Link href={`/demo/${project.id}`}>
                      <Play className="h-4 w-4 mr-2" /> Launch Demo
                    </Link>
                  </Button>
                </div>
                
                <div>
                  <h3 className="text-lg font-bold mb-2 text-slate-200">Project Requirements</h3>
                  <ul className="text-sm space-y-2">
                    <li className="flex items-start gap-2 text-slate-300">
                      <Check className="h-4 w-4 text-cyan-400 mt-0.5 flex-shrink-0" />
                      <span>Webcam access</span>
                    </li>
                    <li className="flex items-start gap-2 text-slate-300">
                      <Check className="h-4 w-4 text-cyan-400 mt-0.5 flex-shrink-0" />
                      <span>Well-lit environment</span>
                    </li>
                    <li className="flex items-start gap-2 text-slate-300">
                      <Check className="h-4 w-4 text-cyan-400 mt-0.5 flex-shrink-0" />
                      <span>Modern browser (Chrome recommended)</span>
                    </li>
                  </ul>
                </div>
              </CardContent>
            </Card>
            
            {/* Additional card for technologies */}
            <Card className="transition-all duration-300 transform hover:scale-105 shadow-lg rounded-lg bg-slate-900/30 backdrop-blur border border-slate-800/50 hover:border-blue-500/30 hover:shadow-xl hover:shadow-blue-500/10">
              <CardContent className="p-6">
                <h3 className="text-lg font-bold mb-2 text-slate-200">Technologies Used</h3>
                <div className="flex flex-wrap gap-2 mt-3">
                  {['React', 'Nextjs', 'Python', 'MediaPipe', 'OpenCV', 'WebRTC', 'CVZone' ].map((tech, i) => (
                    <span 
                      key={i} 
                      className="px-3 py-1 text-xs rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20"
                    >
                      {tech}
                    </span>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </div>
    </div>
  );
}