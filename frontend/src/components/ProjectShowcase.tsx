"use client";

import { useState, useRef, useEffect } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { ArrowRight, Play } from 'lucide-react';
import { Card, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { getProjectData } from '@/lib/projectData';

export default function ProjectsShowcase() {
  const projects = getProjectData();
  const [hoveredProject, setHoveredProject] = useState<string | null>(null);
  const [videoErrors, setVideoErrors] = useState<{[key: string]: boolean}>({});
  const videoRefs = useRef<{ [key: string]: HTMLVideoElement | null }>({});

  useEffect(() => {
    projects.forEach(project => {
      if (videoRefs.current && hoveredProject === project.id && videoRefs.current[project.id]) {
        const video = videoRefs.current[project.id];
        if (video && !videoErrors[project.id]) {
          if (project.startTime) {
            video.currentTime = project.startTime;
          }
          video.play().catch(err => {
            console.warn(`Video play failed for ${project.id}:`, err);
            setVideoErrors(prev => ({ ...prev, [project.id]: true }));
          });
        }
      }
    });
  }, [hoveredProject, projects, videoErrors]);

  const handleMouseEnter = (projectId: string) => {
    setHoveredProject(projectId);
  };

  const handleMouseLeave = (projectId: string) => {
    setHoveredProject(null);
    if (videoRefs.current && videoRefs.current[projectId]) {
      const video = videoRefs.current[projectId];
      if (video) {
        video.pause();
        video.currentTime = 0;
      }
    }
  };

  return (
    <section id="projects" className="py-24 bg-gradient-to-b from-slate-900 to-slate-950 relative overflow-hidden">
      {/* Subtle grid overlay */}
      <div className="absolute inset-0 bg-grid-white/[0.03] bg-[length:40px_40px]"></div>
      
      {/* Glowing accents */}
      <div className="absolute top-1/4 -left-20 w-80 h-80 bg-blue-500/10 rounded-full blur-3xl"></div>
      <div className="absolute bottom-1/4 -right-20 w-80 h-80 bg-purple-500/10 rounded-full blur-3xl"></div>
      
      <div className="container mx-auto px-4 relative z-10">
        {/* Heading */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <div className="inline-block mb-3">
            <span className="px-3 py-1 rounded-full text-xs font-medium bg-blue-500/10 text-blue-400 border border-blue-500/20">
              Projects
            </span>
          </div>
          <h2 className="text-4xl font-bold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-blue-500">
            Projects Gallery
          </h2>
          <p className="text-slate-300 max-w-2xl mx-auto">
            Explore my collection of interactive computer vision applications
          </p>
        </motion.div>

        {/* Project Cards */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-10">
          {projects.map((project, index) => (
            <motion.div
              key={project.id}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              viewport={{ once: true }}
            >
              <Card 
                className="h-full flex flex-col overflow-hidden group bg-slate-900/80 backdrop-blur border border-slate-800/70 hover:border-blue-500/30 hover:shadow-xl hover:shadow-blue-500/10 transition-all duration-300"
                onMouseEnter={() => handleMouseEnter(project.id)}
                onMouseLeave={() => handleMouseLeave(project.id)}
              >
                {/* Video Preview */}
                <div className="relative aspect-video overflow-hidden">
                  {project.demoPath && !videoErrors[project.id] ? (
                    <video
                      ref={el => videoRefs.current[project.id] = el}
                      className="absolute inset-0 w-full h-full object-cover"
                      muted
                      playsInline
                      loop
                      onLoadedMetadata={(e) => {
                        if (project.startTime) {
                          e.currentTarget.currentTime = project.startTime;
                        }
                      }}
                      onError={() => setVideoErrors(prev => ({ ...prev, [project.id]: true }))}
                    >
                      <source src={project.demoPath} type="video/mp4" />
                    </video>
                  ) : (
                    <div className={`absolute inset-0 flex items-center justify-center transition-all bg-gradient-to-br from-slate-800 to-slate-900
                      ${hoveredProject === project.id ? 'bg-black/20' : 'bg-black/40'}
                    `}>
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

                  {/* Project preview overlay */}
                  <div className={`absolute inset-0 bg-gradient-to-t from-slate-900 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300`}></div>
                </div>

                {/* Card Content */}
                <CardHeader className="flex-1">
                  <CardTitle className="text-slate-200">{project.title}</CardTitle>
                  <CardDescription className="text-slate-400">{project.shortDescription}</CardDescription>
                </CardHeader>

                {/* Card Footer */}
                <CardFooter className="flex justify-between items-center mt-auto border-t border-slate-800/50 py-4">
                  <Link
                    href={`/projects/${project.id}`}
                    className="text-cyan-400 flex items-center gap-1 text-sm font-medium cursor-pointer hover:text-cyan-300 transition-colors"
                  >
                    Learn more <ArrowRight className="h-4 w-4" />
                  </Link>
                  
                  <Button 
                    asChild 
                    size="sm" 
                    className="bg-gradient-to-r from-blue-500/20 to-purple-500/20 hover:from-blue-500/30 hover:to-purple-500/30 text-white border border-blue-500/30 rounded-lg shadow-sm shadow-blue-500/10"
                  >
                    <Link href={`/demo/${project.id}`}>
                      <Play className="h-4 w-4 mr-1" /> Launch Demo
                    </Link>
                  </Button>
                </CardFooter>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}