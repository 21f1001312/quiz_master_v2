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
                    <div class="card-header">All Subjects</div>
                    <div class="card-body">
                        <form @submit.prevent="addSubject" class="mb-4">
                            <div class="mb-3">
                                <label for="subjectName" class="form-label">Subject Name</label>
                                <input type="text" class="form-control" id="subjectName" v-model="newSubject.name"
                                    required />
                            </div>

                            <div class="mb-3">
                                <label for="subjectDescription" class="form-label">Description</label>
                                <input type="text" class="form-control" id="subjectDescription"
                                    v-model="newSubject.description" required />
                            </div>

                            <div class="mb-3">
                                <label for="subjectLevel" class="form-label">Level</label>
                                <input type="text" class="form-control" id="subjectLevel" v-model="newSubject.level"
                                    required />
                            </div>

                            <button type="submit" class="btn btn-primary">Add Subject</button>
                        </form>

                        <table class="table">
                            <thead>
                                <tr>
                                    <th scope="col">Subject Name</th>
                                    <th scope="col">Subject Description</th>
                                    <th scope="col">Level</th>
                                    <th scope="col">Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="subject in subjects" :key="subject.id">
                                    <td>{{ subject.name }}</td>
                                    <td>{{ subject.description }}</td>
                                    <td>{{ subject.level }}</td>
                                    <td>
                                        <router-link :to="'/edit-subject/' + subject.id"
                                            class="btn btn-primary">Edit</router-link>
                                        <button class="btn btn-danger"
                                            @click="deleteSubject(subject.id)">Delete</button>
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
            newSubject: {
                name: '',
                description: '',
                level: ''
            },
            subjects: []
        }
    },
methods: {
    async logout() {
      localStorage.removeItem('adminToken');
      this.$router.push('/');
    },
    fetchSubjects: function () {
        const response = fetch('/api/subjects', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('adminToken')}`,
                'Content-Type': 'application/json',
            },
        })
            .then(response => response.json())
            .then(data => {
                this.subjects = data.subjects;
            })
            .catch(error => {
                console.log(error);
            });
    },

    async addSubject() {
        const payload = {
            name: this.newSubject.name,
            description: this.newSubject.description,
            level: this.newSubject.level
        };
        try {
            const response = await fetch('/api/subjects', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('adminToken')}`,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload)
            })
            const result = await response.json();
            if (!response.ok) {
                this.errorMessage = result.message || 'Failed to create subject';
            } else {
                alert('Subject created successfully');
                this.$router.push('/quizmaster');
            }
        }
        catch (error) {
            console.log(error);
        }
    },

    async deleteSubject(id) {
        const token = localStorage.getItem('adminToken')
        try {
            const response = await fetch(`/api/subjects/${id}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('adminToken')}`,
                    'Content-Type': 'application/json',
                },
            });
            if (response.ok) {
                const result = await response.json();
                alert(result.message);
                this.fetchSubjects();
                this.$router.push('/quizmaster');
            } else {
                alert("Error deleting subject");
            }
        } catch (error) {
            alert('Error deleting subject');
        }
    },

    
},

mounted() {
    this.fetchSubjects()
}
};

</script>