<template>
  <div>
    <table>
      <tr>
        <th>Name</th>
        <th>Protocol</th>
      </tr>
      <tr v-for="processor in processors">
        <td>
          <NuxtLink :to="`processors/${processor.id}`">{{
            processor.name
          }}</NuxtLink>
        </td>
        <td>{{ processor.protocol }}</td>
      </tr>
    </table>
  </div>
</template>

<script setup>
const { data: processors } = await useFetch(
  "http://localhost:8000/api/processors"
);
</script>
