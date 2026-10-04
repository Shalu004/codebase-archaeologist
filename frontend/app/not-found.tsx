import React from 'react';
import Link from 'next/link';

export default function NotFound() {
  return (
    <div className="min-h-screen bg-dark-900 text-gray-100 flex flex-col items-center justify-center p-8 text-center font-sans">
      <h1 className="text-6xl font-extrabold text-brand-400 font-mono mb-4">404</h1>
      <h2 className="text-2xl font-bold text-white mb-2">Page Not Found</h2>
      <p className="text-sm text-gray-400 max-w-md mb-6">
        The requested resource or repository route does not exist in Codebase Archaeologist.
      </p>
      <Link
        href="/"
        className="px-6 py-3 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-semibold text-xs transition-all shadow-lg shadow-brand-600/20"
      >
        Return to Dashboard
      </Link>
    </div>
  );
}
