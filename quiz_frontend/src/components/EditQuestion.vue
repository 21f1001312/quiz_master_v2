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
                    <div class="card-header">Edit Question</div>
                    <div class="card-body">
                        <form @submit.prevent="updateQuestion">
                            <div class="form-group mb-3">
                                <label for="question">Question</label>
                                <input type="text" class="form-control" v-model="question.question" />
                            </div>
                            <div class="form-group mb-3">
                                <label for="option1">Option 1</label>
                                <input type="text" class="form-control" v-model="question.option1" />
                            </div>
                            <div class="form-group mb-3">
                                <label for="option2">Option 2</label>
                                <input type="text" class="form-control" v-model="question.option2" />
                            </div>
                            <div class="form-group mb-3">
                                <label for="option3">Option 3</label>
                                <input type="text" class="form-control" v-model="question.option3" />
                            </div>
                            <div class="form-group mb-3">
                                <label for="option4">Option 4</label>
                                <input type="text" class="form-control" v-model="question.option4" />
                            </div>
                            <div class="form-group mb-3">
                                <label for="correctOption">Correct Option</label>
                                <input type="text" class="form-control" v-model="question.correct_option" />
                            </div>
                            <div class="form-group mb-3">
                                <label for="chapterId">Chapter ID</label>
                                <input type="text" class="form-control" v-model="question.chapter_id" />
                            </div>
                            <div v-if="errorMessage" class="alert alert-danger">{{ errorMessage }}</div>
                            <button type="submit" class="btn btn-primary">Update Question</button>
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
            question: {
                question: '',
                option1: '',
                option2: '',
                option3: '',
                option4: '',
                correct_option: '',
                chapter_id: ''
            },
            errorMessage: ''
        };
    },
    methods: {
        logout() {
            this.$router.push('/login');
        },
        async updateQuestion() {
            const questionId = this.$route.params.id;
            const payload = {
                question: this.question.question,
                option1: this.question.option1,
                option2: this.question.option2,
                option3: this.question.option3,
                option4: this.question.option4,
                correct_option: this.question.correct_option,
                chapter_id: this.question.chapter_id
            };
            try { 
                const response = await fetch(`/api/question/${questionId}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
                    },
                    body: JSON.stringify(payload)
                });

                const result = await response.json();
                if (!response.ok) {
                    this.errorMessage = result.message || "Failed to update question";
                } else {
                    alert("Question updated successfully");
                    this.$router.push('/question');
                }
            } catch (error) {
                console.error('Error updating question:', error);
                this.errorMessage = 'An error occurred while updating the question.';
            }

        },

        async created() {
            const questionId = this.$route.params.id;
            if (questionId) {
                fetch(`/api/question/${questionId}`, {
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
                    }
                })
            }
        }
    }
};
</script>