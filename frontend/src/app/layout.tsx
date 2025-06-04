import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { ThemeProvider } from '@/components/theme-provider';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import { Toaster } from 'sonner';
import { Analytics } from "@vercel/analytics/next"

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Computer Vision Portfolio',
  description: 'Interactive computer vision projects and demos',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <ThemeProvider
          attribute="class"
          defaultTheme="light"
          enableSystem
        >
          <div className="min-h-screen flex flex-col">
            <Navbar />
            <main className="flex-grow">
              {children}
              <Analytics />
            </main>
            <Toaster />
            <Footer />
          </div>
        </ThemeProvider>
      </body>
    </html>
  );
}