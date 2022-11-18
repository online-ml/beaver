<template>
  <div>
    <h1>Sources</h1>
    <table>
      <tr>
        <th>Name</th>
        <th>Protocol</th>
        <th>URL</th>
      </tr>
      <tr v-for="source in sources">
        <td>
          <NuxtLink :to="`sources/${source.id}`">{{ source.name }}</NuxtLink>
        </td>
        <td>{{ source.protocol }}</td>
        <td>{{ source.url }}</td>
      </tr>
    </table>
  </div>
</template>

<script setup>
const { data: sources } = await useFetch("http://api:8000/api/sources");
</script>
