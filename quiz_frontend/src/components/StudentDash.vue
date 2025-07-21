// StudentDash.vue
<template>
  <nav class="navbar bg-primary" data-bs-theme="dark">
        <div class="container">
            <a class="navbar-brand" href="#">Admin Dashboard</a>
            <button class="btn btn-outline-light ms-auto" @click="logout">Logout</button>
        </div>
    </nav>
</template>

<script>
export default {
  methods: {
        async logout() {
            localStorage.removeItem('studentToken');
            this.$router.push('/');
        },
      },
};
</script>