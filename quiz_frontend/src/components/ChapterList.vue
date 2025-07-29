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
                    <div class="card-header">All Chapterss</div>
                    <div class="card-body">
                        <form @submit.prevent="addChapter" class="mb-4">
                            <div class="mb-3">
                                <label for="chapterName" class="form-label">Chapter Name</label>
                                <input type="text" class="form-control" id="chapterName" v-model="newChapter.name"
                                    required />
                            </div>
                            <div class="mb-3">
                                <label for="subjectId" class="form-label">Select Subject</label>
                                <select class="form-control" id="subjectId" v-model="newChapter.subject_id" required>
                                    <option disabled value="">-- Select Subject --</option>
                                    <option v-for="subject in subjects" :key="subject.id" :value="subject.id">
                                        {{ subject.name }}
                                    </option>
                                </select>
                            </div>
                            <div class="mb-3">
                                <label for="chapterDescription" class="form-label">Description</label>
                                <input type="text" class="form-control" id="chapterDescription"
                                    v-model="newChapter.description" required />
                            </div>

                            <button type="submit" class="btn btn-primary">Add Chapter</button>
                        </form>

                        <table class="table">
                            <thead>
                                <tr>
                                    <th scope="col">Chapter Name</th>
                                    <th scope="col">Subject Name</th>
                                    <th scope="col">Description</th>
                                    <th scope="col">Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="chapter in chapters" :key="chapter.id">
                                    <td>{{ chapter.name }}</td>
                                    <td>{{ chapter.subject_name }}</td>
                                    <td>{{ chapter.description }}</td>
                                    <td>
                                        <router-link :to="'/edit-chapter/' + chapter.id"
                                            class="btn btn-primary">Edit</router-link>
                                        <button class="btn btn-danger"
                                            @click="deleteChapter(chapter.id)">Delete</button>
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
            newChapter: {
                name: '',
                subject_id: '',
                subject_name: '',
                description: ''
            },
            chapters: [],
            subjects: [],
        }
    },
    methods: {
        async logout() {
            localStorage.removeItem('adminToken');
            this.$router.push('/');
        },
        fetchChapters: function () {
            const response = fetch('/api/chapter', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('adminToken')}`,
                    'Content-Type': 'application/json',
                },
            })
                .then(response => response.json())
                .then(data => {
                    this.chapters = data.chapters;
                })
                .catch(error => {
                    console.log(error);
                });
        },

        async fetchSubjects() {
            try {
                const response = await fetch('/api/subjects', {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('adminToken')}`,
                        'Content-Type': 'application/json'
                    }
                });
                const result = await response.json();
                this.subjects = result.subjects || []; 
            } catch (error) {
                console.error('Error fetching subjects', error);
            }
        },

        async addChapter() {
            const payload = {
                name: this.newChapter.name,
                subject_id: this.newChapter.subject_id, 
                subject_name: this.newChapter.subject_name,
                description: this.newChapter.description
            };
            try {
                const response = await fetch('/api/chapter', {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('adminToken')}`,
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(payload)
                })
                const result = await response.json();
                if (!response.ok) {
                    this.errorMessage = result.message || 'Failed to create chapter';
                } else {
                    alert('Chapter created successfully');
                    this.$router.push('/chapter');
                }
            }
            catch (error) {
                console.log(error);
            }
        },

        async deleteChapter(id) {
            const token = localStorage.getItem('adminToken')
            try {
                const response = await fetch(`/api/chapter/${id}`, {
                    method: 'DELETE',
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('adminToken')}`,
                        'Content-Type': 'application/json',
                    },
                });
                if (response.ok) {
                    const result = await response.json();
                    alert(result.message);
                    this.fetchChapters();
                    this.$router.push('/chapter');
                } else {
                    alert("Error deleting chapter");
                }
            } catch (error) {
                alert('Error deleting chapter');
            }
        },


    },

    mounted() {
        this.fetchChapters();
        this.fetchSubjects();
    }
};

</script>