<template>
  <div>
    <h2>{{ sink['name'] }}</h2>
    <ul>
      <li>Protocol: {{ sink['protocol'] }}</li>
      <li>DSN: <code>{{ sink['url'] }}</code></li>
    </ul>
  </div>
</template>

<script setup>
const route = useRoute();
const { data: sink } = await useFetch(
  `http://localhost:8000/api/sinks/${route.params.id}`
);
</script>
