"use client";

import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { ChevronLeft } from 'lucide-react';

export default function BackButton() {
  const router = useRouter();
  
  return (
    <Button 
      variant="outline" 
      size="sm" 
      className="mb-6" 
      onClick={() => router.back()}
    >
      <ChevronLeft className="h-4 w-4 mr-1" /> Back
    </Button>
  );
}