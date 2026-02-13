import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  // Required because the app is served behind the API gateway at /urbansim
  base: "/urbansim/",
});
