<!-- Student Dashboard -->
<template>
  <div>
    <nav class="navbar bg-primary" data-bs-theme="dark">
      <div class="container">
        <a class="navbar-brand" href="#">Student Dashboard</a>
        <button @click="exportQuizHistory" class="btn btn-primary mb-3">
          Export Quiz History (CSV)
        </button>
        <button class="btn btn-outline-light ms-auto" @click="logout">Logout</button>
      </div>
    </nav>

    <div class="container mt-5">
      <div class="row justify-content-center">
        <div class="col-md-12">
          <div class="card">
            <div class="card-header">All Quizzes</div>
            <div class="card-body">
              <table class="table">
                <thead>
                  <tr>
                    <th scope="col">Title</th>
                    <th scope="col">Subject</th>
                    <th scope="col">Chapter</th>
                    <th scope="col">Scores</th>
                    <th scope="col">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="quiz in allQuizzes" :key="quiz.id">
                    <td>{{ quiz.title }}</td>
                    <td>{{ quiz.subject_name }}</td>
                    <td>{{ quiz.chapter_name }}</td>
                    <td>
                      <span v-if="quiz.submitted && quiz.scores !== undefined && quiz.scores !== null">
                        {{ quiz.scores }}
                      </span>
                      </td>
                      <td><span v-if="quiz.submitted && quiz.scores !== undefined && quiz.scores !== null">
                        {{ quiz.scores }}
                      </span>
                      <span v-else>
                        <router-link :to="'/attempt-quiz/' + quiz.id"
                          class="btn btn-primary btn-sm me-2">Attempt</router-link>
                        <small class="text-muted ms-2">No attempts yet</small>
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
              <div v-if="allQuizzes.length === 0" class="text-center text-muted">
                No quizzes available.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      allQuizzes: [],
    };
  },
  methods: {
    logout() {
      localStorage.removeItem('studentToken');
      this.$router.push('/');
    },
    exportQuizHistory() {
      const token = localStorage.getItem('studentToken');
      if (!token) {
        this.logout();
        return;
      }

      fetch('/api/quiz/export', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      })
        .then(response => {
          if (!response.ok) {
            throw new Error('Failed to export quiz history.');
          }
          return response.blob();
        })
        .then(blob => {
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = 'quiz_history.csv';
          document.body.appendChild(a);
          a.click();
          a.remove();
        })
        .catch(error => {
          console.error('Export error:', error);
          alert('Failed to export quiz history. Please try again later.');
        });

      // Calling celery task to send email
      fetch('/api/quiz/export/email', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      })
        .then(response => response.json())
        .then(data => {
          console.log(data);
        })
        .catch(error => {
          console.error('Email error:', error);
        });
    },
    fetchQuizzes() {
      const token = localStorage.getItem('studentToken');
      if (!token) {
        this.logout();
        return;
      }

      fetch('/api/quiz', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      })
        .then(response => {
          if (!response.ok) {
            throw new Error('Failed to fetch quizzes.');
          }
          return response.json();
        })
        .then(data => {
          this.allQuizzes = data.quizzes;
        })
        .catch(error => {
          console.error('Fetch error:', error);
          alert('Session expired or unauthorized. Redirecting to login.');
          this.logout();
        });
    },
  },
  mounted() {
    this.fetchQuizzes();
  },
};
</script>

