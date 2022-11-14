<template>
  <div>
    <h1>Features</h1>
    <table>
      <tr>
        <th>Name</th>
      </tr>
      <tr v-for="feature in features">
        <td>
          <NuxtLink :to="`features/${feature.id}`">{{ feature.name }}</NuxtLink>
        </td>
      </tr>
    </table>
  </div>
</template>

<script setup>
const { data: features } = await useFetch("http://localhost:8000/api/features");
</script>

