import path from "path"
import react from "@vitejs/plugin-react"
import { defineConfig, loadEnv } from "vite"

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  return {
    base: "./",
    plugins: [react()],
    resolve: {
      alias: {
        "@": path.resolve(__dirname, "./src"),
      },
    },
    server: {
      proxy: {
        "/chat": {
          target: "http://localhost:8000",
          changeOrigin: false,
          secure: false,
        },
        "/mcp": {
          target: env.VITE_MCP_GATEWAY_URL || "http://localhost:8000/mcp",
          changeOrigin: false,
          secure: false,
          rewrite: (p) => p.replace(/^\/mcp/, ""),
        },
      },
    },
  }
})
