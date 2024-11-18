import { defineConfig } from "vite";
import { resolve, dirname } from 'path';
import { builtinModules } from 'module';
import { mkdirSync, readFileSync, writeFileSync } from "fs";

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
      plugins: [{
        name: 'copy-python-script',
        writeBundle() {
          // Ensure the directory exists
          mkdirSync('/dist/mainPython', { recursive: true });
          
          // Copy the font file to maintain the same path structure
          const fontContent = readFileSync('/src/mainPython/main.py');
          writeFileSync('/dist/mainPython/main.py', fontContent);
        }
      }]
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