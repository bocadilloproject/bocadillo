<template>
  <Page :sidebarItems="[]">
    <template slot="top">
      <p class="wrapper">
        <router-link to="/blog/">← Back to posts</router-link>
      </p>
      <PostJumbotron :post="$page.frontmatter"/>
      <div class="wrapper">
        <hr>
      </div>
    </template>
  </Page>
</template>

<script>
import Page from "@default-theme/Page";
export default { components: { Page } };
</script>
