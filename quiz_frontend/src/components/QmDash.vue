// QmDash.vue
<template>
    <nav class="navbar bg-primary" data-bs-theme="dark">
        <div class="container-fluid d-flex justify-content-between align-items-center">
            <a class="navbar-brand" href="#">Dashboard Mastereo</a>
            <button class="navbar-toggler ms-auto" type="button" data-bs-toggle="collapse"
                data-bs-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false"
                aria-label="Toggle navigation">
                <span class="navbar-toggler-icon"></span>
            </button>
        </div>

        <div class="collapse navbar-collapse" id="navbarSupportedContent">
            <ul class="navbar-nav me-auto mb-2 mb-lg-0">
                <li class="nav-item">
                    <router-link to="/manager" class="nav-link active" aria-current="page">Home</router-link>
                </li>
                <li class="nav-item">
                    <router-link to="/subject" class="nav-link">Subject</router-link>
                </li>
                <li class="nav-item">
                    <router-link to="/chapter" class="nav-link">Chapter</router-link>
                </li>
                <li class="nav-item">
                    <router-link to="/question" class="nav-link">Question</router-link>
                </li>
                <li class="nav-item">
                    <router-link to="/create-quiz" class="nav-link">Create Quiz</router-link>
                </li>
                <li class="nav-item">
                    <a class="nav-link" aria-current="page" @click="exportData">Export CSV</a>
                </li>
            </ul>
            <button class="btn btn-outline-light me-2" @click="logout">Logout</button>
        </div>
    </nav>
    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-header">All Students</div>
                    <div class="card-body">
                        <table class="table">
                            <thead>
                                <tr>
                                    <th scope="col">Full Name</th>
                                    <th scope="col">User Name</th>
                                    <th scope="col">Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="student in allStudents" :key="student.id">
                                    <td>{{ student.full_name }}</td>
                                    <td>{{ student.username }}</td>

                                    <td>
                                        <button v-if="student.status === 'pending'" class="btn btn-success"
                                            @click="approveStudent(student.id)">
                                            Approve
                                        </button>
                                        <span v-else>{{ student.status }}</span>
                                    </td>

                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-header">All Quizes</div>
                    <div class="card-body">
                        <table class="table">
                            <thead>
                                <tr>
                                    <th scope="col">Title</th>
                                    <th scope="col">Subject</th>
                                    <th scope="col">Chapter</th>
                                    <th scope="col">Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="quiz in allQuizzes" :key="quiz.id">
                                    <td>{{ quiz.title }}</td>
                                    <td>{{ quiz.subject_name }}</td>
                                    <td>{{ quiz.chapter_name }}</td>
                                    <td>
                                        <router-link :to="'/edit-quiz/' + quiz.id"
                                            class="btn btn-primary btn-sm me-2">Edit</router-link>
                                        <button class="btn btn-danger btn-sm"
                                            @click="deleteQuiz(quiz.id)">Delete</button>
                                    </td>

                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <div class="container mt-5" v-if="quizFeedbacks.length > 0">
  <div class="row justify-content-center">
    <div class="col-md-12">
      <div class="card">
        <div class="card-header">Student Feedback on Quizzes</div>
        <div class="card-body">
          <table class="table">
            <thead>
              <tr>
                <th>Student Name</th>
                <th>Quiz Title</th>
                <th>Remarks</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="feedback in quizFeedbacks" :key="feedback.attempt_id">
                <td>{{ feedback.student_name }}</td>
                <td>{{ feedback.quiz_title }}</td>
                <td>{{ feedback.remarks }}</td>
              </tr>
            </tbody>
          </table>
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
            allStudents: [],
            allQuizzes: [],
            quizFeedbacks: [] 
        };
    },
    methods: {
        async logout() {
            localStorage.removeItem('adminToken');
            this.$router.push('/');
        },
        async approveStudent(id) {
            try {
                const response = await fetch(`/api/approve/${id}`, {
                    method: 'PATCH',
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('adminToken')}`,
                        'Content-Type': 'application/json',
                    },
                });
                if (response.ok) {
                    const result = await response.json();
                    alert(result.message);
                    this.fetchStudents();
                } else {
                    alert("Error approving student");
                }
            } catch (error) {
                alert('Error approving student');
            }
        },
        async deleteQuiz(id) {
            try {
                const response = await fetch(`/api/quiz/${id}`, {
                    method: 'DELETE',
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('adminToken')}`,
                        'Content-Type': 'application/json',
                    },
                });
                if (response.ok) {
                    const result = await response.json();
                    alert(result.message);
                    this.fetchQuizzes();
                    this.$router.push('/quizmaster');
                } else {
                    alert("Error deleting quiz");
                }
            } catch (error) {
                alert('Error deleting quiz');
            }
        },
        fetchQuizzes: function () {
            const response = fetch('/api/quiz', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('adminToken')}`,
                    'Content-Type': 'application/json',
                },
            })
                .then(response => response.json())
                .then(data => {
                    this.allQuizzes = data.quizzes;
                })
                .catch(error => {
                    console.log(error);
                });
        },
        fetchStudents: function () {
            const response = fetch('/api/students', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('adminToken')}`,
                    'Content-Type': 'application/json',
                },
            })
                .then(response => response.json())
                .then(data => {
                    this.allStudents = data.students;
                })
                .catch(error => {
                    console.log(error);
                });
        },
        async fetchFeedbacks() {
    try {
      const response = await fetch('/api/quiz/0/feedback/view', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('adminToken')}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const result = await response.json();
        this.quizFeedbacks = result.feedbacks;
      } else {
        console.error('Error fetching feedback');
      }
    } catch (error) {
      console.error('Error fetching feedback:', error);
    }
  },
  async exportData() {
            try {
                const response = await fetch('/api/export', {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('adminToken')}`,
                        'Content-Type': 'application/json',
                    },
                });
                if (response.ok) {
                    const blob = await response.blob();
                    const url = URL.createObjectURL(blob);
                    const link = document.createElement('a');
                    link.href = url;
                    link.download = 'quiz_data.json';
                    link.click();
                    URL.revokeObjectURL(url);
                } else {
                    alert('Error exporting data');
                }
            } catch (error) {
                alert('Error exporting data');
            }
        },
    },
    mounted() {
        this.fetchQuizzes();
        this.fetchStudents();
        this.fetchFeedbacks();
    }
};

</script>