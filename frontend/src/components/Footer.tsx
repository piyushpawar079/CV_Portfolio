import { Github, Linkedin, Twitter } from "lucide-react";

export default function Footer() {
  return (
    <footer className="relative py-12 bg-gradient-to-t from-slate-950 to-slate-900 overflow-hidden">
      {/* Subtle grid overlay */}
      <div className="absolute inset-0 bg-grid-white/[0.03] bg-[length:40px_40px]"></div>
      
      {/* Glowing edge at the top */}
      <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-blue-500/30 to-transparent"></div>
      
      {/* Subtle glowing accents */}
      <div className="absolute bottom-0 left-1/4 w-64 h-64 bg-blue-500/10 rounded-full blur-3xl"></div>
      <div className="absolute top-0 right-1/4 w-64 h-64 bg-purple-500/10 rounded-full blur-3xl"></div>
      
      <div className="container mx-auto px-4 relative z-10">
        <div className="flex flex-col md:flex-row justify-between items-center gap-8">
          <div className="text-center md:text-left">
            <div className="mb-3">
              <span className="font-bold text-2xl bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-blue-500">
                IntelliDesk
              </span>
            </div>
            <p className="text-sm text-slate-400">
              &copy; {new Date().getFullYear()} Computer Vision Portfolio. All rights reserved.
            </p>
          </div>
          
          <div className="flex items-center gap-6">
            <a
              href="https://github.com/piyushpawar079"
              target="_blank"
              rel="noopener noreferrer"
              className="p-2 rounded-lg bg-slate-800/80 border border-slate-700 text-slate-300 hover:text-cyan-400 hover:border-cyan-500/50 hover:bg-slate-800 transition-all duration-300"
            >
              <Github className="w-5 h-5" />
            </a>
            <a
              href="https://www.linkedin.com/in/piyush-pawar-bb9082297/"
              target="_blank"
              rel="noopener noreferrer"
              className="p-2 rounded-lg bg-slate-800/80 border border-slate-700 text-slate-300 hover:text-blue-400 hover:border-blue-500/50 hover:bg-slate-800 transition-all duration-300"
            >
              <Linkedin className="w-5 h-5" />
            </a>
            <a
              href="https://x.com/Piyush_Pawar079"
              target="_blank"
              rel="noopener noreferrer"
              className="p-2 rounded-lg bg-slate-800/80 border border-slate-700 text-slate-300 hover:text-purple-400 hover:border-purple-500/50 hover:bg-slate-800 transition-all duration-300"
            >
              <Twitter className="w-5 h-5" />
            </a>
          </div>
        </div>
        
        {/* <div className="mt-8 pt-8 border-t border-slate-800/80">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4 text-xs text-slate-500">
            <div>Designed with modern web technologies</div>
            <div className="flex gap-6">
              <a href="/privacy" className="hover:text-blue-400 transition-colors">Privacy Policy</a>
              <a href="/terms" className="hover:text-blue-400 transition-colors">Terms of Service</a>
            </div>
          </div>
        </div> */}
      </div>
    </footer>
  );
}