<template>
  <div>
    <h2>{{ exp['name'] }}</h2>
    <ul>
      <li>Features: <NuxtLink :to="`/features/${exp['feature_set_id']}`">{{ exp['feature_set_id'] }}</NuxtLink></li>
      <li>Target: <NuxtLink :to="`/targets/${exp['target_id']}`">{{ exp['target_id'] }}</NuxtLink></li>
      <li>Model: <NuxtLink :to="`/models/${exp['model_id']}`">{{ exp['model_id'] }}</NuxtLink></li>
      <li>Runner: <NuxtLink :to="`/runners/${exp['runner_id']}`">{{ exp['runner_id'] }}</NuxtLink></li>
    </ul>
    <h3>Monitoring</h3>
    <p>{{ monitoring }}</p>
  </div>
</template>

<script setup>
const route = useRoute();
const { data: exp } = await useFetch(
  `http://localhost:8000/api/experiments/${route.params.id}`
);

const { data: monitoring, refresh } = await useFetch(
  `http://localhost:8000/api/experiments/${route.params.id}/monitor`
);

setInterval(refresh, 2000);
</script>
