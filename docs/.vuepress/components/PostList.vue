<template>
  <div class="posts" v-if="posts.length">
    <div class="post" v-for="post in posts">
      <div>
        <img v-if="post.frontmatter.image" :src="$withBase(post.frontmatter.image)" alt>
      </div>
      <PostMeta class="post-meta" :post="post.frontmatter"/>
      <h2 class="post-title">
        <router-link :to="post.path">{{post.frontmatter.title}}</router-link>
      </h2>
      <p>{{post.frontmatter.description}}</p>
    </div>
  </div>
</template>

<script>
import { getBlogPages } from "./utils";
export default {
  props: ["page"],
  computed: {
    posts() {
      return getBlogPages(this.$site);
    }
  }
};
</script>

<style lang="stylus" scoped>
.post-meta {
  margin-bottom: 0.25em;
}

.post {
  h2 {
    margin-top: 0;
  }

  &:not(:first-child) {
    margin-top: 4em;
  }
}
</style>

