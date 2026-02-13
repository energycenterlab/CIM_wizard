import { ReactFlowProvider } from "@xyflow/react";
import { DnDProvider } from "../../components/NodeDnD/DnDContext";
import DnDFlowForSce from "../../components/NodeDnD/DnDFlowForScey";
import "@xyflow/react/dist/style.css";

const NodesConfig = ({ isLocked = false }: { isLocked?: boolean }) => {
  return (
    <ReactFlowProvider>
      <DnDProvider>
        <DnDFlowForSce isLocked={isLocked} />
      </DnDProvider>
    </ReactFlowProvider>
  );
};

export default NodesConfig;
