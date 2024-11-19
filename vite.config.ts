import { defineConfig } from "vite";
import { resolve, dirname } from 'path';
import { builtinModules } from 'module';
import { mkdirSync, readFileSync, writeFileSync } from "fs";
import copyFilesPlugin from "./viteplugin";

export default defineConfig({
  base: './',
  build: {
    outDir: '.vite/',
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'src/main.ts'),  // main.ts 파일
        preload: resolve(__dirname, 'src/preload.ts'),
        index: resolve(__dirname, 'index.html'),  // index.html 파일
      },
      external: [
        'electron',
        ...builtinModules
      ],
      output: {
        entryFileNames: '[name].js',
        format: 'cjs',
      },
      plugins: [copyFilesPlugin({
        src: '/src/anaconda_env',
        dest: '/dist/mainArea',
        watch: true
      })]
    },
  },
  server: {
    port: 3000,
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, './src'),
    },
  },
});