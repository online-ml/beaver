<template>
  <div>
    <h1>Processors - {{ processor.id }}</h1>
    <code>{{ processor }}</code>
  </div>
</template>

<script setup>
const route = useRoute();
const { data: processor } = await useFetch(
  `http://api:8000/api/processors/${route.params.id}`
);
</script>
