<template>
  <div>
    <h1>Sinks - {{ sink.id }}</h1>
    <code>{{ sink }}</code>
  </div>
</template>

<script setup>
const route = useRoute();
const { data: sink } = await useFetch(
  `http://localhost:8000/api/sinks/${route.params.id}`
);
</script>
