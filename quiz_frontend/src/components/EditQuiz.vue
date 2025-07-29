<template>
    <nav class="navbar bg-primary" data-bs-theme="dark">
        <div class="container">
            <a class="navbar-brand" href="#">Admin Dashboard</a>
            <button class="btn btn-outline-light ms-auto" @click="logout">Logout</button>
        </div>
    </nav>

    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-md-8">
                <div class="card">
                    <div class="card-header">Edit Quiz</div>
                    <div class="card-body">
                        <form @submit.prevent="updateQuiz">
                            <div class="form-group mb-3">
                                <label for="title">Quiz Title</label>
                                <input type="text" class="form-control" v-model="quiz.title" />
                            </div>
                            <div class="form-group mb-3">
                                <label for="date">Date of Quiz</label>
                                <input type="date" class="form-control" v-model="quiz.date_of_quiz" />
                            </div>
                            <div class="form-group mb-3">
                                <label for="start_time">Quiz Start Time</label>
                                <input type="time" class="form-control" v-model="quiz.start_time" />
                            </div>
                            <div class="form-group mb-3">
                                <label for="time_duration">Duration (minutes)</label>
                                <input type="number" class="form-control" v-model.number="quiz.time_duration" />
                            </div>
                            <div v-if="errorMessage" class="alert alert-danger">{{ errorMessage }}</div>
                            <button type="submit" class="btn btn-primary">Edit Quiz</button>
                        </form>
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
            quiz: {
                title: '',
                date_of_quiz: '',
                start_time: '',
                time_duration: ''
            }
        };
    },
    methods: {
        logout() {
            this.$router.push('/login');
        },
        async updateQuiz() {
            const Quiz_id = this.$route.params.id;
            const payload = {
                title: this.quiz.title,
                date_of_quiz: this.quiz.date_of_quiz,
                start_time: this.quiz.start_time,
                time_duration: this.quiz.time_duration
            };
            try {
                const response = await fetch(`/api/quiz/${Quiz_id}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
                    },
                    body: JSON.stringify(payload)
                });

                const responseBody = await response.text();
                if (responseBody.trim() !== '') {
                    const result = JSON.parse(responseBody);
                    if (!response.ok) {
                        this.errorMessage = result.message || "Failed to update quiz";
                    } else {
                        alert("Quiz updated successfully");
                        this.$router.push('/quizmaster');
                    }
                } else {
                    console.log('Empty response body');
                }
            } catch (error) {
                console.log(error);
            }
        },
    }
}
</script>