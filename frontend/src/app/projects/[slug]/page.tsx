import { notFound } from 'next/navigation';
import { getProjectData } from '@/lib/projectData';
import ProjectDetails from '@/components/ProjectDetails';

export async function generateStaticParams() {
  const projects = getProjectData();
  return projects.map((project) => ({
    slug: project.id,
  }));
}

export default async function ProjectPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const project = getProjectData().find((p) => p.id === slug);
  
  if (!project) {
    notFound();
  }

  return (
    <div className="container">
      {/* <BackButton />  */}
      <ProjectDetails project={project} />
    </div>
  );
}