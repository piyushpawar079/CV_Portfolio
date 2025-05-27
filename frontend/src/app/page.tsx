import Hero from '@/components/Hero';
import AboutSection from '@/components/AboutSection';
import TechStack from '@/components/TechStack';

export default function Home() {
  return (
    <div className="container mx-auto">
      <Hero />
      <AboutSection />
      {/* <TechStack /> */}
    </div>
  );
}