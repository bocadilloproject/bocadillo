export default ({ Vue, router }) => {
  router.addRoutes([
    // After renaming "Topics" section to "Guides"
    { path: "/topics/", redirect: "/guides/" }
  ]);
};
