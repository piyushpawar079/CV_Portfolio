"use client";

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Menu, X } from 'lucide-react';
import { motion } from 'framer-motion';

export default function Navbar() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);
  const pathname = usePathname();

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Function to check if a link is active
  const isLinkActive = (href: string) => {
    if (href === '/') {
      return pathname === '/';
    }
    
    if (href === '/#about') {
      return pathname === '/' && href.includes('#about');
    }
    
    return pathname.startsWith(href);
  };

  const navLinks = [
    { label: 'Home', href: '/' },
    // { label: 'About', href: '/#about' },
    { label: 'Projects', href: '/projects' },
    { label: 'Contact', href: '/contact' },
  ];

  return (
    <header 
      className={`fixed top-4 left-0 right-0 z-50 transition-all duration-300  ${
        isScrolled ? 'px-2' : 'px-4'
      }`}
    >
      <div 
        className={`mx-auto max-w-6xl rounded-xl  ${
          isScrolled 
            ? 'bg-slate-900/80 backdrop-blur-md border border-slate-800/50 shadow-lg shadow-blue-900/10' 
            : 'bg-slate-900/20 backdrop-blur-sm'
        }`}
      >
        <div className="container mx-auto px-10">
          <div className="flex items-center justify-between h-16 md:h-20">
            <Link href="/" className="font-bold text-xl md:text-2xl bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-blue-500">
              IntelliDesk
            </Link>

            {/* Desktop navigation */}
            <nav className="hidden md:flex items-center gap-8">
              {navLinks.map((link) => {
                const active = isLinkActive(link.href);

                return (
                  <Link
                    key={link.href}
                    href={link.href}
                    className={`relative group px-3 py-2 text-sm font-medium transition-all duration-300
                      ${active 
                        ? 'text-white' 
                        : 'text-slate-300 hover:text-white'
                      }
                    `}
                  >
                    {link.label}
                    
                    {/* Active indicator - glowing underline */}
                    {active ? (
                      <motion.span
                        layoutId="activeTab"
                        className="absolute left-0 right-0 bottom-0 h-0.5 bg-gradient-to-r from-cyan-400 to-blue-500 rounded-full shadow-sm shadow-blue-400/20"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ duration: 0.3 }}
                      />
                    ) : (
                      <span className="absolute left-0 right-0 bottom-0 h-0.5 bg-gradient-to-r from-cyan-400/0 via-blue-500/0 to-purple-500/0 rounded-full opacity-0 group-hover:opacity-30 transition-opacity duration-300" />
                    )}
                  </Link>
                );
              })}
            </nav>

            {/* CTA Button - Desktop only */}
            <div className="hidden md:block">
              <Link href={'https://github.com/piyushpawar079/CV_Hub'} className="px-4 py-2 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white border-0  rounded-lg font-medium shadow-md shadow-blue-500/20">
                GitHub Repo
              </Link>
            </div>

            {/* Mobile menu toggle */}
            <div className="flex items-center md:hidden">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setIsMenuOpen(!isMenuOpen)}
                aria-label="Toggle menu"
                className="text-slate-200 hover:bg-slate-800/50"
              >
                {isMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Mobile menu */}
      {isMenuOpen && (
        <motion.div 
          className="md:hidden bg-slate-900/95 backdrop-blur-md mt-2 rounded-xl border border-slate-800/50 p-4 shadow-lg mx-4"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.2 }}
        >
          <nav className="flex flex-col gap-1">
            {navLinks.map((link) => {
              const active = isLinkActive(link.href);

              return (
                <Link
                  key={link.href}
                  href={link.href}
                  className={`text-base font-medium transition-colors p-3 rounded-lg relative overflow-hidden ${
                    active 
                      ? 'text-white bg-gradient-to-r from-blue-500/20 to-purple-500/20 border border-blue-500/30'
                      : 'text-slate-200 hover:bg-slate-800/50'
                  }`}
                  onClick={() => setIsMenuOpen(false)}
                >
                  {active && (
                    <span className="absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b from-cyan-400 to-blue-500 rounded-r-full" />
                  )}
                  {link.label}
                </Link>
              );
            })}
            
            {/* CTA Button for Mobile */}
            <div className="mt-3 pt-3 border-t border-slate-800">
              <Button className="w-full bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white border-0 font-medium">
                Get Started
              </Button>
            </div>
          </nav>
        </motion.div>
      )}
    </header>
  );
}