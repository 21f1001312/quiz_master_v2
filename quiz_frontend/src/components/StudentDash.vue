// StudentDash.vue
<template>
  <div class="container mt-5">
    <h2>Student Dashboard</h2>
    <p>Welcome, Student!</p>
  </div>
</template>

<script>
export default {
  name: 'QmDash',
  mounted() {
    const role = localStorage.getItem('userRole');
    if (role !== 'Student') {
      alert('Access denied: Student only');
      this.$router.push('/login');
    }
  },
};
</script>