<template>
  <div>
    <h1>Features - {{ features.id }}</h1>
    <code>{{ features }}</code>
  </div>
</template>

<script setup>
const route = useRoute();
const { data: features } = await useFetch(
  `http://localhost:8000/api/features/${route.params.id}`
);
</script>
