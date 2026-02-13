import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import routes from '../constants/routes.json';

interface PublicRouteProps {
  children: React.ReactNode;
}

const PublicRoute: React.FC<PublicRouteProps> = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        fontSize: '18px',
        color: '#666'
      }}>
        Loading...
      </div>
    );
  }

  if (isAuthenticated) {
    // Redirect to projects page with user's name
    return <Navigate to={`/projects/${localStorage.getItem('username') || 'user'}`} replace />;
  }

  return <>{children}</>;
};

export default PublicRoute;
