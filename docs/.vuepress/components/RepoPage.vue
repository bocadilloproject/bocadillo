<template>
  <custom-link :href="href" :text="text"></custom-link>
</template>

<script>
export default {
  props: ["to", "text"],
  computed: {
    href() {
      return `https://github.com/bocadilloproject/bocadillo/master/blob/${
        this.to
      }`;
    }
  }
};
</script>
