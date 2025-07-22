<!-- CreateQuiz.vue -->
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
                    <div class="card-header">Create Quiz</div>
                    <div class="card-body">
                        <form @submit.prevent="createQuiz">
                            <div class="form-group mb-3">
                                <label for="title">Quiz Title</label>
                                <input type="text" class="form-control" v-model="title" required />
                            </div>

                            <div class="form-group mb-3">
                                <label for="date">Date of Quiz</label>
                                <input type="date" class="form-control" v-model="date_of_quiz" required />
                            </div>

                            <div class="form-group mb-3">
                                <label for="startTime">Quiz Start Time</label>
                                <input type="time" class="form-control" v-model="start_time" required />

                            </div>


                            <div class="form-group mb-3">
                                <label for="duration">Duration (minutes)</label>
                                <input type="number" class="form-control" v-model="time_duration" required />
                            </div>
                            <div class="form-group mb-3">
                                <label for="subject">Select Subject</label>
                                <select v-model="subject_name" class="form-control" required>
                                    <option disabled value="">-- Select a Subject --</option>
                                    <option v-for="subject in subjects" :key="subject.id" :value="subject.name">
                                        {{ subject.name }}
                                    </option>
                                </select>
                            </div>

                            <div class="form-group mb-3">
                                <label for="chapter">Select Chapter</label>
                                <select v-model="chapter_id" class="form-control" required>
                                    <option disabled value="">-- Select a Chapter --</option>
                                    <option v-for="chapter in chapters" :key="chapter.id" :value="chapter.id">
                                        {{ chapter.name }}
                                    </option>
                                </select>
                            </div>

                            <div v-if="errorMessage" class="alert alert-danger">{{ errorMessage }}</div>
                            <button type="submit" class="btn btn-primary w-100">Create Quiz</button>
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
            title: '',
            date_of_quiz: '',
            start_time: '',
            time_duration: '',
            chapter_id: '',
            subject_name: '',
            chapter_name: '',
            errorMessage: '',
            subjects: [],
            chapters: [],
        };
    },
    methods: {

        async fetchSubjects() {
            try {
                const response = await fetch('/api/subjects', {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('adminToken')}`,
                        'Content-Type': 'application/json',
                    },
                });
                if (!response.ok) {
                    throw new Error('Failed to fetch subjects');
                }
                const data = await response.json();
                this.subjects = data.subjects;
            } catch (error) {
                console.error('Error fetching subjects:', error);
                alert('Error fetching subjects');
            }
        },

        async fetchChapters() {
            try {
                const response = await fetch('/api/chapter', {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('adminToken')}`,
                        'Content-Type': 'application/json',
                    },
                });
                if (!response.ok) {
                    throw new Error('Failed to fetch chapters');
                }
                const data = await response.json();
                this.chapters = data.chapters;
            } catch (error) {
                console.error('Error fetching chapters:', error);
                alert('Error fetching chapters');
            }
        },
        async createQuiz() {
            const payload = {
                title: this.title,
                date_of_quiz: this.date_of_quiz,      
                start_time: this.start_time,          
                time_duration: parseInt(this.time_duration),  
                chapter_id: this.chapter_id,
                subject_name: this.subject_name,
                chapter_name: this.chapter_name,
                status: "scheduled"
            };

            try {
                const response = await fetch('/api/quiz', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        Authorization: `Bearer ${localStorage.getItem('adminToken')}`,
                    },
                    body: JSON.stringify(payload),
                });

                const result = await response.json();

                if (!response.ok) {
                    this.errorMessage = result.message || 'Failed to create quiz';
                } else {
                    alert('Quiz created successfully');
                    this.$router.push('/quizmaster');
                }
            } catch (error) {
                console.log(error);
                this.errorMessage = "An unexpected error occurred.";
            }
        }
        ,
        logout() {
            this.$router.push('/login');
        },
    },
    mounted() {
        this.fetchSubjects();
        this.fetchChapters();
    },
};
</script>
