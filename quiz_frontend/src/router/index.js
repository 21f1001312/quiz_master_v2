import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '@/components/HomeView.vue';
import SignUp from '@/components/SignUp.vue';
import LogIn from '@/components/LogIn.vue';
import QmDash from '@/components/QmDash.vue';
import StudentDash from '@/components/StudentDash.vue';
import SubjectList from '@/components/SubjectList.vue';
import ChapterList from '@/components/ChapterList.vue';
import QuestionList from '@/components/QuestionList.vue';
import CreateQuiz from '@/components/CreateQuiz.vue';

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
      path: '/quizmaster',
      name: 'QmDash',
      component: QmDash,
    },
    {
      path: '/student',
      name: 'studentDash',
      component: StudentDash,
    },
    {
      path: '/subject',
      name: 'subjects',
      component: SubjectList,
    },
    {
      path: '/chapter',
      name: 'chapters',
      component: ChapterList,
    },
    {
      path: '/question',
      name: 'questions',
      component: QuestionList,
    },
    {
      path: '/create-quiz',
      name: 'createquiz',
      component: CreateQuiz,
    },
  ]
});

export default router;


