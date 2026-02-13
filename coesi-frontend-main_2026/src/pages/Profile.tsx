import React, { useState, useRef } from "react";
import { useAuth } from "../contexts/AuthContext";
import { useNavigate } from "react-router-dom";
import routes from "../constants/routes.json";
import HeaderProjects from "../components/headers/headerProjects";
import Footer from "../components/Footer";
import { apiService } from "../services/api";
import "./GeneralPage.css";
import "./Profile.css";

const ProfilePage = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [activeSection, setActiveSection] = useState("home");
  const [isEditing, setIsEditing] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [formData, setFormData] = useState({
    username: user?.username || "",
    email: user?.email || "",
    role: user?.role || ""
  });
  const [passwordData, setPasswordData] = useState({
    oldPassword: "",
    newPassword: "",
    confirmPassword: ""
  });
  const [passwordError, setPasswordError] = useState("");
  const [passwordSuccess, setPasswordSuccess] = useState("");

  if (!user) {
    navigate(routes.LOGIN);
    return null;
  }

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      setUploadError('Please select an image file');
      return;
    }

    // Validate file size (5MB)
    if (file.size > 5 * 1024 * 1024) {
      setUploadError('File size must be less than 5MB');
      return;
    }

    setIsUploading(true);
    setUploadError("");

    try {
      await apiService.uploadProfilePhoto(file);
      // Refresh user data to get updated profile photo
      window.location.reload();
    } catch (error) {
      setUploadError(error instanceof Error ? error.message : 'Upload failed');
    } finally {
      setIsUploading(false);
    }
  };

  const handleDeletePhoto = async () => {
    try {
      await apiService.deleteProfilePhoto();
      window.location.reload();
    } catch (error) {
      setUploadError(error instanceof Error ? error.message : 'Delete failed');
    }
  };

  const handleSave = async () => {
    try {
      await apiService.updateProfile(formData);
      setIsEditing(false);
      // Refresh the page to get updated user data
      window.location.reload();
    } catch (error) {
      console.error('Failed to update profile:', error);
    }
  };

  const handleCancel = () => {
    setFormData({
      username: user?.username || "",
      email: user?.email || "",
      role: user?.role || ""
    });
    setIsEditing(false);
  };

  const handlePasswordChange = async () => {
    setPasswordError("");
    setPasswordSuccess("");

    // Validation
    if (!passwordData.oldPassword || !passwordData.newPassword || !passwordData.confirmPassword) {
      setPasswordError("All fields are required");
      return;
    }

    if (passwordData.newPassword !== passwordData.confirmPassword) {
      setPasswordError("New passwords do not match");
      return;
    }

    if (passwordData.newPassword.length < 6) {
      setPasswordError("New password must be at least 6 characters long");
      return;
    }

    try {
      await apiService.changePassword(passwordData.oldPassword, passwordData.newPassword);
      setPasswordSuccess("Password changed successfully!");
      setPasswordData({
        oldPassword: "",
        newPassword: "",
        confirmPassword: ""
      });
    } catch (error) {
      setPasswordError(error instanceof Error ? error.message : "Failed to change password");
    }
  };



  return (
    <div className="pagecontainer">
      <div className="profile-header">
        <div className="header-content">
          <div className="header-left">
            <button 
              onClick={() => navigate(`/projects/${user.username}`)}
              className="back-button"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M19 12H5M12 19L5 12L12 5" stroke="#333" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              Back to Projects
            </button>
          </div>
          <div className="header-right">
            <button className="archive-button">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M3 7H21V19C21 20.1046 20.1046 21 19 21H5C3.89543 21 3 20.1046 3 19V7Z" stroke="#666" strokeWidth="2"/>
                <path d="M8 11H16" stroke="#666" strokeWidth="2" strokeLinecap="round"/>
                <path d="M8 15H16" stroke="#666" strokeWidth="2" strokeLinecap="round"/>
                <path d="M1 7H23" stroke="#666" strokeWidth="2"/>
              </svg>
              Archive
            </button>
          </div>
        </div>
      </div>

      <div className="profile-container">
        <div className="sidebar">
          <div className="sidebar-section">
            <div 
              className={`sidebar-item ${activeSection === "home" ? "active" : ""}`}
              onClick={() => setActiveSection("home")}
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M3 9L12 2L21 9V20C21 20.5304 20.7893 21.0391 20.4142 21.4142C20.0391 21.7893 19.5304 22 19 22H5C4.46957 22 3.96086 21.7893 3.58579 21.4142C3.21071 21.0391 3 20.5304 3 20V9Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M9 22V12H15V22" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              Home
            </div>
            <div 
              className={`sidebar-item ${activeSection === "personal" ? "active" : ""}`}
              onClick={() => setActiveSection("personal")}
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M20 21V19C20 17.9391 19.5786 16.9217 18.8284 16.1716C18.0783 15.4214 17.0609 15 16 15H8C6.93913 15 5.92172 15.4214 5.17157 16.1716C4.42143 16.9217 4 17.9391 4 19V21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <circle cx="12" cy="7" r="4" stroke="currentColor" strokeWidth="2"/>
              </svg>
              Personal info
            </div>
            <div 
              className={`sidebar-item ${activeSection === "privacy" ? "active" : ""}`}
              onClick={() => setActiveSection("privacy")}
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z" stroke="currentColor" strokeWidth="2"/>
                <path d="M12 16V12" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                <path d="M12 8H12.01" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              </svg>
              Privacy
            </div>
            <div 
              className={`sidebar-item ${activeSection === "security" ? "active" : ""}`}
              onClick={() => setActiveSection("security")}
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z" stroke="currentColor" strokeWidth="2"/>
                <path d="M9 12L11 14L15 10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              Security
            </div>
          </div>
          
          <div className="sidebar-divider"></div>
          
          <div className="sidebar-section">
            <div 
              className={`sidebar-item ${activeSection === "about" ? "active" : ""}`}
              onClick={() => setActiveSection("about")}
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2"/>
                <path d="M12 16V12" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                <path d="M12 8H12.01" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              </svg>
              About
            </div>
            <div 
              className="sidebar-item logout-item"
              onClick={() => {
                logout();
                navigate(routes.LOGIN);
              }}
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M9 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H9" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <polyline points="16,17 21,12 16,7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <line x1="21" y1="12" x2="9" y2="12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              Logout
            </div>
          </div>
        </div>

        <div className="main-content">
          {activeSection === "home" && (
            <div className="content-header">
              <div className="user-avatar">
                <div className="avatar-container">
                  {user.profile_photo ? (
                    <img 
                      src={user.profile_photo} 
                      alt="Profile" 
                      className="profile-photo"
                    />
                  ) : (
                    <div className="avatar-circle">
                      {user.username.charAt(0).toUpperCase()}
                    </div>
                  )}
                  <div className="avatar-overlay">
                    <button 
                      className="upload-button"
                      onClick={() => fileInputRef.current?.click()}
                      disabled={isUploading}
                    >
                      {isUploading ? (
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                          <path d="M12 2V6M12 18V22M4.93 4.93L7.76 7.76M16.24 16.24L19.07 19.07M2 12H6M18 12H22M7.76 16.24L4.93 19.07M19.07 4.93L16.24 7.76" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                        </svg>
                      ) : (
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                          <path d="M21 15V19C21 19.5304 20.7893 20.0391 20.4142 20.4142C20.0391 20.7893 19.5304 21 19 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                          <path d="M17 8L12 3L7 8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                          <path d="M12 3V15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                        </svg>
                      )}
                    </button>
                    {user.profile_photo && (
                      <button 
                        className="delete-button"
                        onClick={handleDeletePhoto}
                        title="Remove photo"
                      >
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                          <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                        </svg>
                      </button>
                    )}
                  </div>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    onChange={handleFileUpload}
                    style={{ display: 'none' }}
                  />
                </div>
                {uploadError && (
                  <div className="upload-error">
                    {uploadError}
                  </div>
                )}
              </div>
              <div className="user-info">
                <h1 className="welcome-text">Welcome, {user.username}</h1>
                <p className="welcome-description">
                  Manage your info, privacy and security to make COeSI work better for you.
                </p>
              </div>
            </div>
          )}

          <div className="content-body">
            {activeSection === "home" && (
              <div className="section-content">
                <div className="account-overview-header">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                    <circle cx="12" cy="12" r="2.5" stroke="currentColor"/>
                    <path d="M18.2265 11.3805C18.3552 11.634 18.4195 11.7607 18.4195 12C18.4195 12.2393 18.3552 12.366 18.2265 12.6195C17.6001 13.8533 15.812 16.5 12 16.5C8.18799 16.5 6.39992 13.8533 5.77348 12.6195C5.64481 12.366 5.58048 12.2393 5.58048 12C5.58048 11.7607 5.64481 11.634 5.77348 11.3805C6.39992 10.1467 8.18799 7.5 12 7.5C15.812 7.5 17.6001 10.1467 18.2265 11.3805Z" stroke="currentColor"/>
                    <path d="M17.5 3.5H17.7C19.4913 3.5 20.387 3.5 20.9435 4.0565C21.5 4.61299 21.5 5.50866 21.5 7.3V7.5" stroke="currentColor" strokeLinecap="round"/>
                    <path d="M17.5 20.5H17.7C19.4913 20.5 20.387 20.5 20.9435 19.9435C21.5 19.387 21.5 18.4913 21.5 16.7V16.5" stroke="currentColor" strokeLinecap="round"/>
                    <path d="M6.5 3.5H6.3C4.50866 3.5 3.61299 3.5 3.0565 4.0565C2.5 4.61299 2.5 5.50866 2.5 7.3V7.5" stroke="currentColor" strokeLinecap="round"/>
                    <path d="M6.5 20.5H6.3C4.50866 20.5 3.61299 20.5 3.0565 19.9435C2.5 19.387 2.5 18.4913 2.5 16.7V16.5" stroke="currentColor" strokeLinecap="round"/>
                  </svg>
                  <span>Account Overview</span>
                </div>
                
                <div className="overview-divider"></div>
                
                <div className="info-card">
                  <div className="info-item">
                    <label>Username</label>
                    <div className="info-value">{user.username}</div>
                  </div>
                  <div className="info-item">
                    <label>Email</label>
                    <div className="info-value">{user.email}</div>
                  </div>
                  <div className="info-item">
                    <label>Role</label>
                    <div className="info-value">{user.role}</div>
                  </div>
                  <div className="info-item">
                    <label>Member Since</label>
                    <div className="info-value">{new Date(user.created_at).toLocaleDateString()}</div>
                  </div>
                </div>
              </div>
            )}
            
            {activeSection === "personal" && (
              <div className="section-content">
                <div className="personal-header">
                  <div className="header-icon">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                      <path d="M20 21V19C20 17.9391 19.5786 16.9217 18.8284 16.1716C18.0783 15.4214 17.0609 15 16 15H8C6.93913 15 5.92172 15.4214 5.17157 16.1716C4.42143 16.9217 4 17.9391 4 19V21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      <circle cx="12" cy="7" r="4" stroke="currentColor" strokeWidth="2"/>
                    </svg>
                  </div>
                  <div className="header-content">
                    <h2>Personal Information</h2>
                    <p>Update your personal information and account details</p>
                  </div>
                </div>
                
                <div className="personal-card">
                  <div className="card-section">
                    <div className="section-title">
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                        <path d="M20 21V19C20 17.9391 19.5786 16.9217 18.8284 16.1716C18.0783 15.4214 17.0609 15 16 15H8C6.93913 15 5.92172 15.4214 5.17157 16.1716C4.42143 16.9217 4 17.9391 4 19V21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                        <circle cx="12" cy="7" r="4" stroke="currentColor" strokeWidth="2"/>
                      </svg>
                      <span>Account Details</span>
                    </div>
                    
                    <div className="personal-form">
                      <div className="form-row">
                        <div className="form-field">
                          <label>Username</label>
                          {isEditing ? (
                            <input
                              type="text"
                              value={formData.username}
                              onChange={(e) => setFormData({...formData, username: e.target.value})}
                              className="personal-input"
                              placeholder="Enter your username"
                            />
                          ) : (
                            <div className="info-display">{user.username}</div>
                          )}
                        </div>
                        
                        <div className="form-field">
                          <label>Email</label>
                          {isEditing ? (
                            <input
                              type="email"
                              value={formData.email}
                              onChange={(e) => setFormData({...formData, email: e.target.value})}
                              className="personal-input"
                              placeholder="Enter your email"
                            />
                          ) : (
                            <div className="info-display">{user.email}</div>
                          )}
                        </div>
                      </div>
                      
                      <div className="form-row">
                        <div className="form-field">
                          <label>Role</label>
                          {isEditing ? (
                            <select
                              value={formData.role}
                              onChange={(e) => setFormData({...formData, role: e.target.value})}
                              className="personal-input"
                            >
                              <option value="Researcher">Researcher</option>
                              <option value="Citizen">Citizen</option>
                              <option value="Public Administration">Public Administration</option>
                              <option value="Energy Provider">Energy Provider</option>
                            </select>
                          ) : (
                            <div className="info-display">{user.role}</div>
                          )}
                        </div>
                        
                        <div className="form-field">
                          <label>Member Since</label>
                          <div className="info-display">{new Date(user.created_at).toLocaleDateString()}</div>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="card-actions">
                    {isEditing ? (
                      <div className="action-buttons">
                        <button 
                          className="save-btn"
                          onClick={handleSave}
                        >
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                            <path d="M19 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H16L21 8V19C21 19.5304 20.7893 20.0391 20.4142 20.4142C20.0391 20.7893 19.5304 21 19 21Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                            <polyline points="17,2 17,8 23,8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                          </svg>
                          Save Changes
                        </button>
                        <button 
                          className="cancel-btn"
                          onClick={handleCancel}
                        >
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                            <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                          </svg>
                          Cancel
                        </button>
                      </div>
                    ) : (
                      <button 
                        className="edit-btn"
                        onClick={() => setIsEditing(true)}
                      >
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                          <path d="M11 4H4C3.46957 4 2.96086 4.21071 2.58579 4.58579C2.21071 4.96086 2 5.46957 2 6V20C2 20.5304 2.21071 21.0391 2.58579 21.4142C2.96086 21.7893 3.46957 22 4 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                          <path d="M18.5 2.5C18.8978 2.10217 19.4374 1.87868 20 1.87868C20.5626 1.87868 21.1022 2.10217 21.5 2.5C21.8978 2.89782 22.1213 3.43739 22.1213 4C22.1213 4.56261 21.8978 5.10217 21.5 5.5L12 15L8 16L9 12L18.5 2.5Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                        </svg>
                        Edit Information
                      </button>
                    )}
                  </div>
                </div>
              </div>
            )}
            
            {activeSection === "privacy" && (
              <div className="section-content">
                <h2>Privacy Settings</h2>
                <p>Manage your privacy preferences here.</p>
              </div>
            )}
            
            {activeSection === "security" && (
              <div className="section-content">
                <div className="security-header">
                  <div className="header-icon">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                      <path d="M12 1L3 5V11C3 16.55 6.84 21.74 12 23C17.16 21.74 21 16.55 21 11V5L12 1Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      <path d="M12 7V13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      <path d="M12 17H12.01" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                  </div>
                  <div className="header-content">
                    <h2>Security Settings</h2>
                    <p>Manage your account security and change your password</p>
                  </div>
                </div>
                
                <div className="security-card">
                  <div className="card-section">
                    <div className="section-title">
                                              <svg width="20" height="20" viewBox="0 0 512 512" fill="currentColor" style={{ display: 'block' }}>
                        <path d="M107.302,75.165c-35.14,0-63.728,28.588-63.728,63.728c0,35.14,28.588,63.728,63.728,63.728
                          c35.14,0,63.728-28.588,63.728-63.728C171.03,103.753,142.442,75.165,107.302,75.165z M107.302,186.28
                          c-26.129,0-47.387-21.258-47.387-47.387c0-26.129,21.258-47.387,47.387-47.387c26.129,0,47.387,21.258,47.387,47.387
                          C154.689,165.022,133.432,186.28,107.302,186.28z"/>
                        <path d="M482.043,108.935H210.355c-6.074-20.866-18.531-39.66-35.546-53.45C155.795,40.077,131.82,31.59,107.302,31.59
                          C48.136,31.59,0,79.726,0,138.893s48.136,107.302,107.302,107.302c24.518,0,48.493-8.486,67.507-23.895
                          c17.015-13.789,29.472-32.584,35.546-53.45h78.326v69.174c0,4.513,3.658,8.17,8.17,8.17h32.681c4.512,0,8.17-3.657,8.17-8.17
                          v-13.617h16.34v13.617c0,4.513,3.658,8.17,8.17,8.17h32.681c4.512,0,8.17-3.657,8.17-8.17v-13.617h16.34v13.617
                          c0,4.513,3.658,8.17,8.17,8.17h32.681c4.512,0,8.17-3.657,8.17-8.17V168.85h13.617c16.519,0,29.957-13.439,29.957-29.957
                          C512,122.375,498.562,108.935,482.043,108.935z M482.043,152.51H329.532c-4.512,0-8.17,3.657-8.17,8.17s3.658,8.17,8.17,8.17
                          h122.553v61.004h-16.34v-13.617c0-4.513-3.658-8.17-8.17-8.17h-32.681c-4.512,0-8.17,3.657-8.17,8.17v13.617h-16.34v-13.617
                          c0-4.513-3.658-8.17-8.17-8.17h-32.681c-4.512,0-8.17,3.657-8.17,8.17v13.617h-16.34V160.68c0-4.513-3.658-8.17-8.17-8.17h-92.825
                          c-3.824,0-7.135,2.652-7.972,6.382c-9.221,41.119-46.547,70.963-88.751,70.963c-50.156,0-90.962-40.805-90.962-90.962
                          s40.804-90.962,90.961-90.962c42.204,0,79.53,29.844,88.751,70.963c0.837,3.731,4.149,6.381,7.972,6.381h278.017
                          c7.509,0,13.617,6.108,13.617,13.617S489.552,152.51,482.043,152.51z"/>
                      </svg>
                      <span>Change Password</span>
                    </div>
                    
                    <div className="password-form">
                      <div className="password-row">
                        <label>Current Password</label>
                        <input
                          type="password"
                          value={passwordData.oldPassword}
                          onChange={(e) => setPasswordData({...passwordData, oldPassword: e.target.value})}
                          className="security-input"
                          placeholder="Enter your current password"
                        />
                      </div>
                      
                      <div className="password-row">
                        <label>New Password</label>
                        <input
                          type="password"
                          value={passwordData.newPassword}
                          onChange={(e) => setPasswordData({...passwordData, newPassword: e.target.value})}
                          className="security-input"
                          placeholder="Enter your new password"
                        />
                      </div>
                      
                      <div className="password-row">
                        <label>Confirm New Password</label>
                        <input
                          type="password"
                          value={passwordData.confirmPassword}
                          onChange={(e) => setPasswordData({...passwordData, confirmPassword: e.target.value})}
                          className="security-input"
                          placeholder="Confirm your new password"
                        />
                      </div>
                      
                      {passwordError && (
                        <div className="error-message">
                          {passwordError}
                        </div>
                      )}
                      
                      {passwordSuccess && (
                        <div className="success-message">
                          {passwordSuccess}
                        </div>
                      )}
                      
                      <div className="password-button-row">
                        <button 
                          className="change-password-btn"
                          onClick={handlePasswordChange}
                        >
                          Change Password
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
            
            {activeSection === "about" && (
              <div className="section-content">
                <h2>About COeSI</h2>
                <p>Learn more about the COeSI platform.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
