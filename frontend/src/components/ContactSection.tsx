"use client";

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Send } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent } from '@/components/ui/card';
import { toast } from 'sonner';

export default function ContactSection() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    message: '',
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    // Simulate form submission
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    toast("Thanks for reaching out. I'll get back to you soon.");

    setFormData({ name: '', email: '', message: '' });
    setIsSubmitting(false);
  };

  if (!isMounted) return null;

  return (
    <section id="contact" className="py-24 md:py-32 relative overflow-hidden bg-gradient-to-br from-slate-950 to-indigo-950">
      {/* Animated background elements */}
      <div className="absolute inset-0 -z-10">
        <motion.div
          animate={{ 
            x: [0, 30, 0], 
            y: [0, -20, 0],
            opacity: [0.4, 0.6, 0.4] 
          }}
          transition={{ repeat: Infinity, duration: 10, ease: "easeInOut" }}
          className="absolute top-20 left-10 w-72 h-72 bg-purple-500/20 rounded-full blur-3xl"
        />
        <motion.div
          animate={{ 
            x: [0, -30, 0], 
            y: [0, 20, 0],
            opacity: [0.3, 0.5, 0.3] 
          }}
          transition={{ repeat: Infinity, duration: 8, ease: "easeInOut" }}
          className="absolute bottom-20 right-10 w-96 h-96 bg-cyan-500/20 rounded-full blur-3xl"
        />
        <motion.div
          animate={{ 
            x: [0, 20, 0], 
            y: [0, 30, 0],
            opacity: [0.2, 0.4, 0.2] 
          }}
          transition={{ repeat: Infinity, duration: 12, ease: "easeInOut" }}
          className="absolute bottom-40 left-40 w-80 h-80 bg-blue-500/20 rounded-full blur-3xl"
        />
      </div>

      {/* Grid Pattern Overlay */}
      <div className="absolute inset-0 bg-grid-white/[0.05] bg-[length:50px_50px] opacity-20"></div>

      <div className="container mx-auto px-4 relative z-10">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="text-center mb-12 max-w-4xl mx-auto"
        >
          <h2 className="text-5xl md:text-6xl font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-600">
            Get in Touch
          </h2>
          <p className="text-xl md:text-2xl mb-10 text-slate-300">
            Have a question about my 
            <span className="relative inline-block mx-2">
              <span className="relative z-10 text-white font-semibold">projects</span>
              <span className="absolute -bottom-1 left-0 right-0 h-3 bg-purple-500/30 blur-sm"></span>
            </span>
            or interested in collaboration? Drop me a message!
          </p>
        </motion.div>
        
        {/* Contact Form */}
        <div className="grid md:grid-cols-2 gap-8 items-center max-w-4xl mx-auto">
          <motion.div
            initial={{ opacity: 0, x: -40 }}
            whileInView={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            viewport={{ once: true }}
          >
            <Card className="bg-slate-900/50 border border-slate-800/50 backdrop-blur-md shadow-xl hover:shadow-purple-500/10 transition-all duration-300">
              <CardContent className="p-6">
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div>
                    <Input
                      placeholder="Your Name"
                      name="name"
                      value={formData.name}
                      onChange={handleChange}
                      required
                      className="bg-slate-800/50 border-slate-700 focus:border-purple-500/50 text-slate-200"
                    />
                  </div>
                  <div>
                    <Input
                      type="email"
                      placeholder="Your Email"
                      name="email"
                      value={formData.email}
                      onChange={handleChange}
                      required
                      className="bg-slate-800/50 border-slate-700 focus:border-cyan-500/50 text-slate-200"
                    />
                  </div>
                  <div>
                    <Textarea
                      placeholder="Your Message"
                      name="message"
                      value={formData.message}
                      onChange={handleChange}
                      rows={5}
                      required
                      className="bg-slate-800/50 border-slate-700 focus:border-blue-500/50 text-slate-200 min-h-32"
                    />
                  </div>
                  <Button 
                    type="submit" 
                    disabled={isSubmitting} 
                    className="w-full mt-4 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white font-medium px-6 py-6 rounded-xl shadow-lg shadow-blue-500/20 border-0"
                  >
                    {isSubmitting ? (
                      <div className="flex items-center justify-center gap-2">
                        <div className="animate-spin h-5 w-5 border-2 border-current border-t-transparent rounded-full" />
                        <span>Sending...</span>
                      </div>
                    ) : (
                      <div className="flex items-center justify-center gap-2">
                        <Send className="h-5 w-5" />
                        <span>Send Message</span>
                      </div>
                    )}
                  </Button>
                </form>
              </CardContent>
            </Card>
          </motion.div>
          
          {/* Info Section */}
          <motion.div
            initial={{ opacity: 0, x: 40 }}
            whileInView={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            viewport={{ once: true }}
            className="space-y-8"
          >
            <div>
              <h3 className="text-2xl font-bold mb-3 text-white">Let's Connect</h3>
              <p className="text-lg text-slate-300">
                I'm always interested in discussing new projects, creative ideas, or opportunities to be part of your vision.
              </p>
            </div>
            
          </motion.div>
        </div>
      </div>

      {/* Tech Pattern Bottom */}
      <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-slate-950/80 to-transparent"></div>
    </section>
  );
}