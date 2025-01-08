import { ForgeConfig } from '@electron-forge/shared-types';
import { MakerSquirrel } from '@electron-forge/maker-squirrel';
import { MakerZIP } from '@electron-forge/maker-zip';

const config: ForgeConfig = {
  packagerConfig: {
    asar: false,
    overwrite: true,
    prune: true,
    ignore: [
      "^/src",
      "^/envs",
      "^/.vscode",
      "^/.run",
      "^/.idea",
      "^/static",
      ".gitignore",
      "forge.config.ts",
      "postcss.config.js",
      "README.md",
      "style.css",
      "tailwind.config.js",
      "tsconfig.json",
      "vite.config.ts",
      "viteplugin.ts",
      "^/index.html",
    ],
  },
  makers: [new MakerSquirrel({}), new MakerZIP({}, ['darwin'])]
}

export default config;