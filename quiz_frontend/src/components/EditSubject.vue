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
                    <div class="card-header">Edit Subject</div>
                    <div class="card-body">
                        <form @submit.prevent="updateSubject">
                            <div class="form-group mb-3">
                                <label for="name">Subject Name</label>
                                <input type="text" class="form-control" v-model="subject.name"/>
                            </div>
                            <div class="form-group mb-3">
                                <label for="description">Description</label>
                                <input type="text" class="form-control" v-model="subject.description"/>
                            </div>
                            <div class="form-group mb-3">
                                <label for="level">Level</label>
                                <input type="text" class="form-control" v-model="subject.level"/>
                            </div>
                            <div v-if="errorMessage" class="alert alert-danger">{{ errorMessage }}</div>
                            <button type="submit" class="btn btn-primary">Update Subject</button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>

</template>

<script>
export default{
    data() {
        return {
            subject: {
                name: '',
                description: '',
                level: ''
            },
            errorMessage: ''
        };
    },
    methods: {
        logout() {
            this.$router.push('/login');
        },

        async updateSubject() {
            const subject_id = this.$route.params.id;
            const payload = {
                name: this.subject.name,
                description: this.subject.description,
                level: this.subject.level
            };
            try {
                const response = await fetch(`/api/subjects/${subject_id}`, {
                    method: 'PUT',
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('adminToken')}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(payload)
                });

                const result = await response.json();
                if (!response.ok) {
                    this.errorMessage = result.message || 'Failed to update subject';
                } else {
                    alert('Subject updated successfully');
                    this.$router.push('/subject');
                }
            } catch (error) {
                this.errorMessage = 'An error occurred while updating the subject';
            }
        },
        async create() {
            try {
                const response = await fetch('/api/subjects', {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('adminToken')}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(this.subject)
                });

                const result = await response.json();
                if (!response.ok) {
                    this.errorMessage = result.message || 'Failed to create subject';
                } else {
                    alert('Subject created successfully');
                    this.$router.push('/subject');
                }
            } catch (error) {
                this.errorMessage = 'An error occurred while creating the subject';
            }
        },
    }
};
</script>