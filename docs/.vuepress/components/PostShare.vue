<template>
  <div class="icons">
    <a @click.preventDefault="showShareWindow">
      <img id="twitter-logo" src="/twitter-logo.svg">
    </a>
  </div>
</template>

<script>
export default {
  props: ["page"],
  methods: {
    showShareWindow() {
      const width = 640;
      const height = 640;
      let windowConfig = {
        width,
        height,
        left: screen.width / 2 - width / 2,
        top: screen.height / 2 - height / 2,
        toolbar: "no",
        menubar: "no",
        scrollbars: "no"
      };
      const windowConfigStr = Object.entries(windowConfig)
        .map(([name, value]) => `${name}=${value}`)
        .join(",");

      const url = encodeURIComponent(document.location.href);
      let text = `${this.page.frontmatter.title} |`;
      text = `${text} @bocadillopy`;
      text = encodeURIComponent(text);
      const shareUrl = `https://twitter.com/share?url=${url}&text=${text}`;

      return window.open(shareUrl, "Share this", windowConfigStr);
    }
  }
};
</script>

<style lang="stylus" scoped>
.icons {
  position: fixed;
  top: 10em;
  left: calc(((100vw - 740px) / 2) - 120px);
  display: flex;
  flex-flow: column nowrap;
}

a {
  cursor: pointer;
}

#twitter-logo {
  width: 2.5em;
  height: 2.5em;
  filter: sepia(1) hue-rotate(160deg) brightness(0.6) saturate(1.2);

  &:hover {
    filter: none;
  }
}
</style>
