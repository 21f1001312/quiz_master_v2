<template>
  <div>
    <!-- Navigation Bar -->
    <nav class="navbar bg-primary" data-bs-theme="dark">
      <div class="container">
        <a class="navbar-brand" href="#">Student Dashboard</a>
        <button class="btn btn-outline-light ms-auto" @click="logout">Logout</button>
      </div>
    </nav>

    <!-- Quiz Section -->
    <div class="container mt-5" v-if="quiz">
      <div class="card">
        <div class="card-header">
          <h5>{{ quiz.title }}</h5>
          <p class="mb-0">
            Subject: {{ quiz.subject_name }} | Chapter: {{ quiz.chapter_name }}
          </p>
        </div>
        <div class="card-body">
          <div v-if="!started">
            <button class="btn btn-primary" @click="startQuiz" style="font-size:1.2rem; padding:0.75rem 2rem;">
              Start Quiz
            </button>
            <div v-if="quiz.questions && quiz.questions.length === 0" class="text-danger mt-3">
              No questions in this quiz.
            </div>
          </div>
          <form v-if="started && quiz.questions && quiz.questions.length > 0" @submit.prevent="submitQuiz">
            <div v-for="(question, index) in quiz.questions" :key="question.id" class="mb-4">
              <h6>Q{{ index + 1 }}. {{ question.question_statement }}</h6>
              <div
                class="form-check"
                v-for="(optionKey, i) in ['option1', 'option2', 'option3', 'option4']"
                :key="i"
              >
                <input
                  class="form-check-input"
                  type="radio"
                  :name="'question_' + question.id"
                  :value="['a', 'b', 'c', 'd'][i]"
                  v-model="answers[question.id]"
                  :id="'q' + question.id + '_opt' + i"
                  required
                />
                <label class="form-check-label" :for="'q' + question.id + '_opt' + i">
                  {{ question[optionKey] }}
                </label>
              </div>
            </div>
            <div v-if="errorMessage" class="alert alert-danger">{{ errorMessage }}</div>
            <button type="submit" class="btn btn-success">Submit Quiz</button>
          </form>
        </div>
      </div>
    </div>

    <!-- Loading fallback -->
    <div v-else class="container mt-5 text-center">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      quiz: null,
      answers: {},
      errorMessage: '',
      started: false,
    };
  },
  methods: {
    logout() {
      localStorage.removeItem('studentToken');
      this.$router.push('/login');
    },
    async fetchQuiz() {
      const quizId = this.$route.params.id;
      try {
        const response = await fetch(`/api/quiz/${quizId}`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('studentToken')}`,
          },
        });
        const result = await response.json();
        if (!response.ok) {
          this.errorMessage = result.message || 'Failed to load quiz';
        } else {
          this.quiz = result;
          this.errorMessage = '';
        }
      } catch (error) {
        console.error('Error fetching quiz:', error);
        this.errorMessage = 'An error occurred while fetching the quiz.';
      }
    },
    startQuiz() {
      if (!this.quiz || !this.quiz.questions || this.quiz.questions.length === 0) {
        this.errorMessage = 'This quiz has no questions.';
        return;
      }
      this.errorMessage = '';
      this.started = true;
    },
    async submitQuiz() {
      try {
        const payload = {
          quiz_id: this.quiz.id,
          answers: Object.entries(this.answers).map(([question_id, selected_option]) => ({
            question_id: parseInt(question_id),
            selected_option,
          })),
        };
        const response = await fetch(`/api/quiz/${this.quiz.id}/submit/post`, {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${localStorage.getItem('studentToken')}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(payload),
        });
        const result = await response.json();
        if (!response.ok) {
          this.errorMessage = result.message || 'Failed to submit quiz';
        } else {
          alert('Quiz submitted successfully!');
          this.$router.push('/student');
        }
      } catch (error) {
        console.error('Error submitting quiz:', error);
        this.errorMessage = 'Submission failed. Please try again.';
      }
    },
  },
  mounted() {
    this.fetchQuiz();
  },
};
</script>