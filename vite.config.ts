import { defineConfig } from "vite";
import { resolve, dirname } from 'path';
import { builtinModules } from 'module';
import copyFilesPlugin from "./viteplugin";

const isWindows = process.platform === 'win32';
const anacondaEnvSrc = isWindows ? 'envs/conda_env_win' : 'envs/conda_env_mac';

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
    watch: true
  }), copyFilesPlugin({
    src: anacondaEnvSrc,
    dest: 'dist/conda_env',
    watch: true
  })]
});