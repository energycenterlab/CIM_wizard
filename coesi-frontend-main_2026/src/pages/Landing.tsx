import React from "react";
import { useNavigate } from "react-router-dom";

import Header from "../components/headers/header";
import routes from "../constants/routes.json";

import HeroSection from "../components/LandingSections/HeroSection";
import IntroSection from "../components/LandingSections/IntroSection";
import PublicationSection from "../components/LandingSections/PublicationSection";
import DetailsSection from "../components/LandingSections/DetailsSection";
import GreenSection from "../components/LandingSections/GreenSection";


import "./GeneralPage.css";
import "./Landing.css";
import Footer from "../components/Footer";

const LandingPage = () => {
  const navigate = useNavigate();

  const login = () => {
    navigate(`${routes.PROJECTSDEMO}`);
  };

  return (
    <div className="pagecontainer">
      <Header />
      <div className="mainbody landing-mainbody">
        <div className="full-bleed">
          <HeroSection />
        </div>

        <div className="full-bleed">
          <IntroSection />
        </div>
        <div className="full-bleed">
          <PublicationSection />
        </div>
        <div className="full-bleed">
          <DetailsSection />
        </div>

        <div className="full-bleed">
          <GreenSection />
        </div>

        <Footer />
      </div>
    </div>
  );
};

export default LandingPage;
