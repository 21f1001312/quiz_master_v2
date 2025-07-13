import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '@/components/HomeView.vue';
import SignUp from '@/components/SignUp.vue';
import LogIn from '@/components/LogIn.vue';
import QmDash from '@/components/QmDash.vue';
import StudentDash from '@/components/StudentDash.vue';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/signup',
      name: 'signup',
      component: SignUp,
    },
    {
      path: '/login',
      name: 'login',
      component: LogIn,
    },
    {
      path: '/quizmaster/dashboard',
      name: 'qmDash',
      component: QmDash,
    },
    {
      path: '/student/dashboard',
      name: 'studentDash',
      component: StudentDash,
    },
  ]
});

export default router;


