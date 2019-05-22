<template>
  <div align="center">
    <img :src="src" :alt="altContent">
    <figcaption v-if="caption" style="font-style: italic;">{{ caption }}</figcaption>
  </div>
</template>

<script>
export default {
  props: {
    src: {
      type: String
    },
    alt: {
      type: String,
      default: ""
    },
    caption: {
      type: String,
      default: null
    }
  },
  computed: {
    altContent() {
      return this.alt || this.caption;
    }
  }
};
</script>
