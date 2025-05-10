<script lang="ts">
  // Define scan type
  type ScanEvent = {
    tag_id: string;
    location: string;
    timestamp: string;
    asset_name?: string;
    asset_type?: string;
    rssi?: number;
  };
  
  export let onScanCreated: (scan: ScanEvent) => void = () => {};
  
  // Form data
  let tagId: string = "RF001";
  let location: string = "Office";
  let submitting: boolean = false;
  let error: string = "";
  let success: string = "";
  
  // Predefined locations and tag IDs (would come from API in a real app)
  const locations: string[] = ["Office", "Warehouse", "Meeting Room", "Lobby", "Kitchen"];
  const tagIds: string[] = ["RF001", "RF002", "RF003", "RF004", "RF005"];
  
  // Submit the form to create a manual scan
  async function submitScan(): Promise<void> {
    submitting = true;
    error = "";
    success = "";
    
    try {
      const response = await fetch("/api/scan", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          tag_id: tagId,
          location: location,
        }),
      });
      
      if (!response.ok) {
        throw new Error(`Error creating scan: ${response.statusText}`);
      }
      
      const scanData: ScanEvent = await response.json();
      success = `Scan recorded for ${scanData.asset_name || tagId}`;
      
      // Pass the scan data to the parent component
      onScanCreated(scanData);
      
    } catch (err) {
      console.error("Error creating scan:", err);
      error = err instanceof Error ? err.message : String(err);
    } finally {
      submitting = false;
    }
  }
</script>

<form on:submit|preventDefault={submitScan} class="space-y-4">
  {#if error}
    <div class="bg-red-100 text-red-700 p-3 rounded-md text-sm">
      {error}
    </div>
  {/if}
  
  {#if success}
    <div class="bg-green-100 text-green-700 p-3 rounded-md text-sm">
      {success}
    </div>
  {/if}

  <div>
    <label for="tagId" class="block text-sm font-medium text-gray-700 mb-1">
      Tag ID
    </label>
    <select
      id="tagId"
      bind:value={tagId}
      class="block w-full border-gray-300 rounded-md shadow-sm p-2 bg-white"
      disabled={submitting}
    >
      {#each tagIds as id}
        <option value={id}>{id}</option>
      {/each}
    </select>
  </div>
  
  <div>
    <label for="location" class="block text-sm font-medium text-gray-700 mb-1">
      Location
    </label>
    <select
      id="location"
      bind:value={location}
      class="block w-full border-gray-300 rounded-md shadow-sm p-2 bg-white"
      disabled={submitting}
    >
      {#each locations as loc}
        <option value={loc}>{loc}</option>
      {/each}
    </select>
  </div>
  
  <button
    type="submit"
    class="btn btn-primary w-full"
    disabled={submitting}
  >
    {submitting ? "Processing..." : "Simulate Scan"}
  </button>
</form> 