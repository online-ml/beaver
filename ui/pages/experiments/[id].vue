<template>
  <div>
    <h1>Experiments - {{ experiment.id }}</h1>
    <code>{{ experiment }}</code>
  </div>
</template>

<script setup>
const route = useRoute();
const { data: experiment } = await useFetch(
  `http://api:8000/api/experiments/${route.params.id}`
);
</script>
