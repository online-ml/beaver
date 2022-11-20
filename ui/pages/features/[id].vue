<template>
  <div>
    <h2>{{ features['name'] }}</h2>
    <p>Processed by <NuxtLink :to="`/processors/${features['processor_id']}`">{{ features['processor_id'] }}</NuxtLink></p>
    <pre>{{ features['query'] }}</pre>
  </div>
</template>

<script setup>
const route = useRoute();
const { data: features } = await useFetch(
  `http://localhost:8000/api/features/${route.params.id}`
);
</script>
