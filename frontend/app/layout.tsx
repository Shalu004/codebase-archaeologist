import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Codebase Archaeologist - The Google Maps for an Unfamiliar Codebase',
  description: 'AI-powered codebase understanding, architecture visualizer, impact analysis, and developer onboarding platform.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-dark-900 text-gray-100 min-h-screen antialiased">
        {children}
      </body>
    </html>
  );
}
