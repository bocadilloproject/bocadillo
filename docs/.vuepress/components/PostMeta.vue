<template>
  <p v-if="post.date || post.author">
    <strong v-if="post.date">{{date(post)}}</strong>
    <template v-if="post.author">&middot; {{ post.author }}</template>
  </p>
</template>

<script>
import { format } from "date-fns";

export default {
  props: ["post"],
  methods: {
    date(post) {
      const d = new Date(post.date);
      return format(d, "MMMM Do, YYYY");
    }
  }
};
</script>
