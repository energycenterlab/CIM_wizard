import React, { useState, useEffect, useRef } from "react";

import { useSelector } from "react-redux";
import type { RootState } from "../../main";

import routes from "../../constants/routes.json";
import { Link } from "react-router-dom";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";

import HeaderButton from "../buttons/headerButton";
import LoginButton from "../buttons/loginButton";
import BreadcrumbNavigation from "./BreadcrumbNavigation";

interface HeaderProjectsProps {
  onCreateProject?: () => void;
  onOpenProject?: () => void;
  hideCommunityArchive?: boolean;
  hideFileEditShow?: boolean;
  showBreadcrumb?: boolean;
  scenarioName?: string;
  projectId?: string;
  projectName?: string;
  onAddScenario?: () => void;
  useScenarioMenu?: boolean; // When true, shows scenario-specific menu instead of default menu
}

export default function HeaderProjects({ 
  onCreateProject, 
  onOpenProject, 
  hideCommunityArchive = false, 
  hideFileEditShow = false,
  showBreadcrumb = false,
  scenarioName = "baselineDemo",
  projectId = "projid",
  projectName = "projname",
  onAddScenario,
  useScenarioMenu = false
}: HeaderProjectsProps) {
  const isLoggedIn = useSelector((state: RootState) => state.auth.isLoggedIn);
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [fileDropdownOpen, setFileDropdownOpen] = useState(false);
  const [profileDropdownOpen, setProfileDropdownOpen] = useState(false);
  const [scenariosDropdownOpen, setScenariosDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement | null>(null);
  const profileDropdownRef = useRef<HTMLDivElement | null>(null);
  const scenariosDropdownRef = useRef<HTMLDivElement | null>(null);

  const handleClick = () => {
    console.log("Navigating to login..."); // Debug log
    navigate(routes.LOGIN); // or navigate("/login") directly to test
  };

  const handleArchiveClick = () => {
    // TODO: Implement archive page navigation
    console.log("Opening archive page");
    // Here you would typically navigate to an archive page
    // navigate("/archive");
  };

  const handleFileClick = () => {
    setFileDropdownOpen(!fileDropdownOpen);
  };

  const handleScenariosClick = () => {
    setScenariosDropdownOpen(!scenariosDropdownOpen);
  };

  const handleNewScenario = () => {
    setScenariosDropdownOpen(false);
    // Navigate to scenarios page with new=true to open drawer
    navigate(`${routes.SCENARIOSDEMO}?new=true`);
    onAddScenario?.();
  };

  const handleScenariosList = () => {
    setScenariosDropdownOpen(false);
    navigate(routes.SCENARIOSDEMO);
  };

  const handleProfileClick = () => {
    setProfileDropdownOpen(!profileDropdownOpen);
  };

  const handleCreateProject = () => {
    setFileDropdownOpen(false);
    onCreateProject?.();
  };

  const handleOpenProject = () => {
    setFileDropdownOpen(false);
    onOpenProject?.();
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

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        fileDropdownOpen &&
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setFileDropdownOpen(false);
      }
      if (
        profileDropdownOpen &&
        profileDropdownRef.current &&
        !profileDropdownRef.current.contains(event.target as Node)
      ) {
        setProfileDropdownOpen(false);
      }
      if (
        scenariosDropdownOpen &&
        scenariosDropdownRef.current &&
        !scenariosDropdownRef.current.contains(event.target as Node)
      ) {
        setScenariosDropdownOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [fileDropdownOpen, profileDropdownOpen, scenariosDropdownOpen]);

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
        position: "relative",
        zIndex: 999,
        boxSizing: "border-box",
        borderBottom: "0.5px solid rgba(128, 128, 128, 0.3)",
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center' }}>
        <Link to={`${routes.LANDING}`}>
          <img
            src="/urbansim/logo-coesi.png"
            alt="Logo"
            style={{ height: "40px", width: "auto" }}
          />
        </Link>
        {showBreadcrumb && (
          <BreadcrumbNavigation 
            scenarioName={scenarioName}
            projectId={projectId}
            projectName={projectName}
          />
        )}
      </div>

      <div style={{ display: "flex", gap: "20px", alignItems: "center" }}>
        {!hideFileEditShow && !useScenarioMenu && (
          <div style={{ position: "relative" }} ref={dropdownRef}>
            <HeaderButton label="File" onClick={handleFileClick} />
            {fileDropdownOpen && (
            <div
              style={{
                position: "absolute",
                top: "100%",
                left: 0,
                backgroundColor: "white",
                border: "1px solid #ccc",
                borderRadius: "4px",
                boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
                zIndex: 1000,
                minWidth: "200px",
                marginTop: "4px"
              }}
            >
              <div
                onClick={handleCreateProject}
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
                  <path d="M12 5V19M5 12H19" stroke="#4CAF50" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
                <span style={{ textAlign: "left" }}>Create a new project</span>
              </div>
              <div
                onClick={handleOpenProject}
                style={{
                  padding: "12px 16px",
                  cursor: "pointer",
                  fontSize: "14px",
                  color: "#333",
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
                  <path d="M4 5C4 3.89543 4.89543 3 6 3H9L11 5H20C21.1046 5 22 5.89543 22 7V19C22 20.1046 21.1046 21 20 21H4C2.89543 21 2 20.1046 2 19V7C2 5.89543 2.89543 5 4 5Z" stroke="#2196F3" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
                <span style={{ textAlign: "left" }}>Open project</span>
              </div>
            </div>
          )}
        </div>
        )}
        {!hideFileEditShow && (
          <>
            {useScenarioMenu ? (
              <>
                <div style={{ position: "relative" }} ref={scenariosDropdownRef}>
                  <HeaderButton 
                    label="Scenarios" 
                    onClick={handleScenariosClick} 
                  />
                  {scenariosDropdownOpen && (
                    <div
                      style={{
                        position: "absolute",
                        top: "100%",
                        left: 0,
                        backgroundColor: "white",
                        border: "1px solid #ccc",
                        borderRadius: "4px",
                        boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
                        zIndex: 1000,
                        minWidth: "200px",
                        marginTop: "4px"
                      }}
                    >
                      <div
                        onClick={handleNewScenario}
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
                          <path d="M12 5V19M5 12H19" stroke="#4CAF50" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                        </svg>
                        <span style={{ textAlign: "left" }}>New Scenario</span>
                      </div>
                      <div
                        onClick={handleScenariosList}
                        style={{
                          padding: "12px 16px",
                          cursor: "pointer",
                          fontSize: "14px",
                          color: "#333",
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
                          <path d="M4 5C4 3.89543 4.89543 3 6 3H9L11 5H20C21.1046 5 22 5.89543 22 7V19C22 20.1046 21.1046 21 20 21H4C2.89543 21 2 20.1046 2 19V7C2 5.89543 2.89543 5 4 5Z" stroke="#2196F3" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                        </svg>
                        <span style={{ textAlign: "left" }}>Scenarios List</span>
                      </div>
                    </div>
                  )}
                </div>
                <HeaderButton 
                  label="Inspect" 
                  onClick={() => navigate(`${routes.SCENARIOSDEMO}/inspect`)} 
                />
                <HeaderButton 
                  label="Δ Delta"
                  onClick={() => navigate(`${routes.SCENARIOSDEMO}/delta`)} 
                />
                <HeaderButton 
                  label="History" 
                  onClick={() => navigate(`${routes.SCENARIOSDEMO}/history`)} 
                />
              </>
            ) : (
              <>
                <HeaderButton label="Edit" onClick={() => {}} />
                <HeaderButton label="Show" onClick={() => {}} />
              </>
            )}
          </>
        )}
        {!hideCommunityArchive && !useScenarioMenu && (
          <>
            <HeaderButton label="Community" onClick={() => {}} />
            <HeaderButton label="History" onClick={handleArchiveClick} />
          </>
        )}
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
