export const getBlogPages = site =>
  site.pages
    .filter(page => page.frontmatter.layout === "Post")
    .sort(
      (a, b) => new Date(b.frontmatter.date) - new Date(a.frontmatter.date)
    );
