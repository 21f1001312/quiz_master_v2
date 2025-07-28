<!-- Student Dashboard -->
<template>
  <div>
    <nav class="navbar bg-primary" data-bs-theme="dark">
      <div class="container">
        <a class="navbar-brand" href="#">Student Dashboard</a>
        <button @click="exportQuizHistory" class="btn btn-primary mb-3">
          Export Quiz History (CSV)
        </button>
        <div class="position-relative" style="width: 300px;">
                <input v-model="globalSearch" class="form-control me-2" type="search"
                    placeholder="Search subject" @input="fetchSearchResults" />
            </div>
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
      globalSearch: '',
      searchResults: [],
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

      fetch('/api/quiz/export/email', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      })
        .then(response => {
          if (response.status === 202 || response.status === 200) {
            return response.json();
          } else {
            throw new Error('Unexpected response');
          }
        })
        .then(data => {
          alert(data.message || "Export started. You'll receive it via email shortly.");
        })
        .catch(error => {
          console.error('Email error:', error);
          alert("Failed to export quiz history. Please try again later.");
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
    async fetchSearchResults() {
            if (!this.globalSearch.trim()) {
                this.searchResults = [];
                return;
            }

            const token = localStorage.getItem("studentToken");
            const response = await fetch(`/api/students/search?q=${this.globalSearch}`, {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });

            if (response.ok) {
                const data = await response.json();
                this.searchResults = data.results;
                console.log("Search Results:", data.results);
            }
        },
  },
  mounted() {
    this.fetchQuizzes();
    this.fetchSearchResults();
  },
};
</script>
