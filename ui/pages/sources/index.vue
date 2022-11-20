<template>
  <div>
    <table>
      <tr>
        <th>Name</th>
        <th>Protocol</th>
      </tr>
      <tr v-for="source in sources">
        <td>
          <NuxtLink :to="`sources/${source.id}`">{{ source.name }}</NuxtLink>
        </td>
        <td>{{ source.protocol }}</td>
      </tr>
    </table>
  </div>
</template>

<script setup>
const { data: sources } = await useFetch("http://localhost:8000/api/sources");
</script>
