import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";


// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
    process.env = Object.assign(process.env, loadEnv(mode, process.cwd(), ''));
    return { 
        server: {
            proxy: {
                "/api": {
                    // For use to pull dynamic environment variables
                    // target: import.meta.env.VITE_BACKEND_URL
                    // For use to pull environment variables in dev server
                    // target: process.env.VITE_BACKEND_URL 
                    // Hardcoded backend
                    target:"http://localhost:8000",
                },
            },
        },
        plugins: [
            react(),
        ],
    };
});
