import { notFound } from 'next/navigation';
import { getProjectData } from '@/lib/projectData';
import ProjectDetails from '@/components/ProjectDetails';
import BackButton from '@/components/BackButton';

export async function generateStaticParams() {
  const projects = getProjectData();
  return projects.map((project) => ({
    slug: project.id,
  }));
}

export default function ProjectPage({ params }: { params: { slug: string } }) {
  const project = getProjectData().find((p) => p.id === params.slug);
  
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