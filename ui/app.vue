<template>
  <div style="display: flex; flex-direction: row">
    <header style="margin-right: 3em">
      <nav>
        <ul>
          <li>Infrastructure</li>
          <ul>
            <li><NuxtLink to="/sources">Sources</NuxtLink></li>
            <li><NuxtLink to="/processors">Data processors</NuxtLink></li>
            <li><NuxtLink to="/runners">Model runners</NuxtLink></li>
            <li><NuxtLink to="/sinks">Sinks</NuxtLink></li>
          </ul>
          <li>Assets</li>
          <ul>
            <li><NuxtLink to="/features">Features</NuxtLink></li>
            <li><NuxtLink to="/targets">Targets</NuxtLink></li>
            <li><NuxtLink to="/models">Models</NuxtLink></li>
          </ul>
          <li>Deployment</li>
          <ul>
            <li><NuxtLink to="/experiments">Experiments</NuxtLink></li>
            <li><NuxtLink to="/monitoring">Monitoring</NuxtLink></li>
            <li><NuxtLink to="/serving">Serving</NuxtLink></li>
          </ul>
        </ul>
      </nav>
    </header>
    <NuxtLayout>
      <div style="display: flex; flex-direction: column">
        <NuxtPage />
      </div>
    </NuxtLayout>
  </div>
</template>

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
</style>
