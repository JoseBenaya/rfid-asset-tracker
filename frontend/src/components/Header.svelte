<script lang="ts">
  import { link } from "svelte-spa-router";
</script>

<header class="bg-white shadow">
  <div class="container mx-auto px-4 py-4 flex justify-between items-center">
    <div class="flex items-center">
      <a href="/" use:link class="text-xl font-bold text-primary-600 flex items-center">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
        </svg>
        RFID Asset Tracker
      </a>
    </div>
    
    <nav>
      <ul class="flex space-x-6">
        <li>
          <a href="/" use:link class="text-gray-600 hover:text-primary-600">Dashboard</a>
        </li>
        <li>
          <a href="http://localhost:8000/docs" target="_blank" class="text-gray-600 hover:text-primary-600">API Docs</a>
        </li>
      </ul>
    </nav>
  </div>
</header> 