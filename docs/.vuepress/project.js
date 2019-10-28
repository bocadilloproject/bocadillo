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
  description:
    "Fast, scalable and real-time capable web APIs for everyone: Bocadillo is a Python asynchronous web framework built with productivity and modularity in mind.",
  name,
  author: "Florimond Manca",
  org,
  orgLink,
  repo,
  repoLink,
  issues: `${repoLink}/issues/new/choose`,
  contributing: repoPage("CONTRIBUTING.md"),
  docs,
  cli: projectRepo("bocadillo-cli"),
  twitterUser,
  twitter: `https://twitter.com/${twitterUser}`,
  repoPage,
  docsPage,
  projectRepo
};
