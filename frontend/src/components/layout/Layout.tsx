import React from 'react';
import { Link } from 'react-router-dom';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-white shadow-sm">
        <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <Link to="/" className="flex items-center">
                <span className="text-xl font-bold text-blue-600">Direct File</span>
              </Link>
            </div>
            <div className="flex items-center space-x-4">
              <Link to="/dashboard" className="text-gray-600 hover:text-gray-900">Dashboard</Link>
              <Link to="/forms" className="text-gray-600 hover:text-gray-900">Forms</Link>
              <Link to="/settings" className="text-gray-600 hover:text-gray-900">Settings</Link>
            </div>
          </div>
        </nav>
      </header>

      <main className="flex-grow">
        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          {children}
        </div>
      </main>

      <footer className="bg-gray-50">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <p className="text-center text-gray-500 text-sm">
            © {new Date().getFullYear()} Direct File. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Layout; 