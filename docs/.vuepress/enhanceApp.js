import * as project from "./project";

export default ({ Vue, router }) => {
  Vue.prototype.$project = project;
  router.addRoutes([
    // After renaming "Topics" section to "Guides"
    { path: "/topics/", redirect: "/guides/" }
  ]);
};
