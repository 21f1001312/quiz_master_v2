<!-- HomeView.vue -->
<template>
  <div class="home-container text-center d-flex flex-column justify-content-center align-items-center">
    <h1 class="mb-4 text-white">Welcome to Quiz App</h1>
    <div>
      <router-link to="/login" class="btn btn-primary me-2">Login</router-link>
      <router-link to="/signup" class="btn btn-success">Signup</router-link>
    </div>
  </div>
</template>

<script>
export default {
  name: "HomeView",
};
</script>

<style scoped>
.home-container {
  background-image: url('/quiz.jpg'); /* from public folder */
  background-size: cover;
  background-repeat: no-repeat;
  background-position: center center;
  min-height: 100vh;
  padding: 2rem;
}

</style>
