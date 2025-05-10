<script lang="ts">
  import Router from "svelte-spa-router";
  import { push, link } from "svelte-spa-router";
  import Dashboard from "./components/Dashboard.svelte";
  import Header from "./components/Header.svelte";
  import AssetDetail from "./components/AssetDetail.svelte";

  const routes = {
    '/': Dashboard,
    '/assets/:id': AssetDetail
  };
</script>

<div class="min-h-screen flex flex-col">
  <Header />
  
  <main class="flex-grow container mx-auto py-6 px-4">
    <Router {routes} />
  </main>
  
  <footer class="bg-gray-100 py-4">
    <div class="container mx-auto px-4 text-center text-gray-600 text-sm">
      RFID Asset Tracker © {new Date().getFullYear()} - Simulation Project
    </div>
  </footer>
</div> 