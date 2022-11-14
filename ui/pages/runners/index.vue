<template>
  <div>
    <h1>Runners</h1>
    <table>
      <tr>
        <th>Name</th>
        <th>Protocol</th>
        <th>URL</th>
      </tr>
      <tr v-for="runner in runners">
        <td>
          <NuxtLink :to="`runners/${runner.id}`">{{ runner.name }}</NuxtLink>
        </td>
        <td>{{ runner.protocol }}</td>
        <td>{{ runner.url }}</td>
      </tr>
    </table>
  </div>
</template>

<script setup>
const { data: runners } = await useFetch("http://localhost:8000/api/runners");
</script>
