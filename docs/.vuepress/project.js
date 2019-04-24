const utils = require("./utils");

const name = "bocadillo";
const org = "bocadilloproject";
const orgLink = `https://github.com/${org}`;
const repo = `${org}/${name}`;
const repoLink = `https://github.com/${repo}`;
const docs = `https://${org}.github.io`;
const twitterUser = "bocadillopy";

function repoPage(path, options = { branch: "master" }) {
  const base = `https://github.com/${repo}/blob/${options.branch}`;
  return utils.maybeRoot(base, path);
}

function docsPage(path) {
  return utils.maybeRoot(docs, path);
}

function projectRepo(name) {
  return `${orgLink}/${name}`;
}

module.exports = {
  title: "Bocadillo",
  description: "A modern Python web framework filled with asynchronous salsa",
  name,
  author: "Florimond Manca",
  org,
  orgLink,
  repo,
  repoLink,
  issues: `${repoLink}/issues/new/choose`,
  contributing: repoPage("CONTRIBUTING.md"),
  docs,
  aiodine: projectRepo("aiodine"),
  gitter: `https://gitter.im/${repo}`,
  twitterUser,
  twitter: `https://twitter.com/${twitterUser}`,
  algoliaIndex: "bocadilloproject",
  repoPage,
  docsPage,
  projectRepo
};
