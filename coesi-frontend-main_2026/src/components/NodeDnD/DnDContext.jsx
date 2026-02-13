// @ts-nocheck
import React, { createContext, useContext, useState } from 'react';
import "@xyflow/react/dist/style.css";
 
const DnDContext = createContext([null, (_) => {}]);
 
export const DnDProvider = ({ children }) => {
  const [type, setType] = useState(null);
 
  return (
    <DnDContext.Provider value={[type, setType]}>
      {children}
    </DnDContext.Provider>
  );
}
 
export default DnDContext;
 
export const useDnD = () => {
  return useContext(DnDContext);
}