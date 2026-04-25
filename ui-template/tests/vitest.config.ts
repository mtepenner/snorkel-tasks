import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    environment: "happy-dom",
    include: ["unit/**/*.spec.ts"],
    globals: true,
  },
});
