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
                    <div class="card-header">Edit Chapter</div>
                    <div class="card-body">
                        <form @submit.prevent="updateChapter">
                            <div class="form-group mb-3">
                                <label for="name">Chapter Name</label>
                                <input type="text" class="form-control" v-model="chapter.name" />
                            </div>
                            <div class="form-group mb-3">
                                <label for="description">Description</label>
                                <input type="text" class="form-control" v-model="chapter.description" />
                            </div>
                            <div class="form-group mb-3">
                                <label for="subject">Subject</label>
                                <select v-model="chapter.subject_id" class="form-control">
                                    <option disabled value="">-- Select a Subject --</option>
                                    <option v-for="subject in subjects" :key="subject.id" :value="subject.id">
                                        {{ subject.name }}
                                    </option>
                                </select>
                            </div>

                            <div v-if="errorMessage" class="alert alert-danger">{{ errorMessage }}</div>
                            <button type="submit" class="btn btn-primary">Update Chapter</button>
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
            chapter: {},
            subjects: [],
            errorMessage: ''
        };
    },
    methods: {
        logout() {
            this.$router.push('/login');
        },
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

        async updateChapter() {
            const chapterId = this.$route.params.id;
            const payload = {
                name: this.chapter.name,
                description: this.chapter.description,
                subject_id: this.chapter.subject_id,
            };
            try {
                const response = await fetch(`/api/chapter/${chapterId}`, {
                    method: 'PUT',
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('adminToken')}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(payload)
                });

                const result = await response.json();
                if (!response.ok) {
                    this.errorMessage = result.message || 'Failed to update chapter.';
                } else {
                    alert('Chapter updated successfully!');
                    this.$router.push('/chapter');
                }
            } catch (error) {
                this.errorMessage = 'An error occurred while updating the chapter.';

            }
        },
        async create() {
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
    },
    mounted() {
        this.fetchSubjects();
        this.fetchChapters();
    },
};
</script>