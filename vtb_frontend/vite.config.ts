import { defineConfig } from 'vite';
import { resolve } from 'path';
import vue from '@vitejs/plugin-vue';
import vueJsx from '@vitejs/plugin-vue-jsx';
import svgLoader from 'vite-svg-loader';

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [
      vue(),
      vueJsx(),
      svgLoader({ defaultImport: 'url' }),
    ],
    resolve: {
        alias: {
          '@': resolve('./src')
        }
    },
    css: {
        charset: 'utf-8'
    }
})
