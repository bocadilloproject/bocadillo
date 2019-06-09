<template>
  <aside class="home-sidebar">
    <h3 class="first">Latest news</h3>
    <b-latest-news/>

    <h3>New to Bocadillo?</h3>
    <b-link-list :items="starters" icons="repo"/>

    <h3>Pinned features</h3>
    <b-link-list :items="features" icons="repo"/>
    <br>
    <b-link :more="true" to="/guide/">Explore more features</b-link>

    <h3>Stay up to date</h3>
    <b-link-list :items="social"/>

    <h3>Get involved</h3>
    <b-link-list :items="contribute"/>
  </aside>
</template>

<script>
export default {
  data() {
    return {
      starters: [
        { title: "Installation", path: "/guide/installation" },
        { title: "Tutorial", path: "/guide/tutorial" },
        { title: "FAQ", path: "/faq" }
      ],
      features: [
        { title: "Routing", path: "/guide/routing" },
        { title: "JSON validation", path: "/guide/json-validation" },
        { title: "WebSockets", path: "/guide/websockets" },
        { title: "Providers", path: "/guide/providers" }
      ],
      social: [
        {
          title: "Follow @bocadillopy",
          path: "https://twitter.com/bocadillopy"
        },
        {
          title: "DEV Community",
          path: "https://dev.to/bocadillo"
        },
        {
          title: "Changelog",
          path:
            "https://github.com/bocadilloproject/bocadillo/path/master/CHANGELOG.md"
        }
      ],
      contribute: [
        {
          title: "Issues",
          path: "https://github.com/bocadilloproject/bocadillo/issues"
        },
        {
          title: "Contributing guide",
          path:
            "https://github.com/bocadilloproject/bocadillo/path/master/CONTRIBUTING.md"
        }
      ]
    };
  }
};
</script>


<style lang="stylus" scoped>
@import './config.styl';

.home-sidebar {
  padding: 1rem 2rem;
  background: $cardBackgroundColor;

  h3:not(.first) {
    margin-top: 2rem;
    padding-top: 1rem;
    border-top: 1px solid #d0d4d8;
  }

  @media (max-width: $MQMobile) {
    margin: 0;
  }
}
</style>
