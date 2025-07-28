import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '@/components/HomeView.vue';
import SignUp from '@/components/SignUp.vue';
import LogIn from '@/components/LogIn.vue';
import QmDash from '@/components/QmDash.vue';
import StudentDash from '@/components/StudentDash.vue';
import SubjectList from '@/components/SubjectList.vue';
import EditSubject from '@/components/EditSubject.vue';
import ChapterList from '@/components/ChapterList.vue';
import EditChapter from '@/components/EditChapter.vue';
import QuestionList from '@/components/QuestionList.vue';
import EditQuestion from '@/components/EditQuestion.vue';
import CreateQuiz from '@/components/CreateQuiz.vue';
import EditQuiz from '@/components/EditQuiz.vue';
import AttemptQuiz from '@/components/AttemptQuiz.vue';
import SubmitQuiz from '@/components/AttemptQuiz.vue';

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
    {
      path: '/edit-quiz/:id',
      name: 'edit-quiz',
      component: EditQuiz,
    },
    {
      path: '/edit-subject/:id',
      name: 'edit-subject',
      component: EditSubject,
    },
    {
      path: '/edit-chapter/:id',
      name: 'edit-chapter',
      component: EditChapter,
    },
    {
      path: '/edit-question/:id',
      name: 'edit-question',
      component: EditQuestion,
    },
    {
      path: '/attempt-quiz/:id',
      name: 'attempt-quiz',
      component: AttemptQuiz,
    },
    {
      path: '/submit-quiz/:id',
      name: 'submit-quiz',
      component: SubmitQuiz,
    }

  ]
});

export default router;


