import { notFound } from 'next/navigation';
import { getProjectData } from '@/lib/projectData';
import DemoContainer from '@/components/DemoContainer';

export async function generateStaticParams() {
  const projects = getProjectData();
  return projects.map((project) => ({
    slug: project.id,
  }));
}

export default async function DemoPage({ 
  params 
}: { 
  params: Promise<{ slug: string }> 
}) {
  // Await the params promise
  const { slug } = await params;
  
  const project = getProjectData().find((p) => p.id === slug);

  if (!project) {
    notFound();
  }

  return (
    <div className="container">
      <DemoContainer project={project} />
    </div>
  );
}