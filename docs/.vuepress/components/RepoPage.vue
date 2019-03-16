<template>
  <custom-link :href="href" :text="text"></custom-link>
</template>

<script>
export default {
  props: {
    to: {
      type: String
    },
    branch: {
      type: String,
      default: "master"
    },
    text: {
      type: String
    }
  },
  computed: {
    href() {
      const base = "https://github.com/bocadilloproject/bocadillo";
      return `${base}/${this.branch}/blob/${this.to}`;
    }
  }
};
</script>
