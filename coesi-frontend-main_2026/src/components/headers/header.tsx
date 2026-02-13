import React, { useState, useEffect, useRef } from "react";

import { useSelector } from "react-redux";
import type { RootState } from "../../main";

import routes from "../../constants/routes.json";
import { Link } from "react-router-dom";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";

import HeaderButton from "../buttons/headerButton";
import LoginButton from "../buttons/loginButton";

export default function Header() {
  const isLoggedIn = useSelector((state: RootState) => state.auth.isLoggedIn);
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [activeSection, setActiveSection] = useState("");
  const [profileDropdownOpen, setProfileDropdownOpen] = useState(false);
  const profileDropdownRef = useRef<HTMLDivElement | null>(null);
  
  const handleClick = () => {
    console.log("Navigating to login..."); // Debug log
    navigate(routes.LOGIN); // or navigate("/login") directly to test
  };

  const handleProfileClick = () => {
    setProfileDropdownOpen(!profileDropdownOpen);
  };

  const handleDashboard = () => {
    setProfileDropdownOpen(false);
    navigate(`/projects/${user?.username}`);
  };

  const handleLogout = () => {
    logout();
    navigate(routes.LOGIN);
  };

  const handleProfile = () => {
    setProfileDropdownOpen(false);
    navigate(routes.PROFILE);
  };

  const scrollToSection = (sectionId: string) => {
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ 
        behavior: 'smooth',
        block: 'start'
      });
    }
  };

  // Handle scroll-based highlighting using Intersection Observer
  useEffect(() => {
    const sections = [
      { id: 'intro-section', button: 'about' },
      { id: 'publications-section', button: 'publications' },
      { id: 'details-section', button: 'learn' },
      { id: 'green-section', button: 'community' }
    ];

    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const sectionId = entry.target.id;
          const section = sections.find(s => s.id === sectionId);
          if (section) {
            console.log('Section in view:', section.button);
            setActiveSection(section.button);
          }
        }
      });
    }, {
      threshold: 0.3, // Trigger when 30% of section is visible
      rootMargin: '-80px 0px 0px 0px' // Account for header height
    });

    // Observe all sections
    sections.forEach((section) => {
      const element = document.getElementById(section.id);
      if (element) {
        observer.observe(element);
        console.log('Observing section:', section.id);
      } else {
        console.log('Section not found:', section.id);
      }
    });

    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        profileDropdownOpen &&
        profileDropdownRef.current &&
        !profileDropdownRef.current.contains(event.target as Node)
      ) {
        setProfileDropdownOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [profileDropdownOpen]);

  return (
    <div
      className="header"
      style={{
        width: "100%",
        height: "10vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "0 40px",
        backgroundColor: "#fff",
        position: "fixed", // <-- make it fixed
        top: 0,            // <-- stick to top
        left: 0,
        zIndex: 1000,      // <-- ensure it's above everything
        boxSizing: "border-box",
        borderBottom: "0.5px solid rgba(128, 128, 128, 0.3)",
      }}
    >
      <div>
        <Link to={`${routes.LANDING}`}>
          <img
            src="/urbansim/logo-coesi.png"
            alt="Logo"
            style={{ height: "40px", width: "auto" }}
          />
        </Link>
      </div>

      <div style={{ display: "flex", gap: "20px", alignItems: "center" }}>
        <HeaderButton 
          label="About" 
          onClick={() => scrollToSection('intro-section')} 
          isActive={activeSection === 'about'}
        />
        <HeaderButton 
          label="Publications" 
          onClick={() => scrollToSection('publications-section')} 
          isActive={activeSection === 'publications'}
        />
        <HeaderButton 
          label="Learn" 
          onClick={() => scrollToSection('details-section')} 
          isActive={activeSection === 'learn'}
        />
        <HeaderButton 
          label="Community" 
          onClick={() => scrollToSection('green-section')} 
          isActive={activeSection === 'community'}
        />
      </div>

      <div
        style={{ width: "180px", display: "flex", justifyContent: "flex-end" }}
      >
        {!user ? (
          <LoginButton label="Login" onClick={handleClick} />
        ) : (
          <div style={{ position: "relative" }} ref={profileDropdownRef}>
            <button
              onClick={handleProfileClick}
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: "8px",
                width: "180px",
                height: "32px",
                minWidth: "180px",
                padding: "5px 44px",
                borderRadius: "30px",
                backgroundColor: "transparent",
                border: "1px solid #ddd",
                cursor: "pointer",
                fontFamily: "Host Grotesk, sans-serif",
                fontWeight: 500,
                fontSize: "16px",
                lineHeight: "100%",
                color: "#333",
                transition: "all 0.2s ease"
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = "#f5f5f5";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = "transparent";
              }}
            >
              <span>{user.username}</span>
              <svg
                width="12"
                height="12"
                viewBox="0 0 24 24"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
                style={{
                  transform: profileDropdownOpen ? "rotate(180deg)" : "rotate(0deg)",
                  transition: "transform 0.2s ease"
                }}
              >
                <path d="M6 9L12 15L18 9" stroke="#666" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </button>
            
            {profileDropdownOpen && (
              <div
                style={{
                  position: "absolute",
                  top: "100%",
                  right: 0,
                  backgroundColor: "white",
                  border: "1px solid #ccc",
                  borderRadius: "8px",
                  boxShadow: "0 4px 12px rgba(0,0,0,0.15)",
                  zIndex: 1000,
                  minWidth: "200px",
                  marginTop: "8px",
                  padding: "8px 0"
                }}
              >
                <div
                  onClick={handleProfile}
                  style={{
                    padding: "12px 16px",
                    cursor: "pointer",
                    fontSize: "14px",
                    color: "#333",
                    borderBottom: "1px solid #f0f0f0",
                    transition: "background-color 0.2s ease",
                    display: "flex",
                    alignItems: "center",
                    gap: "12px"
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = "#f5f5f5";
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = "white";
                  }}
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M20 21V19C20 17.9391 19.5786 16.9217 18.8284 16.1716C18.0783 15.4214 17.0609 15 16 15H8C6.93913 15 5.92172 15.4214 5.17157 16.1716C4.42143 16.9217 4 17.9391 4 19V21" stroke="#666" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    <circle cx="12" cy="7" r="4" stroke="#666" strokeWidth="2"/>
                  </svg>
                  <span>Profile</span>
                </div>
                <div
                  onClick={handleDashboard}
                  style={{
                    padding: "12px 16px",
                    cursor: "pointer",
                    fontSize: "14px",
                    color: "#333",
                    borderBottom: "1px solid #f0f0f0",
                    transition: "background-color 0.2s ease",
                    display: "flex",
                    alignItems: "center",
                    gap: "12px"
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = "#f5f5f5";
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = "white";
                  }}
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M3 12L12 3L21 12" stroke="#666" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    <path d="M5 10V20C5 20.5304 5.21071 21.0391 5.58579 21.4142C5.96086 21.7893 6.46957 22 7 22H17C17.5304 22 18.0391 21.7893 18.4142 21.4142C18.7893 21.0391 19 20.5304 19 20V10" stroke="#666" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                  <span>Dashboard</span>
                </div>
                <div
                  onClick={handleLogout}
                  style={{
                    padding: "12px 16px",
                    cursor: "pointer",
                    fontSize: "14px",
                    color: "#d32f2f",
                    transition: "background-color 0.2s ease",
                    display: "flex",
                    alignItems: "center",
                    gap: "12px"
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = "#ffebee";
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = "white";
                  }}
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M9 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H9" stroke="#d32f2f" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    <polyline points="16,17 21,12 16,7" stroke="#d32f2f" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    <line x1="21" y1="12" x2="9" y2="12" stroke="#d32f2f" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                  <span>Logout</span>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
