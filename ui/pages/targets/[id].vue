<template>
  <div>
    <h1>Targets - {{ target.id }}</h1>
    <code>{{ target }}</code>
  </div>
</template>

<script setup>
const route = useRoute();
const { data: target } = await useFetch(
  `http://api:8000/api/targets/${route.params.id}`
);
</script>
