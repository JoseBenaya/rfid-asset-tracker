<script lang="ts">
  import { format, parseISO } from "date-fns";
  
  // Define scan event type
  type ScanEvent = {
    tag_id: string;
    location: string;
    timestamp: string;
    asset_name?: string;
    asset_type?: string;
    rssi?: number;
  };
  
  export let events: ScanEvent[] = [];
  
  // Format timestamp
  function formatTime(timestamp: string | null): string {
    if (!timestamp) return "N/A";
    return format(parseISO(timestamp), "h:mm:ss a");
  }
  
  // Format date
  function formatDate(timestamp: string | null): string {
    if (!timestamp) return "N/A";
    return format(parseISO(timestamp), "MMM d");
  }
</script>

{#if events.length === 0}
  <div class="text-center py-4 text-gray-500">
    <p>No recent scan events</p>
  </div>
{:else}
  <ul class="divide-y">
    {#each events as event}
      <li class="py-3 flex items-start">
        <div class="flex-shrink-0 w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center text-primary-600 mr-3">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v1m6 11h2m-6 0h-2v4m0-11v3m0 0h.01M12 12h4.01M16 20h4M4 12h4m12 0h.01M5 8h2a1 1 0 001-1V5a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1zm12 0h2a1 1 0 001-1V5a1 1 0 00-1-1h-2a1 1 0 00-1 1v2a1 1 0 001 1zM5 20h2a1 1 0 001-1v-2a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1z" />
          </svg>
        </div>
        <div class="flex-grow">
          <div class="flex justify-between">
            <p class="font-medium">
              {event.asset_name || `Asset (${event.tag_id})`}
            </p>
            <span class="text-sm text-gray-500">
              {formatTime(event.timestamp)}
            </span>
          </div>
          <p class="text-sm text-gray-600">
            Scanned at <span class="font-medium">{event.location}</span>
          </p>
          {#if event.rssi}
            <p class="text-xs text-gray-500 mt-1">
              Signal strength: {event.rssi} dBm
            </p>
          {/if}
        </div>
      </li>
    {/each}
  </ul>
{/if} 