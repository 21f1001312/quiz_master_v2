// AdminDashboard.vue
<template>
  <div class="container mt-5">
    <h2>Master Dashboard</h2>
    <p>Welcome, Master!</p>
  </div>
</template>

<script>
export default {
  name: 'QmDash',
  mounted() {
    const role = localStorage.getItem('userRole');
    if (role !== 'quiz_master') {
      alert('Access denied: Master only');
      this.$router.push('/login');
    }
  },
};
</script>