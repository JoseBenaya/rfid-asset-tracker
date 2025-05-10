<script lang="ts">
  import { onMount } from "svelte";
  import { link } from "svelte-spa-router";
  import { format, parseISO } from "date-fns";
  import ScanEventList from "./ScanEventList.svelte";
  
  // Define types
  type Asset = {
    id: number;
    tag_id: string;
    name: string;
    description: string;
    asset_type: string;
    status: string;
    last_seen: string | null;
    last_location: string | null;
  };
  
  type Scan = {
    id: number;
    location: string;
    timestamp: string;
    rssi: number | null;
  };
  
  // Get the asset ID from route params
  export let params: { id?: string } = {};
  
  // State
  let asset: Asset | null = null;
  let scanHistory: Scan[] = [];
  let loading = true;
  let error: string | null = null;
  
  // Format date
  function formatDateTime(date: string | null): string {
    if (!date) return "N/A";
    return format(parseISO(date), "PPpp");
  }
  
  // Load asset details
  async function loadAssetDetails(): Promise<void> {
    try {
      loading = true;
      error = null;
      
      // Get asset data
      const assetResponse = await fetch(`/api/assets/${params.id}`);
      if (!assetResponse.ok) {
        throw new Error(`Error fetching asset: ${assetResponse.statusText}`);
      }
      asset = await assetResponse.json();
      
      // Get scan history
      const scanResponse = await fetch(`/api/assets/${params.id}/scans?limit=10`);
      if (!scanResponse.ok) {
        throw new Error(`Error fetching scan history: ${scanResponse.statusText}`);
      }
      scanHistory = await scanResponse.json();
      
      loading = false;
    } catch (err) {
      console.error("Error loading asset details:", err);
      error = err instanceof Error ? err.message : String(err);
      loading = false;
    }
  }
  
  // Load data when component mounts or ID changes
  $: if (params && params.id) {
    loadAssetDetails();
  }

  onMount(() => {
    if (params && params.id) {
      loadAssetDetails();
    }
  });
</script>

<div>
  <div class="mb-6">
    <a href="/" use:link class="text-primary-600 hover:text-primary-800 flex items-center">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
      </svg>
      Back to Dashboard
    </a>
  </div>

  {#if loading}
    <div class="card text-center py-8">
      <p>Loading asset details...</p>
    </div>
  {:else if error}
    <div class="card bg-red-50 text-red-800 py-6">
      <p class="text-center">{error}</p>
      <div class="text-center mt-4">
        <button class="btn btn-primary" on:click={loadAssetDetails}>Retry</button>
      </div>
    </div>
  {:else if asset}
    <div class="card mb-6">
      <div class="flex justify-between items-start mb-4">
        <h1 class="text-2xl font-bold">{asset.name}</h1>
        <span class={`badge ${asset.status === 'active' ? 'badge-active' : asset.status === 'missing' ? 'badge-missing' : 'badge-idle'}`}>
          {asset.status}
        </span>
      </div>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div>
          <h2 class="text-lg font-semibold mb-3">Asset Information</h2>
          <table class="w-full">
            <tbody>
              <tr>
                <td class="py-2 font-medium">Tag ID</td>
                <td>{asset.tag_id}</td>
              </tr>
              <tr>
                <td class="py-2 font-medium">Asset Type</td>
                <td>{asset.asset_type}</td>
              </tr>
              <tr>
                <td class="py-2 font-medium">Description</td>
                <td>{asset.description || 'No description'}</td>
              </tr>
              <tr>
                <td class="py-2 font-medium">Last Seen</td>
                <td>{formatDateTime(asset.last_seen)}</td>
              </tr>
              <tr>
                <td class="py-2 font-medium">Last Location</td>
                <td>{asset.last_location || 'Unknown'}</td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <div>
          <h2 class="text-lg font-semibold mb-3">RFID Information</h2>
          <div class="bg-gray-50 p-4 rounded-lg">
            <div class="flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 text-primary-600 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
              </svg>
            </div>
            <div class="text-center">
              <p class="text-xl font-mono font-bold">{asset.tag_id}</p>
              <p class="text-sm text-gray-600 mt-1">RFID Tag ID</p>
            </div>
          </div>
        </div>
      </div>
      
      <div class="border-t pt-4">
        <h2 class="text-lg font-semibold mb-3">Scan History</h2>
        {#if scanHistory.length === 0}
          <p class="text-center text-gray-500 py-4">No scan history available</p>
        {:else}
          <div class="overflow-x-auto">
            <table class="w-full">
              <thead>
                <tr class="bg-gray-50">
                  <th class="text-left py-2 px-4">Time</th>
                  <th class="text-left py-2 px-4">Location</th>
                  <th class="text-left py-2 px-4">Signal Strength</th>
                </tr>
              </thead>
              <tbody>
                {#each scanHistory as scan}
                  <tr class="border-t">
                    <td class="py-2 px-4">{formatDateTime(scan.timestamp)}</td>
                    <td class="py-2 px-4">{scan.location}</td>
                    <td class="py-2 px-4">{scan.rssi ? `${scan.rssi} dBm` : 'N/A'}</td>
                  </tr>
                {/each}
              </tbody>
            </table>
          </div>
        {/if}
      </div>
    </div>
  {:else}
    <div class="card bg-yellow-50 text-yellow-800 py-6 text-center">
      <p>Asset not found</p>
    </div>
  {/if}
</div> 