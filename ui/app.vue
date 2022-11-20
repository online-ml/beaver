<template>
  <div style="display: flex; flex-direction: row;">
    <header style="margin-right: 3em">
      <nav style="width: 14em">
        <ul style="list-style: none;">
          <li><NuxtLink to="/"><b>🦫 Beaver</b></NuxtLink></li>
          <br>
          <li>⚙️ Infra</li>
          <ul style="padding-bottom: 1em;">
            <li><NuxtLink to="/sources">Sources</NuxtLink></li>
            <li><NuxtLink to="/processors">Data processors</NuxtLink></li>
            <li><NuxtLink to="/runners">Model runners</NuxtLink></li>
            <li><NuxtLink to="/sinks">Sinks</NuxtLink></li>
          </ul>
          <li>📊 Data</li>
          <ul style="padding-bottom: 1em;">
            <li><NuxtLink to="/features">Features</NuxtLink></li>
            <li><NuxtLink to="/targets">Targets</NuxtLink></li>
            <li><NuxtLink to="/predictions">Predictions</NuxtLink></li>
          </ul>
          <li>🔮 Modelling</li>
          <ul>
            <li><NuxtLink to="/models">Models</NuxtLink></li>
            <li><NuxtLink to="/experiments">Experiments</NuxtLink></li>
            <li><NuxtLink to="/serving">Serving</NuxtLink></li>
          </ul>
        </ul>
      </nav>
    </header>
    <NuxtLayout>
      <div style="display: flex; flex-direction: column">
        <h1>{{ route.path }}</h1>
        <NuxtPage />
      </div>
    </NuxtLayout>
  </div>
</template>

<script setup>
const route = useRoute()
</script>

<style>
table {
  font-family: arial, sans-serif;
  border-collapse: collapse;
  width: 100%;
}

td,
th {
  border: 1px solid #dddddd;
  text-align: left;
  padding: 8px;
}

tr:nth-child(even) {
  background-color: #dddddd;
}

body {
  font-family: "Helvetica", "Arial", sans-serif;
  line-height: 1.5;
}

code,
pre {
  background: #eee;
}

code {
  padding: 2px 4px;
  vertical-align: text-bottom;
}

pre {
  padding: 2em;
}

header {
  margin-top: 1em;
}

a:visited {
    color: black;
    text-decoration-color: hotpink;
}
</style>
