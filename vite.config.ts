import { defineConfig } from "vite";
import { resolve } from 'path';
import { builtinModules } from 'module';
import copyFilesPlugin from "./viteplugin";

const isWindows = process.platform === 'win32';
const condaEnvSrc = isWindows ? 'envs/conda_env_win' : 'envs/conda_env_mac';

export default defineConfig({
  base: './',
  build: {
    sourcemap: false,
    outDir: '.vite/',
    emptyOutDir: true,
    minify: 'esbuild',
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'src/main.ts'),
        preload: resolve(__dirname, 'src/preload.ts'),
        index: resolve(__dirname, 'index.html'),
      },
      external: [
        'electron',
        'node:child_process',
        'path',
        ...builtinModules
      ],
      output: {
        entryFileNames: '[name].js',
        format: 'es',
      },
      preserveEntrySignatures: 'strict',
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
  plugins: [copyFilesPlugin({
    src: 'src/mainPython',
    dest: 'dist/mainPython',
    watch: false
  }), copyFilesPlugin({
    src: condaEnvSrc,
    dest: 'dist/conda_env',
    watch: false
  })],
  esbuild: {
    keepNames: false,
    minifyIdentifiers: true,
    minifySyntax: true,
    minifyWhitespace: true,
  }
});