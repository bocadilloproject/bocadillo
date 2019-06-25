<template>
  <div>
    <div class="u-center-h">
      <b-tabs :tabs="tabs" @selected="slotKey = $event.slot"/>
    </div>
    <Content v-if="slotKey" :slot-key="slotKey"/>
  </div>
</template>

<script>
export default {
  props: {
    labels: {
      type: Array
    }
  },
  data() {
    return {
      tabs: this.labels.map((label, index) => ({
        label,
        slot: `compare-${index}`
      })),
      slotKey: null
    };
  }
};
</script>
