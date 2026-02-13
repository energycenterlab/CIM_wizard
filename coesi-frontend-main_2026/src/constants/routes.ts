import { API_CONFIG } from '../config/apiConfig';

const routes = {
  LOGIN: "/login",
  LANDING: "/*",
  PROJECTSDEMO: "/projects/userid",
  SCENARIOSDEMO: "/scenarios/projid==projname",
  COSIMO: "/cosimo",
  PROFILE: "/profile",
  NODES: "/configuration",
  SIGNUP: "/signup",
  SHELPER: API_CONFIG.COESI_API_BASE,
  INPUTEDITORDEMO: "/projid==projname-sceid==scename-inputeditordemo"
};

export default routes;


