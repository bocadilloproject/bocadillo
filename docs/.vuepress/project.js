const utils = require("./utils");

const name = "bocadillo";
const org = "bocadilloproject";
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

module.exports = {
  title: "Bocadillo",
  description: "A modern Python web framework filled with asynchronous salsa",
  name,
  author: "Florimond Manca",
  org,
  orgLink: `https://github.com/${org}`,
  repo,
  repoLink,
  issues: `${repoLink}/issues/new/choose`,
  contributing: repoPage("CONTRIBUTING.md"),
  roadmap: repoPage("ROADMAP.md"),
  docs,
  queso: docsPage("queso"),
  gitter: `https://gitter.im/${repo}`,
  twitterUser,
  twitter: `https://twitter.com/${twitterUser}`,
  algoliaIndex: "bocadilloproject",
  repoPage,
  docsPage
};
