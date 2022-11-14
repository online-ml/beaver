<template>
  <div>
    <h1>Models - {{ model.id }}</h1>
    <code>{{ model }}</code>
  </div>
</template>

<script setup>
const route = useRoute();
const { data: model } = await useFetch(
  `http://localhost:8000/api/models/${route.params.id}`
);
</script>
