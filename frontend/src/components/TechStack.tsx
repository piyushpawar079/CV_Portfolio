"use client";

import { motion } from 'framer-motion';
import { Card, CardContent } from '@/components/ui/card';

export default function TechStack() {
  const technologies = [
    { name: 'Python', icon: '🐍' },
    { name: 'OpenCV', icon: '👁️' },
    { name: 'MediaPipe', icon: '🖐️' },
    { name: 'Flask', icon: '🧪' },
    { name: 'Socket.IO', icon: '🔌' },
    { name: 'Next.js', icon: '⚡' },
    { name: 'React', icon: '⚛️' },
    { name: 'TypeScript', icon: '📘' },
    { name: 'Tailwind CSS', icon: '🎨' },
  ];

  return (
    <section className="py-16 bg-muted/10">
      <div className="container mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          viewport={{ once: true }}
          className="text-center mb-12"
        >
          <h2 className="text-3xl font-bold mb-4">Tech Stack</h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Technologies powering my computer vision projects
          </p>
        </motion.div>
        
        <div className="grid grid-cols-3 md:grid-cols-5 lg:grid-cols-9 gap-4">
          {technologies.map((tech, index) => (
            <motion.div
              key={tech.name}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: index * 0.05 }}
              viewport={{ once: true }}
            >
              <Card className="h-full">
                <CardContent className="flex flex-col items-center justify-center p-4 text-center h-full">
                  <div className="text-3xl mb-2">{tech.icon}</div>
                  <p className="font-medium text-sm">{tech.name}</p>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}