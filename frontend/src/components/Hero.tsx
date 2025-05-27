"use client";

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { motion } from 'framer-motion';
import Link from 'next/link';

export default function Hero() {
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  if (!isMounted) return null;

  return (
    <section className="py-24 md:py-40 relative overflow-hidden bg-gradient-to-br from-slate-950 to-indigo-950">
      {/* Animated background elements */}
      <div className="absolute inset-0 -z-10">
        <motion.div
          animate={{ 
            x: [0, 30, 0], 
            y: [0, -20, 0],
            opacity: [0.5, 0.7, 0.5] 
          }}
          transition={{ repeat: Infinity, duration: 8, ease: "easeInOut" }}
          className="absolute top-20 left-10 w-72 h-72 bg-cyan-500/20 rounded-full blur-3xl"
        />
        <motion.div
          animate={{ 
            x: [0, -30, 0], 
            y: [0, 20, 0],
            opacity: [0.5, 0.7, 0.5] 
          }}
          transition={{ repeat: Infinity, duration: 10, ease: "easeInOut" }}
          className="absolute bottom-20 right-10 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl"
        />
        <motion.div
          animate={{ 
            x: [0, 20, 0], 
            y: [0, 30, 0],
            opacity: [0.3, 0.5, 0.3] 
          }}
          transition={{ repeat: Infinity, duration: 12, ease: "easeInOut" }}
          className="absolute bottom-40 left-40 w-80 h-80 bg-blue-500/20 rounded-full blur-3xl"
        />
      </div>

      {/* Grid Pattern Overlay */}
      <div className="absolute inset-0 bg-grid-white/[0.05] bg-[length:50px_50px] opacity-20"></div>

      <div className="container mx-auto px-4 relative z-10">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <h1 className="text-5xl md:text-7xl font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-600">
              Computer Vision Projects
            </h1>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <p className="text-xl md:text-2xl mb-10 text-slate-300">
              Interact with the digital world using just your 
              <span className="relative inline-block mx-2">
                <span className="relative z-10 text-white font-semibold">hands</span>
                <span className="absolute -bottom-1 left-0 right-0 h-3 bg-purple-500/30 blur-sm"></span>
              </span>
              Experience the power of computer vision technology.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="flex flex-col sm:flex-row gap-5 justify-center"
          >
            <Button size="lg" asChild className="bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white font-medium px-8 py-6 rounded-xl shadow-lg shadow-blue-500/20 border-0">
              <Link href="/projects">Explore Projects</Link>
            </Button>
            <Button size="lg" variant="outline" asChild className="border-2 border-purple-500/50 text-purple-300 hover:bg-purple-500/10 backdrop-blur-sm font-medium px-8 py-6 rounded-xl">
              <Link href="/contact">Get in Touch</Link>
            </Button>
          </motion.div>
        </div>
      </div>

      {/* Tech Pattern Bottom */}
      <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-slate-950/80 to-transparent"></div>
    </section>
  );
}