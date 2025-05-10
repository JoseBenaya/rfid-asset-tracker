<script lang="ts">
  import { link } from "svelte-spa-router";
  import { format, parseISO } from "date-fns";
  
  // Define asset type
  type Asset = {
    id: number;
    tag_id: string;
    name: string;
    description: string;
    asset_type: string;
    status: string;
    last_seen: string;
    last_location: string;
  };

  export let asset: Asset;
  
  // Format last seen time or return null
  function formatLastSeen(lastSeen: string | null): string {
    if (!lastSeen) return "Never";
    return format(parseISO(lastSeen), "MMM d, yyyy h:mm a");
  }
  
  // Get the status badge class based on asset status
  function getStatusBadgeClass(status: string): string {
    switch (status) {
      case "active": return "badge badge-active";
      case "missing": return "badge badge-missing";
      case "idle": return "badge badge-idle";
      default: return "badge";
    }
  }
  
  // Get an icon for the asset type
  function getAssetTypeIcon(type: string): string {
    switch (type.toLowerCase()) {
      case "electronics":
        return "M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z";
      case "furniture":
        return "M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M9 16h.01";
      default:
        return "M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4";
    }
  }
</script>

<div class="card hover:shadow-md transition-shadow">
  <div class="flex justify-between mb-2">
    <div>
      <span class={getStatusBadgeClass(asset.status)}>
        {asset.status}
      </span>
    </div>
    <div class="text-gray-500 text-sm">
      ID: {asset.tag_id}
    </div>
  </div>
  
  <div class="flex items-start mb-3">
    <div class="w-10 h-10 rounded-full bg-primary-100 flex items-center justify-center text-primary-600 mr-3">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={getAssetTypeIcon(asset.asset_type)} />
      </svg>
    </div>
    <div>
      <h3 class="text-lg font-medium">{asset.name}</h3>
      <p class="text-gray-600 text-sm mb-1">{asset.asset_type}</p>
    </div>
  </div>
  
  <div class="text-sm text-gray-600 mb-4">
    {#if asset.description}
      <p>{asset.description}</p>
    {/if}
  </div>
  
  <div class="border-t pt-3">
    <div class="text-sm flex justify-between">
      <div>
        <span class="font-medium">Last seen:</span> {formatLastSeen(asset.last_seen)}
      </div>
      
      {#if asset.last_location}
        <div class="text-gray-600">
          <span class="font-medium">Location:</span> {asset.last_location}
        </div>
      {/if}
    </div>
    
    <a href={`/assets/${asset.id}`} use:link class="btn btn-primary mt-3 w-full block text-center">
      View Details
    </a>
  </div>
</div> 