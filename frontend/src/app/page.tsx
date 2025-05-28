import Hero from '@/components/Hero';
import AboutSection from '@/components/AboutSection';

export default function Home() {
  return (
    <div className="container mx-auto">
      <Hero />
      <AboutSection />
    </div>
  );
}