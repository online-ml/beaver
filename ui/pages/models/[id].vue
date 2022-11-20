<template>
  <div>
    <h2>{{ model["name"] }}</h2>
    <code>{{ model['class'] }}</code>
    <pre>{{ model['repr'] }}</pre>
  </div>
</template>

<script setup>
const route = useRoute();
const { data: model } = await useFetch(
  `http://localhost:8000/api/models/${route.params.id}`
);
</script>
