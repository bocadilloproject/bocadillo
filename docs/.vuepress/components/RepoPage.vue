<template>
  <custom-link :href="href" :text="text"></custom-link>
</template>

<script>
import project from "../project";

export default {
  props: ["to", "text"],
  computed: {
    href() {
      return project.repoPage(this.to);
    }
  }
};
</script>
