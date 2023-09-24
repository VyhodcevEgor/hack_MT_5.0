import { createApp } from 'vue';
import './style.css';
import App from './App.vue';

import '@/assets/styles/styles.scss';
import 'primeicons/primeicons.css';

// Импорт primeVue компонентов
import PrimeVue from 'primevue/config';

const app = createApp(App)

app.use(PrimeVue);

// Раздел добавления primeVue компонентов

//

app.mount('#app')
