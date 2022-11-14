<template>
  <div>
    <h1>Sinks</h1>
    <table>
      <tr>
        <th>Name</th>
        <th>Protocol</th>
        <th>URL</th>
      </tr>
      <tr v-for="sink in sinks">
        <td>
          <NuxtLink :to="`sinks/${sink.id}`">{{ sink.name }}</NuxtLink>
        </td>
        <td>{{ sink.protocol }}</td>
        <td>{{ sink.url }}</td>
      </tr>
    </table>
  </div>
</template>

<script setup>
const { data: sinks } = await useFetch("http://localhost:8000/api/sinks");
</script>
