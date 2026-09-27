import { defineConfig } from '@playwright/test';
export default defineConfig({ testDir: './tests', retries: process.env.CI ? 2 : 0 });
