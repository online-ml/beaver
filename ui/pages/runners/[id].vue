<template>
  <div>
    <h2>{{ runner['name'] }}</h2>
    <ul>
      <li>Protocol: {{ runner['protocol'] }}</li>
      <li>URL: <code>{{ runner['url'] }}</code></li>
    </ul>
  </div>
</template>

<script setup>
const route = useRoute();
const { data: runner } = await useFetch(
  `http://localhost:8000/api/runners/${route.params.id}`
);
</script>
