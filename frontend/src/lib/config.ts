const config = {
  backendUrl: process.env.NODE_ENV === 'production' 
    ? process.env.NEXT_PUBLIC_BACKEND_URL || 'https://cv-portfolio-backend.onrender.com'
    : 'http://localhost:5000',
  
  // WebSocket connection options for production
  socketOptions: {
    reconnection: true,
    reconnectionAttempts: 5,
    reconnectionDelay: 1000,
    timeout: 20000,
    forceNew: true,
    transports: ['websocket', 'polling'], // Fallback to polling if WebSocket fails
  }
};

export default config;