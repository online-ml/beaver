<template>
  <div>
    <h1>Targets</h1>
    <table>
      <tr>
        <th>Name</th>
      </tr>
      <tr v-for="target in targets">
        <td>
          <NuxtLink :to="`targets/${target.id}`">{{ target.name }}</NuxtLink>
        </td>
      </tr>
    </table>
  </div>
</template>

<script setup>
const { data: targets } = await useFetch("http://api:8000/api/targets");
</script>
