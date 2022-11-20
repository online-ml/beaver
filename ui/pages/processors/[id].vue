<template>
  <div>
    <h2>{{ processor['name'] }}</h2>
    <ul>
      <li>Protocol: {{ processor['protocol'] }}</li>
      <li>DSN: <code>{{ processor['url'] }}</code></li>
    </ul>
  </div>
</template>

<script setup>
const route = useRoute();
const { data: processor } = await useFetch(
  `http://localhost:8000/api/processors/${route.params.id}`
);
</script>
