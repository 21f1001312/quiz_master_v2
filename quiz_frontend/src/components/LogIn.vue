<template>
  <div class="container mt-5">
    <div class="row justify-content-center">
      <div class="col-md-6">
        <div class="card">
          <div class="card-header">
            Login
          </div>
          <div class="card-body">
            <form @submit.prevent="loginUser">
              <div class="form-group mb-3">
                <label for="email">Email</label>
                <input type="email" class="form-control" id="email" v-model="email" required />
              </div>
              <div class="form-group mb-3">
                <label for="password">Password</label>
                <input type="password" class="form-control" id="password" v-model="password" required />
              </div>
              <div v-if="errorMessage" class="text-danger mb-3">{{ errorMessage }}</div>
              <div class="form-group">
                <button type="submit" class="btn btn-primary w-100">Login</button>
              </div>
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
      email: '',
      password: '',
      errorMessage: null,
    };
  },
  methods: {
    async loginUser() {
      this.errorMessage = null;
      const payload = {
        username: this.email,
        password: this.password,
      };

      try {
        const response = await fetch("/api/login", {
          method: "POST",
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(payload)
        });

        const result = await response.json();

        if (!response.ok) {
          this.errorMessage = result.message || "Login Failed";
        } else {
          alert("Login Successful");
          localStorage.setItem("adminToken", result.token);
          localStorage.setItem("studentToken", result.token);
          localStorage.setItem("userRole", result.user_role);
          localStorage.setItem("userName", result.User_name);

          // Role-based redirection
          const role = result.user_role;
          if (role === 'quiz_master') {
            alert("Admin login successful");
            localStorage.setItem("adminToken", result.token);
            this.$router.push("/quizmaster");
          } else if (role === 'student') {
            alert("Student login successful");
            localStorage.setItem("studentToken", result.token);
            this.$router.push("/student");
          } else {
            alert("Unknown role, unable to redirect.");
          }
        }
      } catch (error) {
        this.errorMessage = "Unable to connect to server";
      }
    },
  },
};

</script>