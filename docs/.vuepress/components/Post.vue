<template>
  <Layout>
    <template slot="page-top">
      <p class="navbar-fix page-width">
        <router-link to="/news/">← Back to posts</router-link>
      </p>

      <PostShare :page="$page"/>

      <PostJumbotron :post="$page.frontmatter"/>

      <div class="page-width">
        <hr>
      </div>
    </template>
  </Layout>
</template>

<script>
import Layout from "@theme/layouts/Layout.vue";
import PostShare from "./PostShare";

export default { components: { Layout, PostShare } };
</script>

<style scoped>
.navbar-fix {
  padding: 4em 2rem 0 2rem;
}
</style>
