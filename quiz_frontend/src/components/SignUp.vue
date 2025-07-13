<template>
  <div class="container mt-5">
    <div class="row justify-content-center">
      <div class="col-md-6">
        <div class="card shadow">
          <div class="card-header bg-primary text-white">
            <h4 class="mb-0">Sign Up</h4>
          </div>
          <div class="card-body">
            <form @submit.prevent="signUpUser">
              <div class="form-group mb-3">
                <label>Email (Username)</label>
                <input v-model="username" type="email" class="form-control" required />
              </div>

              <div class="form-group mb-3">
                <label>Password</label>
                <input v-model="password" type="password" class="form-control" required minlength="4" maxlength="20" />
              </div>

              <div class="form-group mb-3">
                <label>Full Name</label>
                <input v-model="full_name" type="text" class="form-control" required minlength="3" maxlength="100" />
              </div>

              <div class="form-group mb-3">
                <label>Qualification</label>
                <input v-model="qualification" type="text" class="form-control" required />
              </div>

              <div class="form-group mb-4">
                <label>Date of Birth</label>
                <input v-model="date_of_birth" type="date" class="form-control" required />
              </div>

              <div v-if="message" class="alert alert-success mt-2">{{ message }}</div>
              <div v-if="errorMessage" class="alert alert-danger mt-2">{{ errorMessage }}</div>

              <button type="submit" class="btn btn-success w-100">Sign Up</button>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Signup',
  data() {
    return {
      username: '',
      password: '',
      full_name: '',
      qualification: '',
      date_of_birth: '',
      message: '',
      errorMessage: ''
    };
  },
  methods: {
    async signUpUser() {
      this.message = '';
      this.errorMessage = '';

      const payload = {
        username: this.username,
        password: this.password,
        full_name: this.full_name,
        qualification: this.qualification,
        date_of_birth: this.date_of_birth
      };

      try {
        const res = await fetch('/api/signup', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(payload)
        });

        const data = await res.json();

        if (!res.ok) {
          this.errorMessage = data.message || 'Signup failed.';
          return;
        }

        this.message = data.message;
        this.username = '';
        this.password = '';
        this.full_name = '';
        this.qualification = '';
        this.date_of_birth = '';
      } catch (err) {
        this.errorMessage = 'Signup failed. Server error.';
      }
    }
  }
};
</script>
