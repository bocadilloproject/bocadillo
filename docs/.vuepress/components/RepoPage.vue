<template>
  <custom-link :href="href" :text="text"></custom-link>
</template>

<script>
import project from "../project";

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
      return project.repoPage(this.to, { branch: this.branch });
    }
  }
};
</script>
