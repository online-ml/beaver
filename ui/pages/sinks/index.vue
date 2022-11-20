<template>
  <div>
    <table>
      <tr>
        <th>Name</th>
        <th>Protocol</th>
      </tr>
      <tr v-for="sink in sinks">
        <td>
          <NuxtLink :to="`sinks/${sink.id}`">{{ sink.name }}</NuxtLink>
        </td>
        <td>{{ sink.protocol }}</td>
      </tr>
    </table>
  </div>
</template>

<script setup>
const { data: sinks } = await useFetch("http://localhost:8000/api/sinks");
</script>
