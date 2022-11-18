<template>
  <div>
    <h1>Runners - {{ runner.id }}</h1>
    <code>{{ runner }}</code>
  </div>
</template>

<script setup>
const route = useRoute();
const { data: runner } = await useFetch(
  `http://api:8000/api/runners/${route.params.id}`
);
</script>
