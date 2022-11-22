<template>
  <div>
    <h2>{{ source['name'] }}</h2>
    <ul>
      <li>Protocol: {{ source['protocol'] }}</li>
      <li>DSN: <code>{{ source['url'] }}</code></li>
    </ul>
  </div>
</template>

<script setup>
const route = useRoute();
const { data: source } = await useFetch(
  `http://localhost:8000/api/sources/${route.params.id}`
);
</script>
