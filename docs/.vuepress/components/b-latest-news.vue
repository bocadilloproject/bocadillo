<template>
  <div>
    <template v-for="post in posts">
      <h4>
        <b-link :to="post.path">{{ post.frontmatter.title }}</b-link>
      </h4>
      <p class="post-description">{{ post.frontmatter.description }}</p>
    </template>
    <b-link to="/news/" :more="true">More news</b-link>
  </div>
</template>

<script>
import { getBlogPages } from "./utils";

export default {
  computed: {
    posts() {
      return getBlogPages(this.$site).slice(0, 2);
    }
  }
};
</script>

<style lang="stylus" scoped>
.post-description {
  font-size: 0.85em;
}
</style>
