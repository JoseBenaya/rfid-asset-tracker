<script lang="ts">
  import { onMount, onDestroy } from "svelte";
  import { push, link } from "svelte-spa-router";
  import { format } from "date-fns";
  import AssetCard from "./AssetCard.svelte";
  import ScanEventList from "./ScanEventList.svelte";
  import ManualScanForm from "./ManualScanForm.svelte";
  
  // Define Types
  type Asset = {
    id: number;
    tag_id: string;
    name: string;
    description: string;
    asset_type: string;
    status: string;
    last_seen: string;
    last_location: string;
  }
  
  // Scan event type
  type ScanEvent = {
    tag_id: string;
    location: string;
    timestamp: string;
    asset_name?: string;
    asset_type?: string;
    rssi?: number;
  }
  
  // State
  let assets: Asset[] = [];
  let filteredAssets: Asset[] = [];
  let recentScans: ScanEvent[] = [];
  let filter: string = "all";
  let ws: WebSocket;
  let loadingAssets = true;
  let errorMsg = "";
  
  // Filter assets based on status
  $: {
    if (filter === "all") {
      filteredAssets = [...assets];
    } else {
      filteredAssets = assets.filter(asset => asset.status === filter);
    }
  }
  
  // Load assets from API
  async function loadAssets() {
    try {
      loadingAssets = true;
      const response = await fetch("/api/assets");
      if (!response.ok) {
        throw new Error(`Error fetching assets: ${response.statusText}`);
      }
      assets = await response.json();
      loadingAssets = false;
    } catch (error) {
      console.error("Failed to load assets:", error);
      errorMsg = error instanceof Error ? error.message : String(error);
      loadingAssets = false;
    }
  }
  
  // Connect to WebSocket for real-time updates
  function connectWebSocket() {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const wsUrl = `${protocol}//${window.location.host}/ws`;
    
    ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
      console.log("WebSocket connection established");
    };
    
    ws.onmessage = (event) => {
      const scanEvent: ScanEvent = JSON.parse(event.data);
      handleScanEvent(scanEvent);
    };
    
    ws.onerror = (error) => {
      console.error("WebSocket error:", error);
    };
    
    ws.onclose = () => {
      console.log("WebSocket connection closed");
      // Attempt to reconnect after a delay
      setTimeout(connectWebSocket, 3000);
    };
  }
  
  // Handle incoming scan events
  function handleScanEvent(scanEvent: ScanEvent) {
    // Add to recent scans (keep only last 5)
    recentScans = [scanEvent, ...recentScans.slice(0, 4)];
    
    // Update asset status if applicable
    const asset = assets.find(a => a.tag_id === scanEvent.tag_id);
    if (asset) {
      asset.last_seen = scanEvent.timestamp;
      asset.last_location = scanEvent.location;
      asset.status = "active";
      
      // Force reactivity by creating a new array
      assets = [...assets];
    }
  }
  
  // Lifecycle
  onMount(() => {
    loadAssets();
    connectWebSocket();
    
    // Set up an interval to refresh assets every minute
    const interval = setInterval(loadAssets, 60000);
    
    return () => {
      clearInterval(interval);
    };
  });
  
  onDestroy(() => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.close();
    }
  });
</script>

<div class="mb-6">
  <h1 class="text-2xl font-bold mb-4">Asset Tracking Dashboard</h1>
  
  <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
    <div class="card">
      <h2 class="text-lg font-semibold mb-2">Total Assets</h2>
      <p class="text-3xl font-bold text-primary-600">{assets.length}</p>
    </div>
    
    <div class="card">
      <h2 class="text-lg font-semibold mb-2">Active Assets</h2>
      <p class="text-3xl font-bold text-green-600">
        {assets.filter(a => a.status === "active").length}
      </p>
    </div>
    
    <div class="card">
      <h2 class="text-lg font-semibold mb-2">Missing Assets</h2>
      <p class="text-3xl font-bold text-red-600">
        {assets.filter(a => a.status === "missing").length}
      </p>
    </div>
  </div>
  
  <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
    <div class="lg:col-span-2">
      <div class="card mb-6">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-lg font-semibold">Asset List</h2>
          
          <div class="flex space-x-2">
            <button 
              class="btn {filter === 'all' ? 'btn-primary' : 'btn-secondary'}" 
              on:click={() => filter = "all"}>
              All
            </button>
            <button 
              class="btn {filter === 'active' ? 'btn-primary' : 'btn-secondary'}" 
              on:click={() => filter = "active"}>
              Active
            </button>
            <button 
              class="btn {filter === 'missing' ? 'btn-primary' : 'btn-secondary'}" 
              on:click={() => filter = "missing"}>
              Missing
            </button>
          </div>
        </div>
        
        {#if loadingAssets}
          <div class="text-center py-4">
            <p>Loading assets...</p>
          </div>
        {:else if errorMsg}
          <div class="bg-red-100 text-red-700 p-4 rounded-md">
            <p>{errorMsg}</p>
            <button class="btn btn-secondary mt-2" on:click={loadAssets}>Retry</button>
          </div>
        {:else if filteredAssets.length === 0}
          <div class="text-center py-4 text-gray-500">
            <p>No assets found</p>
          </div>
        {:else}
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {#each filteredAssets as asset (asset.id)}
              <AssetCard {asset} />
            {/each}
          </div>
        {/if}
      </div>
    </div>
    
    <div>
      <div class="card mb-6">
        <h2 class="text-lg font-semibold mb-4">Recent Scan Events</h2>
        <ScanEventList events={recentScans} />
      </div>
      
      <div class="card">
        <h2 class="text-lg font-semibold mb-4">Simulate Manual Scan</h2>
        <ManualScanForm onScanCreated={handleScanEvent} />
      </div>
    </div>
  </div>
</div> 