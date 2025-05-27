import { notFound } from 'next/navigation';
import { getProjectData } from '@/lib/projectData';
import DemoContainer from '@/components/DemoContainer';

export async function generateStaticParams() {
  const projects = getProjectData();
  return projects.map((project) => ({
    slug: project.id,
  }));
}

export default async function DemoPage({ params }: { params: { slug: string } }) {
  const data = await params;
  const project = getProjectData().find((p) => p.id ===  data.slug);
  
  if (!project) {
    notFound();
  }

  return (
    <div className="container ">
      {/* <BackButton /> */}
      <DemoContainer project={project} />
    </div>
  );
}