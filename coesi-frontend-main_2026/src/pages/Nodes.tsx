import React from "react";
import { useNavigate } from "react-router-dom";

import routes from "../constants/routes.json";
import HeaderNodes from "../components/headers/headerNodes";

import { ReactFlowProvider } from "@xyflow/react";
import { DnDProvider } from "../components/NodeDnD/DnDContext";
import DnDFlow from "../components/NodeDnD/DnDFlow";
import "@xyflow/react/dist/style.css";

const NodesPage = () => {
  /*
  const navigate = useNavigate();

  const login = () => {
    navigate(`${routes.PROJECTS}`);
  };*/

  return (
    <div className="pagecontainer">
      <HeaderNodes />
      <div className="mainbody">
        <ReactFlowProvider>
          <DnDProvider>
            <DnDFlow />
          </DnDProvider>
        </ReactFlowProvider>
      </div>
    </div>
  );
};

export default NodesPage;
