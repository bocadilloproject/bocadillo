export default ({ Vue, router }) => {
  router.addRoutes([
    { path: "/topics/", redirect: "/guide/" },
    { path: "/guides/", redirect: "/guide/" }
  ]);
};
