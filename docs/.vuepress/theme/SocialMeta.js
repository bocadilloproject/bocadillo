export default {
  mounted() {
    const { frontmatter } = this.$page;

    const meta = [];

    meta.push({
      name: "twitter:title",
      content:
        (frontmatter.title ? frontmatter.title : this.$page.title) +
        " | " +
        this.$site.title
    });

    meta.push({
      name: "twitter:description",
      content: frontmatter.description
        ? frontmatter.description
        : this.$site.description
    });

    if (frontmatter.image) {
      meta.push({ name: "twitter:image", content: frontmatter.image });
    }

    const head = document.getElementsByTagName("head")[0];
    meta.forEach(m => {
      const tag = document.createElement("meta");
      tag.name = m.name;
      tag.content = m.content;
      head.appendChild(tag);
    });
  }
};
