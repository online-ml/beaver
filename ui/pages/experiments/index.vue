<template>
  <div>
    <table>
      <tr>
        <th>Name</th>
      </tr>
      <tr v-for="experiment in experiments">
        <td>
          <NuxtLink :to="`experiments/${experiment.id}`">{{
            experiment.name
          }}</NuxtLink>
        </td>
      </tr>
    </table>
  </div>
</template>

<script setup>
const { data: experiments } = await useFetch(
  "http://localhost:8000/api/experiments"
);
</script>
