<template>
  <div>
    <h1>Sources - {{ source.id }}</h1>
    <code>{{ source }}</code>
  </div>
</template>

<script setup>
const route = useRoute();
const { data: source } = await useFetch(
  `http://localhost:8000/api/sources/${route.params.id}`
);
</script>
