<template>
  <div>
    <h2>{{ model["name"] }}</h2>
    <ul>
      <li><code>{{ model['class'] }}</code></li>
      <li>{{ model['task'] }} task</li>
    </ul>
    <pre>{{ model['repr'] }}</pre>
  </div>
</template>

<script setup>
const route = useRoute();
const { data: model } = await useFetch(
  `http://localhost:8000/api/models/${route.params.id}`
);
</script>
