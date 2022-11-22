<template>
  <div>
    <table>
      <tr>
        <th>Name</th>
        <th>Protocol</th>
      </tr>
      <tr v-for="runner in runners">
        <td>
          <NuxtLink :to="`runners/${runner.id}`">{{ runner.name }}</NuxtLink>
        </td>
        <td>{{ runner.protocol }}</td>
      </tr>
    </table>
  </div>
</template>

<script setup>
const { data: runners } = await useFetch("http://localhost:8000/api/runners");
</script>
