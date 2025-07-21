<template>
    <nav class="navbar bg-primary" data-bs-theme="dark">
        <div class="container">
            <a class="navbar-brand" href="#">Admin Dashboard</a>
            <button class="btn btn-outline-light ms-auto" @click="logout">Logout</button>
        </div>
    </nav>

</template>

<script>
export default{
    methods: {
        logout() {
            this.$router.push('/login');
        },
    }
}
</script>