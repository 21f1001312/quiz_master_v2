<template>
    <nav class="navbar bg-primary" data-bs-theme="dark">
        <div class="container">
            <a class="navbar-brand" href="#">Dashboard Mastereo</a>
            <button class="btn btn-outline-light ms-auto" @click="logout">Logout</button>
        </div>
    </nav>

    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-header">All Questions</div>
                    <div class="card-body">
                        <form @submit.prevent="submitQuestions" class="mb-4">
                            <div v-for="(question, index) in questionsToSubmit" :key="index"
                                class="mb-4 border p-3 rounded">
                                <label class="form-label">Question Text</label>
                                <input type="text" class="form-control mb-2" v-model="question.question_statement"
                                    required>

                                <label class="form-label">Option 1</label>
                                <input type="text" class="form-control mb-2" v-model="question.option1" required>

                                <label class="form-label">Option 2</label>
                                <input type="text" class="form-control mb-2" v-model="question.option2" required>

                                <label class="form-label">Option 3</label>
                                <input type="text" class="form-control mb-2" v-model="question.option3" required>

                                <label class="form-label">Option 4</label>
                                <input type="text" class="form-control mb-2" v-model="question.option4" required>

                                <label class="form-label">Correct Option</label>
                                <input type="text" class="form-control mb-2" v-model="question.correct_option" required>

                                <label class="form-label">Chapter ID</label>
                                <input type="text" class="form-control mb-2" v-model="question.chapter_id" required>

                            </div>

                            <label class="form-label">Quiz ID</label>
                            <input type="text" class="form-control mb-4" v-model="quiz_id" required>

                            <button type="button" class="btn btn-secondary me-2" @click="addNewQuestion">Add Another
                                Question</button>
                            <button type="submit" class="btn btn-primary">Submit All Questions</button>
                        </form>
                        <table class="table">
                            <thead>
                                <tr>
                                    <th>Question Text</th>
                                    <th>Options</th>
                                    <th>Correct Option</th>
                                    <th>Quiz ID</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="question in questions" :key="question.id">
                                    <td>{{ question.question_statement }}</td>
                                    <td>
                                        1. {{ question.option1 }}<br>
                                        2. {{ question.option2 }}<br>
                                        3. {{ question.option3 }}<br>
                                        4. {{ question.option4 }}
                                    </td>

                                    <td>{{ question.correct_option }}</td>
                                    <td>{{ question.quiz_id }}</td>
                                    <td>
                                        <router-link :to="'/edit-question/' + question.id"
                                            class="btn btn-primary">Edit</router-link>
                                        <button class="btn btn-danger"
                                            @click="deleteQuestion(question.id)">Delete</button>
                                    </td>
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
            quiz_id: '',
            questionsToSubmit: [
                {
                    question_statement: '',
                    option1: '',
                    option2: '',
                    option3: '',
                    option4: '',
                    correct_option: '',
                    chapter_id: ''
                }
            ],
            questions: []
        };
    },

    methods: {
        async logout() {
            localStorage.removeItem('adminToken');
            this.$router.push('/');
        },
        async fetchQuestions() {
            try {
                const response = await fetch('/api/question', {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('adminToken')}`,
                        'Content-Type': 'application/json',
                    },
                });
                if (!response.ok) {
                    throw new Error('Failed to fetch questions');
                }
                const data = await response.json();
                this.questions = data.questions;
            } catch (error) {

                console.error('Error fetching questions:', error);
                alert('Error fetching questions');
            }
        },
        addNewQuestion() {
            this.questionsToSubmit.push({
                question_statement: '',
                option1: '',
                option2: '',
                option3: '',
                option4: '',
                correct_option: '',
                chapter_id: ''
            });
        },
        removeQuestion(index) {
            this.questionsToSubmit.splice(index, 1);
        },
        async submitQuestions() {
            const payload = {
                quiz_id: this.quiz_id,
                questions: this.questionsToSubmit.map((q) => ({
                    ...q,
                    quiz_id: this.quiz_id
                }))
            };

            try {
                const response = await fetch('/api/question', {
                    method: 'POST',
                    headers: {
                        Authorization: `Bearer ${localStorage.getItem('adminToken')}`,
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(payload),
                });

                const result = await response.json();

                if (!response.ok) {
                    alert(result.message || 'Failed to create questions');
                } else {
                    alert('Questions submitted successfully');
                    this.questionsToSubmit = [
                        {
                            question_statement: '',
                            option1: '',
                            option2: '',
                            option3: '',
                            option4: '',
                            correct_option: '',
                            chapter_id: ''
                        }
                    ];
                    this.quiz_id = '';
                    this.fetchQuestions();
                }
            } catch (error) {
                console.error('Submit failed:', error);
                alert('Error submitting questions');
            }
        },

        async deleteQuestion(id) {
            try {
                const response = await fetch(`/api/question/${id}`, {
                    method: 'DELETE',
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('adminToken')}`,
                        'Content-Type': 'application/json',
                    },
                });
                if (response.ok) {
                    const result = await response.json();
                    alert(result.message);
                    this.fetchQuestions();
                    this.$router.push('/question');
                } else {
                    alert("Error deleting question");
                }
            } catch (error) {
                alert('Error deleting question');
            }
        }
    },
    mounted() {
        this.fetchQuestions();
    },
};
</script>
