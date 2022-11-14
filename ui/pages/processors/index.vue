<template>
  <div>
    <h1>Processors</h1>
    <table>
      <tr>
        <th>Name</th>
        <th>Protocol</th>
        <th>URL</th>
      </tr>
      <tr v-for="processor in processors">
        <td>
          <NuxtLink :to="`processors/${processor.id}`">{{
            processor.name
          }}</NuxtLink>
        </td>
        <td>{{ processor.protocol }}</td>
        <td>{{ processor.url }}</td>
      </tr>
    </table>
  </div>
</template>

<script setup>
const { data: processors } = await useFetch(
  "http://localhost:8000/api/processors"
);
</script>
