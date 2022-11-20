<template>
  <div>
    <h2>{{ target['name'] }}</h2>
    <p>Processed by <NuxtLink :to="`/processors/${target['processor_id']}`">{{ target['processor_id'] }}</NuxtLink></p>
    <pre>{{ target['query'] }}</pre>
  </div>
</template>

<script setup>
const route = useRoute();
const { data: target } = await useFetch(
  `http://localhost:8000/api/targets/${route.params.id}`
);
</script>
