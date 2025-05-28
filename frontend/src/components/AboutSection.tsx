"use client";

import { motion } from 'framer-motion';
import { CheckCircle, Cpu, Zap, Monitor } from 'lucide-react';

export default function AboutSection() {
  const featureItems = [
    {
      text: "Intuitive hand gesture controls",
      icon: CheckCircle,
      color: "text-cyan-500"
    },
    {
      text: "Interactive apps without physical devices",
      icon: Monitor,
      color: "text-blue-500"
    },
    {
      text: "Real-time processing and fast response",
      icon: Zap,
      color: "text-purple-500"
    },
    {
      text: "Educational and practical use cases",
      icon: Cpu,
      color: "text-indigo-500"
    },
  ];

  return (
    <section id="about" className="py-24 px-10  bg-gradient-to-b from-slate-950 to-slate-900 relative overflow-hidden">
      {/* Subtle grid overlay */}
      <div className="absolute inset-0 bg-grid-white/[0.03] bg-[length:40px_40px]"></div>
      
      {/* Glowing edge at the top */}
      <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-blue-500/50 to-transparent"></div>
      
      <div className="container mx-auto px-4 relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <div className="inline-block mb-3">
            <span className="px-3 py-1 rounded-full text-xs font-medium bg-blue-500/10 text-blue-400 border border-blue-500/20">
              About
            </span>
          </div>
          <h2 className="text-4xl font-bold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-500">
            About My Projects
          </h2>
          <p className="text-slate-300 max-w-2xl mx-auto">
            Exploring the intersection of computer vision and intuitive human-computer interaction.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-2 gap-16 items-center">
          <motion.div
            initial={{ opacity: 0, x: -40 }}
            whileInView={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.7 }}
            viewport={{ once: true }}
            className="relative"
          >
            {/* Glowing accent lights */}
            <div className="absolute -top-10 -left-10 w-40 h-40 bg-blue-500/20 rounded-full blur-3xl"></div>
            <div className="absolute -bottom-10 -right-10 w-40 h-40 bg-purple-500/20 rounded-full blur-3xl"></div>
            
            <div className="relative bg-gradient-to-br from-blue-500/10 to-purple-500/10 p-1 rounded-2xl border border-white/10 shadow-xl">
              <div className="aspect-video rounded-xl overflow-hidden bg-slate-900/80 backdrop-blur">
                <div className="w-full h-full bg-[radial-gradient(ellipse_at_center,rgba(54,109,255,0.1),transparent)] flex items-center justify-center">
                  <div className="text-center">
                    <motion.div 
                      initial={{ opacity: 0, scale: 0.9 }}
                      whileInView={{ opacity: 1, scale: 1 }}
                      transition={{ duration: 0.5, delay: 0.3 }}
                      viewport={{ once: true }}
                      className="mb-3"
                    >
                      <div className="w-16 h-16 mx-auto rounded-full bg-slate-800 border border-blue-500/20 flex items-center justify-center">
                        <Monitor className="h-8 w-8 text-blue-400" />
                      </div>
                    </motion.div>
                    <p className="text-lg font-medium bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-blue-500">
                      Demo Video Placeholder
                    </p>
                    <p className="text-slate-400 text-sm mt-1">Click to watch the demonstration</p>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 40 }}
            whileInView={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.7 }}
            viewport={{ once: true }}
            className="relative"
          >
            <div className="absolute -top-10 -right-10 w-40 h-40 bg-blue-500/10 rounded-full blur-3xl"></div>
            
            <h3 className="text-3xl font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-blue-500">
              Computer Vision Technology
            </h3>
            <p className="text-slate-300 mb-8">
              My Computer Vision projects bring together multiple interactive applications, allowing users to control digital interfaces using hand gestures tracked by a webcam. Experience the future of human-computer interaction.
            </p>

            <div className="space-y-4">
              {featureItems.map((item, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.4, delay: index * 0.1 }}
                  viewport={{ once: true }}
                  className="flex items-start gap-3 p-3 rounded-lg hover:bg-white/5 transition-colors"
                >
                  <div className={`p-2 rounded-lg bg-slate-800/80 border border-slate-700 ${item.color}`}>
                    <item.icon className="h-5 w-5" />
                  </div>
                  <span className="text-slate-200 mt-1">{item.text}</span>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}